#!/usr/bin/env python3
"""
Story Wizard Validation Script
Test the Semantic Kernel connection and Story Wizard functionality
"""

async def validate_story_wizard_connection():
    """Validate Story Wizard AI connection and Semantic Kernel setup"""
    
    print("🧙‍♂️ Story Wizard Connection Validation")
    print("=" * 50)
    
    try:
        # Test 1: Import Semantic Kernel
        print("1. Testing Semantic Kernel import...")
        from app.services.semantic_kernel_setup import kernel
        print("   ✅ Semantic Kernel imported successfully")
        
        # Test 2: Check kernel services
        print("\n2. Checking kernel services...")
        if hasattr(kernel, 'services') and kernel.services:
            print(f"   ✅ Found {len(kernel.services)} service(s):")
            for service_id in kernel.services:
                service = kernel.services[service_id]
                print(f"      - {service_id}: {type(service).__name__}")
        else:
            print("   ❌ No services found in kernel")
            return False
            
        # Test 3: Check if Azure OpenAI chat service is available
        print("\n3. Testing Azure OpenAI chat service...")
        chat_service = kernel.services.get("azure_openai_chat_service")
        if chat_service:
            print("   ✅ Azure OpenAI chat service found")
        else:
            print("   ❌ Azure OpenAI chat service not found")
            return False
            
        # Test 4: Test Story Wizard function registration
        print("\n4. Testing Story Wizard function registration...")
        from app.routers.story_wizard_api import _ensure_story_wizard_functions
        await _ensure_story_wizard_functions()
        
        if kernel.plugins.get("StoryWizard"):
            wizard_plugin = kernel.plugins["StoryWizard"]
            print("   ✅ Story Wizard plugin registered")
            
            # Check functions
            functions = wizard_plugin._functions if hasattr(wizard_plugin, '_functions') else {}
            print(f"   ✅ Functions available: {list(functions.keys())}")
        else:
            print("   ❌ Story Wizard plugin not found")
            return False
            
        # Test 5: Test simple prompt execution
        print("\n5. Testing simple prompt execution...")
        from semantic_kernel.functions.kernel_arguments import KernelArguments
        
        test_args = KernelArguments(
            phase_name="Core Spark & Protagonist",
            step=1,
            total_steps=2,
            story_context="No story data collected yet.",
            user_message="I want to write a fantasy adventure story.",
            conversation_history=""
        )
        
        try:
            result = await kernel.invoke(
                plugin_name="StoryWizard",
                function_name="ChatResponse", 
                arguments=test_args
            )
            response = str(result)
            print(f"   ✅ Test response generated: {response[:100]}...")
        except Exception as e:
            print(f"   ❌ Prompt execution failed: {e}")
            return False
            
        print("\n🎉 All Story Wizard validations passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(validate_story_wizard_connection())