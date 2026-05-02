#!/usr/bin/env python3
"""
Script to check for missing ApiResponse imports in router files.
"""

import os
import re

def check_file_for_import_and_usage(file_path):
    """Check if file uses ApiResponse but is missing the import."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file uses ApiResponse in decorators
        uses_apiresponse = bool(re.search(r'response_model=ApiResponse', content))
        
        # Check if file has the import
        has_import = bool(re.search(r'from app\.schemas\.base import.*ApiResponse', content))
        
        # Find all line numbers where ApiResponse is used
        usage_lines = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'response_model=ApiResponse' in line:
                usage_lines.append(i)
        
        return {
            'uses_apiresponse': uses_apiresponse,
            'has_import': has_import,
            'usage_lines': usage_lines,
            'file_path': file_path
        }
    except Exception as e:
        return {
            'error': str(e),
            'file_path': file_path
        }

def main():
    router_files = [
        'app/routers/act.py',
        'app/routers/act_ai_review.py',
        'app/routers/admin_billing.py',
        'app/routers/admin_help_editor.py',
        'app/routers/ai_model_config.py',
        'app/routers/ai_text_transform.py',
        'app/routers/associations.py',
        'app/routers/auth.py',
        'app/routers/basic_stories.py',
        'app/routers/batch.py',
        'app/routers/billing.py',
        'app/routers/blog.py',
        'app/routers/blog_author_profile.py',
        'app/routers/blog_categories.py',
        'app/routers/blog_comments.py',
        'app/routers/blog_engagement.py',
        'app/routers/blog_media.py',
        'app/routers/blog_search.py',
        'app/routers/blog_subscriptions.py',
        'app/routers/blog_tags.py',
        'app/routers/brainstorm.py',
        'app/routers/character.py',
        'app/routers/dashboard.py',
        'app/routers/document_upload.py',
        'app/routers/forum_category.py',
        'app/routers/forum_post.py',
        'app/routers/forum_thread.py',
        'app/routers/image_generation.py',
        'app/routers/interview.py',
        'app/routers/llm_models.py',
        'app/routers/location.py',
        'app/routers/location_connection.py',
        'app/routers/lore_item.py',
        'app/routers/prompt.py',
        'app/routers/public_world_chat.py',
        'app/routers/published_stories.py',
        'app/routers/referrals.py',
        'app/routers/scene.py',
        'app/routers/social_sharing.py',
        'app/routers/story.py',
        'app/routers/story_chat.py',
        'app/routers/story_class.py',
        'app/routers/users.py',
        'app/routers/welcome_interview.py',
        'app/routers/world.py',
        'app/routers/world_builder.py',
        'app/routers/world_chat.py',
        'app/routers/world_importer.py'
    ]
    
    missing_imports = []
    
    print("Checking router files for ApiResponse usage and imports...\n")
    
    for file_path in router_files:
        if os.path.exists(file_path):
            result = check_file_for_import_and_usage(file_path)
            
            if 'error' in result:
                print(f"ERROR: {file_path} - {result['error']}")
                continue
                
            if result['uses_apiresponse'] and not result['has_import']:
                missing_imports.append(result)
                print(f"MISSING IMPORT: {file_path}")
                print(f"  - Uses ApiResponse on lines: {', '.join(map(str, result['usage_lines']))}")
                print(f"  - Missing import: from app.schemas.base import ApiResponse")
                print()
            elif result['uses_apiresponse'] and result['has_import']:
                print(f"OK: {file_path} - Has import and uses ApiResponse")
            elif not result['uses_apiresponse']:
                print(f"N/A: {file_path} - Does not use ApiResponse")
        else:
            print(f"NOT FOUND: {file_path}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total files checked: {len(router_files)}")
    print(f"Files missing imports: {len(missing_imports)}")
    
    if missing_imports:
        print("\nFiles that need the import added:")
        for result in missing_imports:
            print(f"  - {result['file_path']} (lines: {', '.join(map(str, result['usage_lines']))})")

if __name__ == "__main__":
    main()