# /ai_rag_story_app/app/mainTestEmbedding.py

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# --- Load Environment Variables ---
# This ensures the script uses the same settings as your main app
print("Loading environment variables from .env file...")
load_dotenv()

# --- Configuration from Environment ---
# Reads the specific settings for your new 1536d setup
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# --- Validation and Client Initialization ---
print("\n--- Verifying Configuration ---")
print(f"Endpoint: {endpoint}")
print(f"API Key: {'********' if api_key else 'NOT SET'}")
print(f"API Version: {api_version}")
print(f"Embedding Deployment Name: {deployment}")

if not all([endpoint, api_key, deployment, api_version]):
    print("\nERROR: One or more required Azure OpenAI settings are missing.")
    print("Please check your .env file for AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME, and AZURE_OPENAI_API_VERSION.")
    exit()

try:
    client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=endpoint,
        api_key=api_key,
    )
    print("\nSUCCESS: AzureOpenAI client initialized successfully.")
except Exception as e:
    print(f"\nERROR: Failed to initialize AzureOpenAI client: {e}")
    exit()


# --- Test Embedding Generation ---
print("\n--- Generating Embeddings ---")
try:
    response = client.embeddings.create(
        input=["This is a test of the text-embedding-ada-002 model.", "It should produce 1536-dimension vectors."],
        model=deployment 
    )
    print("SUCCESS: API call to embedding model completed.")
    print("\n--- Results ---")

    # Validate the response
    if response.data and len(response.data) > 0:
        for item in response.data:
            vector_length = len(item.embedding)
            print(f"Vector for data[{item.index}]:")
            print(f"  - Length: {vector_length}")
            
            # This is the critical check
            if vector_length == 1536:
                print(f"  - \033[92mSUCCESS: Vector dimension is correct (1536).\033[0m")
            else:
                print(f"  - \033[91mFAILURE: Vector dimension is INCORRECT. Expected 1536, got {vector_length}.\033[0m")
            
            print(f"  - Preview: [{item.embedding[0]}, {item.embedding[1]}, ..., {item.embedding[-2]}, {item.embedding[-1]}]")
    else:
        print("\033[91mFAILURE: The API response did not contain any embedding data.\033[0m")

    if response.usage:
        print(f"\nUsage Info: {response.usage}")
    else:
        print("\nUsage info not available in response.")

except Exception as e:
    print(f"\n\033[91m--- An error occurred during the API call ---")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}\033[0m")