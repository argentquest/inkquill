#!/usr/bin/env python3
"""
Static analysis of prompt API endpoints to verify their existence and configuration.
This script analyzes the code without running the server.
"""

import re
import os
from pathlib import Path

def analyze_router_file(file_path: str):
    """Analyze a router file to extract endpoint information."""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract router configuration
    router_config = {}
    
    # Find router prefix
    prefix_match = re.search(r'router\s*=\s*APIRouter\s*\([^)]*prefix\s*=\s*["\']([^"\']*)["\']', content)
    if prefix_match:
        router_config['prefix'] = prefix_match.group(1)
    
    # Find dependencies
    deps_match = re.search(r'dependencies\s*=\s*\[([^\]]*)\]', content)
    if deps_match:
        router_config['dependencies'] = deps_match.group(1).strip()
    
    # Find all endpoints
    endpoints = []
    endpoint_patterns = [
        r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']*)["\'][^)]*name\s*=\s*["\']([^"\']*)["\']',
        r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']*)["\']'
    ]
    
    for pattern in endpoint_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            name = match.group(3) if len(match.groups()) >= 3 else None
            
            # Find the function name by looking for async def after the decorator
            func_match = re.search(rf'@router\.{method.lower()}\([^)]*\)\s*async\s+def\s+(\w+)', content, re.IGNORECASE)
            if func_match:
                func_name = func_match.group(1)
            else:
                func_name = "unknown"
            
            endpoints.append({
                'method': method,
                'path': path,
                'name': name,
                'function': func_name
            })
    
    return {
        'router_config': router_config,
        'endpoints': endpoints,
        'file_path': file_path
    }

def analyze_main_app(file_path: str):
    """Analyze main.py to find API prefix and router inclusion."""
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find API_V1_STR usage
    api_prefix = None
    api_prefix_match = re.search(r'api_v1_prefix\s*=\s*settings\.API_V1_STR', content)
    if api_prefix_match:
        # Look for the actual value in config
        config_match = re.search(r'API_V1_STR:\s*str\s*=\s*["\']([^"\']*)["\']', content)
        if not config_match:
            api_prefix = "/api/v1"  # Default from config.py
        else:
            api_prefix = config_match.group(1)
    
    # Find router inclusions
    router_inclusions = []
    include_patterns = [
        r'app\.include_router\s*\(\s*([^,\s]+)[^)]*prefix\s*=\s*([^,)]+)',
        r'app\.include_router\s*\(\s*([^,\s)]+)'
    ]
    
    for pattern in include_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            router_name = match.group(1)
            prefix = match.group(2) if len(match.groups()) >= 2 else "No explicit prefix"
            router_inclusions.append({
                'router': router_name,
                'prefix': prefix
            })
    
    return {
        'api_prefix': api_prefix,
        'router_inclusions': router_inclusions
    }

def main():
    """Main analysis function."""
    print("="*80)
    print("PROMPT API ENDPOINTS ANALYSIS")
    print("="*80)
    
    # Analyze prompt router
    prompt_router_path = "app/routers/prompt.py"
    print(f"\n1. Analyzing {prompt_router_path}")
    print("-" * 50)
    
    prompt_analysis = analyze_router_file(prompt_router_path)
    if 'error' in prompt_analysis:
        print(f"❌ Error: {prompt_analysis['error']}")
    else:
        config = prompt_analysis['router_config']
        print(f"Router prefix: {config.get('prefix', 'Not specified')}")
        print(f"Dependencies: {config.get('dependencies', 'None')}")
        
        print(f"\nEndpoints found ({len(prompt_analysis['endpoints'])}):")
        for endpoint in prompt_analysis['endpoints']:
            print(f"  {endpoint['method']:6} {endpoint['path']:20} -> {endpoint['function']} (name: {endpoint.get('name', 'N/A')})")
    
    # Analyze views_prompt router
    views_prompt_path = "app/routers/views_prompt.py"
    print(f"\n2. Analyzing {views_prompt_path}")
    print("-" * 50)
    
    views_analysis = analyze_router_file(views_prompt_path)
    if 'error' in views_analysis:
        print(f"❌ Error: {views_analysis['error']}")
    else:
        config = views_analysis['router_config']
        print(f"Router prefix: {config.get('prefix', 'Not specified')}")
        print(f"Dependencies: {config.get('dependencies', 'None')}")
        
        print(f"\nEndpoints found ({len(views_analysis['endpoints'])}):")
        for endpoint in views_analysis['endpoints']:
            print(f"  {endpoint['method']:6} {endpoint['path']:20} -> {endpoint['function']} (name: {endpoint.get('name', 'N/A')})")
    
    # Analyze main app configuration
    main_app_path = "app/main.py"
    print(f"\n3. Analyzing {main_app_path}")
    print("-" * 50)
    
    main_analysis = analyze_main_app(main_app_path)
    if 'error' in main_analysis:
        print(f"❌ Error: {main_analysis['error']}")
    else:
        print(f"API prefix: {main_analysis.get('api_prefix', 'Not found')}")
        print(f"\nRouter inclusions found ({len(main_analysis['router_inclusions'])}):")
        for inclusion in main_analysis['router_inclusions']:
            print(f"  {inclusion['router']} with prefix: {inclusion['prefix']}")
    
    # Summary of target endpoints
    print(f"\n4. TARGET ENDPOINTS VERIFICATION")
    print("-" * 50)
    
    if 'error' not in prompt_analysis:
        api_prefix = "/api/v1"  # From config.py
        router_prefix = prompt_analysis['router_config'].get('prefix', '')
        
        target_endpoints = [
            "/my-prompts",
            "/shared"
        ]
        
        print("Expected full URLs:")
        for endpoint_path in target_endpoints:
            full_url = f"{api_prefix}{router_prefix}{endpoint_path}"
            print(f"  {full_url}")
        
        print("\nEndpoint verification:")
        found_endpoints = [ep['path'] for ep in prompt_analysis['endpoints']]
        
        for target in target_endpoints:
            if target in found_endpoints:
                print(f"  ✅ {target} - FOUND")
            else:
                print(f"  ❌ {target} - NOT FOUND")
                print(f"     Available paths: {found_endpoints}")
    
    # Authentication requirements
    print(f"\n5. AUTHENTICATION REQUIREMENTS")
    print("-" * 50)
    
    if 'error' not in prompt_analysis:
        deps = prompt_analysis['router_config'].get('dependencies', '')
        if 'get_current_active_user' in deps:
            print("✅ Authentication required: get_current_active_user dependency found")
            print("   All endpoints in this router require authentication")
        else:
            print("❓ Authentication status unclear")
            print(f"   Dependencies: {deps}")
    
    print(f"\n6. CRUD OPERATIONS ANALYSIS")
    print("-" * 50)
    
    # Check if CRUD file exists
    crud_path = "app/crud/prompt.py"
    if os.path.exists(crud_path):
        print(f"✅ CRUD file exists: {crud_path}")
        with open(crud_path, 'r') as f:
            crud_content = f.read()
        
        crud_functions = re.findall(r'async\s+def\s+(\w+)', crud_content)
        print(f"CRUD functions found: {', '.join(crud_functions)}")
        
        # Check for specific functions used by our target endpoints
        required_functions = ['get_prompts_by_user', 'get_shared_prompts']
        for func in required_functions:
            if func in crud_functions:
                print(f"  ✅ {func} - FOUND")
            else:
                print(f"  ❌ {func} - NOT FOUND")
    else:
        print(f"❌ CRUD file not found: {crud_path}")

if __name__ == "__main__":
    main()