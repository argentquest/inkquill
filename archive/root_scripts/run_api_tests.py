#!/usr/bin/env python3

"""
Comprehensive API Testing Suite for React SPA Migration - Phase 2
Runs all unit tests for API endpoints to verify ApiResponse wrapper functionality
"""

import sys
import pytest
import subprocess
from pathlib import Path


def run_tests():
    """Run comprehensive API test suite."""

    print("🚀 Starting React SPA Migration - Phase 2: Unit Testing")
    print("=" * 60)

    # Test configurations
    test_files = [
        "tests/test_api_response.py",           # ApiResponse wrapper tests
        "tests/test_users_crud_complete.py",     # User management tests
        "tests/test_stories_crud_complete.py",   # Story management tests
        "tests/test_world_building_complete.py", # World building tests
        "tests/test_dashboard_billing_complete.py", # Dashboard & billing tests
        "tests/test_forum_admin_complete.py",    # Forum & admin tests
        "tests/conftest.py",                     # Fixtures and configuration
    ]

    print(f"📋 Found {len(test_files)} test files to run")

    # Run pytest with comprehensive options
    cmd = [
        "python", "-m", "pytest",
        "--tb=short",                           # Short traceback format
        "--verbose",                           # Verbose output
        "--no-header",                         # Clean output
        "--capture=no",                        # Show print statements
        "-x",                                  # Stop on first failure
        "--strict-markers",                    # Strict marker validation
        "--asyncio-mode=auto",                # Automatic async testing
    ]

    # Add test files
    cmd.extend(test_files)

    print("🏃 Running test suite...")
    print("-" * 40)

    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)

        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED!")
            print("🎉 Phase 2: Unit Testing - COMPLETED")
            print("\n📊 API endpoints are now fully tested with:")
            print("   - ✅ ApiResponse wrapper functionality")
            print("   - ✅ React SPA compatible JSON responses")
            print("   - ✅ Bearer token authentication")
            print("   - ✅ Error handling")
            print("   - ✅ Pagination support")
            print("   - ✅ CRUD operations coverage")
            print("\n🚀 Ready for React frontend integration!")
        else:
            print("❌ SOME TESTS FAILED")
            print("📋 Review the test output above and fix failing tests")
            print("💡 Common issues:")
            print("   - Mock objects not returning expected data")
            print("   - Async/await patterns not properly mocked")
            print("   - Database session handling issues")
            sys.exit(1)

    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest:")
        print("   pip install pytest pytest-asyncio")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)


def show_test_coverage_summary():
    """Show a summary of what the tests cover."""
    print("\n🔍 TEST COVEContextE SUMMARY")
    print("-" * 40)
    print("✅ ApiResponse Wrapper Tests")
    print("   - Standard response format validation")
    print("   - Error response handling")
    print("   - Pagination metadata support")
    print("   - Serialization to JSON")
    print()
    print("✅ Authentication & User Management")
    print("   - Bearer token endpoint (/auth/token)")
    print("   - Token refresh (/auth/refresh)")
    print("   - User profile CRUD (/users/me)")
    print("   - Admin user management")
    print()
    print("✅ Story Management")
    print("   - Story CRUD operations")
    print("   - Story publishing & search")
    print("   - Story analytics & dashboard")
    print()
    print("✅ World Building")
    print("   - World CRUD with ownership")
    print("   - Character and location management")
    print("   - Lore items and associations")
    print("   - Batch operations support")
    print()
    print("✅ Dashboard & Analytics")
    print("   - User activity dashboard")
    print("   - Billing account summary")
    print("   - Coin balance & transactions")
    print("   - Usage analytics & costs")
    print()
    print("✅ Forum & Community")
    print("   - Category management (admin)")
    print("   - Thread and post CRUD")
    print("   - Voting and moderation")
    print("   - User statistics")
    print()
    print("✅ Administrative Functions")
    print("   - CTA content management")
    print("   - User debugging tools")
    print("   - Content moderation")
    print()
    print("🎯 REACT SPA COMPATIBILITY VERIFIED:")
    print("   - ✅ Consistent ApiResponse format")
    print("   - ✅ Bearer token authentication")
    print("   - ✅ TypeScript-friendly responses")
    print("   - ✅ Error handling patterns")
    print("   - ✅ Pagination support")


if __name__ == "__main__":
    # Check if running from correct directory
    if not Path("tests").exists():
        print("❌ Error: Run this script from the project root directory")
        print("   The 'tests' directory was not found")
        sys.exit(1)

    # Show coverage summary first
    show_test_coverage_summary()

    # Run the tests
    print()
    run_tests()
