#!/usr/bin/env python3
"""
Test script to verify prompt API endpoints are working correctly.
Tests the following endpoints:
1. /api/v1/prompts/my-prompts
2. /api/v1/prompts/shared
"""

import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PromptAPITester:
    def __init__(self, base_url: str = "http://localhost:8000", username: str = None, password: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        self.username = username
        self.password = password
        self.access_token = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with the API to get an access token."""
        if not self.username or not self.password:
            logger.error("Username and password are required for authentication")
            return False
        
        auth_url = f"{self.api_base}/auth/login"
        auth_data = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            async with self.session.post(auth_url, data=auth_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.access_token = result.get("access_token")
                    if self.access_token:
                        logger.info("Authentication successful")
                        return True
                    else:
                        logger.error("No access token in response")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"Authentication failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def test_endpoint(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a specific API endpoint."""
        url = f"{self.api_base}{endpoint}"
        headers = self.get_auth_headers()
        
        logger.info(f"Testing {method} {url}")
        
        try:
            async with self.session.request(method, url, headers=headers, json=data) as response:
                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "success": 200 <= response.status < 300
                }
                
                try:
                    result["response_data"] = await response.json()
                except:
                    result["response_text"] = await response.text()
                
                if result["success"]:
                    logger.info(f"✅ {method} {endpoint} - Status: {response.status}")
                    if "response_data" in result and isinstance(result["response_data"], list):
                        logger.info(f"   Returned {len(result['response_data'])} items")
                else:
                    logger.error(f"❌ {method} {endpoint} - Status: {response.status}")
                    if "response_text" in result:
                        logger.error(f"   Response: {result['response_text']}")
                
                return result
                
        except Exception as e:
            logger.error(f"❌ {method} {endpoint} - Error: {e}")
            return {
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "success": False
            }
    
    async def test_prompt_endpoints(self) -> Dict[str, Any]:
        """Test all prompt-related endpoints."""
        results = {}
        
        # Test my-prompts endpoint
        results["my_prompts"] = await self.test_endpoint("/prompts/my-prompts")
        
        # Test my-prompts with query parameters
        results["my_prompts_filtered"] = await self.test_endpoint(
            "/prompts/my-prompts?skip=0&limit=10&filter_is_active=true"
        )
        
        # Test shared prompts endpoint
        results["shared_prompts"] = await self.test_endpoint("/prompts/shared")
        
        # Test shared prompts with query parameters
        results["shared_prompts_filtered"] = await self.test_endpoint(
            "/prompts/shared?skip=0&limit=10&filter_is_active=true"
        )
        
        # Test prompts list (root endpoint)
        results["prompts_root"] = await self.test_endpoint("/prompts/")
        
        return results
    
    async def check_server_availability(self) -> bool:
        """Check if the server is running and accessible."""
        try:
            async with self.session.get(f"{self.base_url}/docs") as response:
                if response.status == 200:
                    logger.info("✅ Server is accessible")
                    return True
                else:
                    logger.warning(f"Server responded with status: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Server is not accessible: {e}")
            return False
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of test results."""
        logger.info("\n" + "="*60)
        logger.info("PROMPT API ENDPOINTS TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(results)
        successful_tests = sum(1 for result in results.values() if result.get("success", False))
        
        logger.info(f"Total endpoints tested: {total_tests}")
        logger.info(f"Successful tests: {successful_tests}")
        logger.info(f"Failed tests: {total_tests - successful_tests}")
        
        logger.info("\nDetailed results:")
        for endpoint_name, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            status_code = result.get("status_code", "N/A")
            endpoint = result.get("endpoint", "Unknown")
            
            logger.info(f"  {status} - {endpoint_name}: {endpoint} (Status: {status_code})")
            
            if "error" in result:
                logger.info(f"    Error: {result['error']}")
            elif not result.get("success", False) and "response_text" in result:
                response_preview = result["response_text"][:100] + "..." if len(result.get("response_text", "")) > 100 else result.get("response_text", "")
                logger.info(f"    Response: {response_preview}")

async def main():
    """Main test function."""
    # Get server URL from environment or use default
    base_url = os.getenv("SERVER_URL", "http://localhost:8000")
    
    # Get credentials from environment variables or use defaults for testing
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")
    
    if not username or not password:
        logger.warning("No TEST_USERNAME or TEST_PASSWORD environment variables found.")
        logger.info("You can set these with:")
        logger.info("  export TEST_USERNAME=your_username")
        logger.info("  export TEST_PASSWORD=your_password")
        logger.info("Proceeding without authentication (may fail for protected endpoints)...")
    
    async with PromptAPITester(base_url, username, password) as tester:
        # Check server availability
        if not await tester.check_server_availability():
            logger.error("Cannot proceed - server is not accessible")
            return 1
        
        # Authenticate if credentials are provided
        if username and password:
            if not await tester.authenticate():
                logger.error("Cannot proceed - authentication failed")
                return 1
        else:
            logger.warning("Proceeding without authentication - protected endpoints may fail")
        
        # Test prompt endpoints
        results = await tester.test_prompt_endpoints()
        
        # Print summary
        tester.print_summary(results)
        
        # Return appropriate exit code
        failed_tests = sum(1 for result in results.values() if not result.get("success", False))
        return 1 if failed_tests > 0 else 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        sys.exit(1)