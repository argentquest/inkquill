#!/usr/bin/env python
"""Test script to verify the world builder service fix"""

import asyncio
import logging
from app.services.world_builder_service import WorldBuilderService
from app.services.sk_kernel_instance import kernel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_world_builder_fix():
    """Test that the world builder service works with the fixed service ID"""
    
    print("=== Testing World Builder Service Fix ===\n")
    
    # Test 1: Service instantiation
    try:
        service = WorldBuilderService()
        print("✓ WorldBuilderService instantiated successfully")
    except Exception as e:
        print(f"✗ Failed to instantiate WorldBuilderService: {e}")
        return
    
    # Test 2: Load questions
    try:
        questions = service.get_all_questions()
        print(f"✓ Loaded {len(questions)} questions")
    except Exception as e:
        print(f"✗ Failed to load questions: {e}")
    
    # Test 3: Check kernel services
    try:
        if kernel:
            services = kernel.services
            service_ids = list(services.keys()) if services else []
            print(f"✓ Kernel initialized with services: {service_ids}")
            
            # Check if our expected service ID exists
            expected_service_id = "azure_openai_chat_service"
            if expected_service_id in service_ids:
                print(f"✓ Expected service ID '{expected_service_id}' found in kernel")
            else:
                print(f"✗ Expected service ID '{expected_service_id}' NOT found in kernel")
                print(f"  Available service IDs: {service_ids}")
        else:
            print("✗ Kernel is None")
    except Exception as e:
        print(f"✗ Error checking kernel services: {e}")
    
    # Test 4: Test imports
    try:
        from semantic_kernel.functions.kernel_arguments import KernelArguments
        from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
        from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
        print("✓ All required imports are available")
    except ImportError as e:
        print(f"✗ Import error: {e}")
    
    # Test 5: Check if we can access the correct chat service ID from settings
    try:
        from app.core.config import settings
        print(f"✓ Settings loaded successfully")
        if hasattr(settings, 'AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT'):
            print(f"  - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT: {settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT}")
        else:
            print("  - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT not found in settings")
    except Exception as e:
        print(f"✗ Error loading settings: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_world_builder_fix())