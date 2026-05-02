#!/usr/bin/env python3
"""
Test script for token estimation functionality for streaming calls.
This script validates that the new token estimation functions work correctly.
"""

import asyncio
import sys
import os
import logging

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.cost_tracker_service import (
    estimate_tokens_for_streaming_call,
    build_full_prompt_from_kernel_args,
    _get_tokenizer_for_model
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockKernelArguments:
    """Mock KernelArguments class for testing"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def test_tokenizer_loading():
    """Test that we can load tokenizers for different models"""
    logger.info("Testing tokenizer loading...")
    
    # Test models that should work
    test_models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4o",
        "unknown-model-name"  # Should fallback to cl100k_base
    ]
    
    for model in test_models:
        try:
            tokenizer = _get_tokenizer_for_model(model)
            test_text = "Hello, world! This is a test."
            tokens = tokenizer.encode(test_text)
            logger.info(f"✓ Model '{model}': {len(tokens)} tokens for test text")
        except Exception as e:
            logger.error(f"✗ Model '{model}': Failed to load tokenizer - {e}")

def test_token_estimation():
    """Test token estimation for streaming calls"""
    logger.info("Testing token estimation...")
    
    input_text = """
    You are a creative writing assistant. Generate a dramatic scene about a dragon's final battle.
    
    Context:
    - Story: Epic Fantasy Adventure
    - Character: Ancient Red Dragon Pyraxis
    - Location: Volcanic Mountain Peak
    - User Request: Write the dragon's last stand against the heroes
    """
    
    output_text = """
    The ancient red dragon Pyraxis spread his massive wings against the crimson sky, scales gleaming like molten metal in the volcanic glow. His golden eyes, filled with millennia of wisdom and rage, surveyed the approaching heroes. This would be his final battle, and he would make it legendary.
    
    "So, mortals," his voice rumbled like distant thunder, "you have come to claim my life. Know that I have witnessed the rise and fall of kingdoms, the birth of stars, and the tears of gods. Your victory will be paid for in blood and sacrifice."
    """
    
    # Test with different model names
    test_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
    
    for model in test_models:
        try:
            usage = estimate_tokens_for_streaming_call(input_text, output_text, model)
            logger.info(f"✓ Model '{model}' token estimation:")
            logger.info(f"  - Input tokens: {usage['prompt_tokens']}")
            logger.info(f"  - Output tokens: {usage['completion_tokens']}")
            logger.info(f"  - Total tokens: {usage['total_tokens']}")
        except Exception as e:
            logger.error(f"✗ Model '{model}': Token estimation failed - {e}")

def test_kernel_args_prompt_building():
    """Test building full prompts from KernelArguments"""
    logger.info("Testing KernelArguments prompt building...")
    
    # Create mock kernel arguments similar to what's used in the routers
    mock_args = MockKernelArguments(
        user_instruction="Write an epic battle scene",
        story_title="The Dragon's Last Stand",
        story_description="An epic fantasy about heroes facing an ancient dragon",
        character_context="Pyraxis: Ancient red dragon, guardian of the volcanic peaks",
        location_context="Volcanic Mountain Peak: Sacred ground where dragons make their final stand",
        generation_mode="Continue/Append",
        selected_text="The dragon roared...",
        settings=None  # This should be ignored
    )
    
    try:
        full_prompt = build_full_prompt_from_kernel_args(mock_args)
        logger.info(f"✓ Built prompt from KernelArguments ({len(full_prompt)} characters):")
        logger.info(f"Prompt preview: {full_prompt[:200]}...")
        
        # Test tokenization of the built prompt
        usage = estimate_tokens_for_streaming_call(full_prompt, "Dragon battle response", "gpt-3.5-turbo")
        logger.info(f"✓ Estimated tokens for built prompt: {usage['prompt_tokens']} input, {usage['completion_tokens']} output")
        
    except Exception as e:
        logger.error(f"✗ Failed to build prompt from KernelArguments - {e}")

def main():
    """Run all tests"""
    logger.info("Starting token estimation tests...")
    
    try:
        test_tokenizer_loading()
        print("\n" + "="*50 + "\n")
        
        test_token_estimation()
        print("\n" + "="*50 + "\n")
        
        test_kernel_args_prompt_building()
        print("\n" + "="*50 + "\n")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)