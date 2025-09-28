# /ai_rag_story_app/app/processing/chunking.py

import tiktoken # OpenAI's tokenizer library
from typing import List
from app.core.config import settings

# --- Background: Text Chunking ---
# This module provides functions for splitting large pieces of text (extracted
# from documents) into smaller, more manageable chunks. This is a crucial step
# in preparing data for RAG systems because:
# 1.  Embedding Models Have Input Limits: Most text embedding models can only handle
#     a certain amount of text at once (e.g., often around 8191 tokens for OpenAI's ada-002).
# 2.  LLM Context Windows: The final LLM that generates the answer also has a limited
#     context window. Providing overly large, irrelevant chunks can dilute the useful
#     information and exceed these limits.
# 3.  Retrieval Precision: Smaller chunks can sometimes lead to more precise retrieval,
#     as the embedding for a smaller chunk is more likely to closely match a specific query.
#
# We are implementing a "fixed-size chunking with overlap" strategy using token counts,
# as it provides a good balance between simplicity and effectiveness. The overlap helps
# maintain context across chunk boundaries.

# --- Tokenizer Initialization ---
# It's generally efficient to load the tokenizer once if the function is called repeatedly.
# We choose the tokenizer based on the models we're likely using (embeddings or LLM).
# "cl100k_base" is common for newer OpenAI models like ada-002, gpt-3.5-turbo, gpt-4.
_tokenizer = None
try:
    # Attempt to load the recommended tokenizer for modern OpenAI models.
    _tokenizer = tiktoken.get_encoding(settings.DEFAULT_TOKENIZER)
    print(f"Tiktoken '{settings.DEFAULT_TOKENIZER}' tokenizer loaded successfully for chunking.")
except Exception as e_token:
    # Log a warning if the primary tokenizer fails to load.
    # The get_tokenizer function will attempt a fallback.
    print(f"Warning: Failed to load '{settings.DEFAULT_TOKENIZER}' tokenizer: {e_token}. Falling back based on model name if needed.")

def get_tokenizer(model_name: str = None) -> tiktoken.Encoding:
    """
    Gets the appropriate tiktoken tokenizer, loading lazily if needed.
    Uses a cached global instance if already loaded, otherwise tries to load it.

    Args:
        model_name: The model name used as a fallback to determine encoding. If None, uses default from config.

    Returns:
        A tiktoken.Encoding instance.

    Raises:
        ValueError: If no suitable tokenizer can be loaded.
    """
    if model_name is None:
        model_name = settings.DEFAULT_MODEL_FOR_CHUNKING
        
    global _tokenizer
    if _tokenizer:
        # Return the globally cached tokenizer if available.
        return _tokenizer
    else:
        # If initial load failed, try model-specific loading as a fallback.
        try:
            print(f"Attempting to load tokenizer for model '{model_name}'...")
            _tokenizer = tiktoken.encoding_for_model(model_name)
            print(f"Tiktoken tokenizer loaded for model '{model_name}'.")
            return _tokenizer
        except Exception as e:
            # If fallback also fails, log an error and raise an exception.
            print(f"ERROR: Could not load tokenizer for model '{model_name}'. Chunking may fail. Error: {e}")
            raise ValueError(f"Failed to load tokenizer for model {model_name}") from e


# --- Chunking Function ---

def chunk_text_fixed_size_with_overlap(
    full_text: str,
    chunk_size: int,    # Target chunk size in tokens
    chunk_overlap: int, # Number of tokens to overlap between chunks
    model_name: str = None # Used to select the correct tokenizer if needed
) -> List[str]:
    """
    Splits a large text into smaller chunks of a target token size with overlap,
    using tokenization for accurate sizing.

    Args:
        full_text: The entire text content extracted from a document.
        chunk_size: The desired maximum number of tokens per chunk.
        chunk_overlap: The number of tokens that consecutive chunks should overlap.
                       Must be less than chunk_size.
        model_name: The name of the OpenAI model (used to ensure the correct tokenizer
                    is employed for accurate token counting).

    Returns:
        A list of strings, where each string is a text chunk. Returns an empty list
        if the input text is empty or if chunking parameters are invalid.
    """
    # Basic input validation
    if not full_text or full_text.isspace():
        print("Warning: Input text for chunking is empty.")
        return []

    if chunk_overlap < 0:
         raise ValueError("Chunk overlap cannot be negative.")
    if chunk_size <= 0:
         raise ValueError("Chunk size must be positive.")
    if chunk_overlap >= chunk_size:
        # Overlap must be smaller than chunk size to make progress when iterating.
        raise ValueError(f"Chunk overlap ({chunk_overlap}) must be less than chunk size ({chunk_size}).")

    try:
        # Get the appropriate tokenizer instance.
        tokenizer = get_tokenizer(model_name)
    except ValueError as e:
        # If tokenizer fails to load, cannot proceed with token-based chunking.
        print(f"ERROR: Cannot perform chunking due to tokenizer error: {e}")
        return [] # Return empty list or re-raise depending on desired behavior

    # Encode the entire text into a list of token integers.
    tokens = tokenizer.encode(full_text)
    num_tokens = len(tokens)

    print(f"[Chunking] Input text token count: {num_tokens}")

    chunks_text: List[str] = [] # List to store the resulting text chunks
    start_index = 0 # Starting token index for the current chunk

    # Iterate through the tokens to create overlapping chunks.
    while start_index < num_tokens:
        # Calculate the end index for the current chunk.
        # It's the minimum of (start + chunk_size) or the total number of tokens.
        end_index = min(start_index + chunk_size, num_tokens)

        # Extract the tokens for this chunk slice.
        chunk_tokens = tokens[start_index:end_index]

        # Decode the token integers back into a human-readable text string.
        # Handle potential decoding errors, though usually rare with encode/decode pairs from same tokenizer.
        try:
            chunk_text = tokenizer.decode(chunk_tokens)
            # Add the decoded text chunk to our list.
            chunks_text.append(chunk_text)
        except Exception as e_decode:
            # Log a warning if decoding fails for a specific chunk.
            print(f"Warning: Failed to decode token chunk starting at index {start_index}. Error: {e_decode}")
            # Decide whether to skip this chunk or stop processing entirely. Skipping for now.

        # Check if we've processed the last possible chunk.
        if end_index == num_tokens:
            break # Exit the loop if we've reached the end of the tokens.

        # Calculate the starting index for the *next* chunk.
        # We move forward by (chunk_size - chunk_overlap) tokens to create the overlap.
        next_start_index = start_index + (chunk_size - chunk_overlap)

        # Sanity check: ensure we are making progress to avoid infinite loops.
        # This should only happen if chunk_overlap >= chunk_size, which is checked earlier.
        if next_start_index <= start_index:
             print(f"CRITICAL WARNING: Chunking parameters resulted in no progress (start_index={start_index}, next_start_index={next_start_index}). Check chunk_size and chunk_overlap. Stopping chunking.")
             break # Avoid potential infinite loop

        # Update the start index for the next iteration.
        start_index = next_start_index

    print(f"[Chunking] Generated {len(chunks_text)} chunks.")
    return chunks_text


def count_tokens(text: str, model_name: str = None) -> int:
    """
    Count the number of tokens in a given text string using the appropriate tokenizer.
    
    Args:
        text: The text to count tokens for
        model_name: The model name to select the appropriate tokenizer
        
    Returns:
        The number of tokens in the text
        
    Raises:
        ValueError: If tokenizer cannot be loaded
    """
    if not text:
        return 0
        
    try:
        tokenizer = get_tokenizer(model_name)
        tokens = tokenizer.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens: {e}")
        # Fallback to rough estimation (4 chars per token average)
        return len(text) // 4

# --- Example Usage (for testing this module directly) ---
# This block runs only when the script is executed directly (e.g., `python app/processing/chunking.py`).
if __name__ == '__main__':
    # A sample text containing multiple sentences and paragraphs.
    sample_text = """This is the first sentence. This is the second sentence which is a bit longer.
This marks the beginning of a new paragraph. It contains several moderately sized sentences to test the chunking mechanism. We want to see how it splits across paragraphs and sentences, especially with overlap.
Another paragraph starts here. Let's add more content to ensure multiple chunks are generated. The overlap should help maintain context if a split happens mid-thought. Final sentence."""

    # Define small chunking parameters for easy demonstration.
    chunk_s = 25 # Target token size per chunk
    chunk_o = 5  # Token overlap between chunks

    print(f"\n--- Chunking Sample Text ---")
    print(f"Chunk Size: {chunk_s} tokens, Overlap: {chunk_o} tokens")

    # Call the chunking function.
    generated_chunks = chunk_text_fixed_size_with_overlap(sample_text, chunk_s, chunk_o)

    # Print each generated chunk along with its approximate token count.
    for i, chunk in enumerate(generated_chunks):
        print(f"\n--- Chunk {i+1} ---")
        # Optionally, show token count for verification using the same tokenizer.
        try:
             tokenizer_instance = get_tokenizer()
             tok = tokenizer_instance.encode(chunk)
             print(f"(Tokens: {len(tok)})")
        except Exception as e:
             print(f"(Could not get token count: {e})")
        print(chunk)

    print("\n--- Testing Edge Cases ---")
    print("Empty Text:", chunk_text_fixed_size_with_overlap("", 10, 2))
    print("Short Text:", chunk_text_fixed_size_with_overlap("Short text.", 20, 5))
    try:
        print("Invalid Overlap:", chunk_text_fixed_size_with_overlap("Some text", 10, 10))
    except ValueError as e:
        print(f"Caught expected error for invalid overlap: {e}")