#!/usr/bin/env python3
"""
Simple test script to debug story generation without running the full server.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services import sk_kernel_instance

async def test_story_generation():
    """Test the story generation function directly."""
    print("Testing story generation function...")
    
    # Check if kernel is available
    kernel = sk_kernel_instance.kernel
    if not kernel:
        print("❌ Kernel not available")
        return
    
    print("✅ Kernel is available")
    
    # Check if function is available
    generate_function = sk_kernel_instance.generate_story_structure_function
    if not generate_function:
        print("❌ GenerateStoryStructure function not available")
        
        # Debug: Check what plugins and functions are available
        print(f"Available plugins: {list(kernel.plugins.keys())}")
        
        from app.services.sk_constants import STORY_STRUCTURE_PLUGIN_NAME
        if STORY_STRUCTURE_PLUGIN_NAME in kernel.plugins:
            plugin = kernel.plugins[STORY_STRUCTURE_PLUGIN_NAME]
            functions_metadata = plugin.get_functions_metadata()
            function_names = [func.name for func in functions_metadata]
            print(f"Functions in {STORY_STRUCTURE_PLUGIN_NAME}: {function_names}")
        
        return
    
    print("✅ GenerateStoryStructure function is available")
    
    # Test with minimal data
    test_data = {
        "characters": "- **Test Hero**: A brave adventurer seeking glory",
        "locations": "- **Mystic Forest**: A dark and mysterious woodland",
        "lore_items": "- **Ancient Sword**: A legendary weapon of power",
        "author_concept": "A simple adventure story",
        "story_genre": "Fantasy Adventure",
        "story_tone": "Heroic",
        "primary_conflict_type": "Character vs. Nature"
    }
    
    print("\n🚀 Testing AI function invocation...")
    print(f"Input data: {test_data}")
    
    try:
        result = await generate_function.invoke(
            kernel,
            **test_data
        )
        
        print(f"✅ Function invocation completed")
        print(f"Result type: {type(result)}")
        
        if hasattr(result, 'value'):
            print(f"Result.value type: {type(result.value)}")
            print(f"Result.value preview: {str(result.value)[:300]}...")
            
            # Try to extract content
            response_text = None
            if isinstance(result.value, list) and len(result.value) > 0:
                first_item = result.value[0]
                if hasattr(first_item, 'content'):
                    response_text = str(first_item.content).strip()
                elif hasattr(first_item, 'inner_content'):
                    try:
                        content = first_item.inner_content.choices[0].message.content
                        response_text = str(content).strip()
                    except (AttributeError, IndexError):
                        pass
            
            if not response_text:
                response_text = str(result.value).strip()
            
            print(f"Extracted response: {response_text[:500]}...")
            
            if response_text and response_text != "None":
                print("✅ Got response from AI!")
            else:
                print("❌ No response from AI")
        else:
            print("❌ Result has no 'value' attribute")
            
    except Exception as e:
        print(f"❌ Error during function invocation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_story_generation())