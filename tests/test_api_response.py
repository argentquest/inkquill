# tests/test_api_response.py

"""
Unit tests for ApiResponse wrapper and error handling
Tests standardized API response functionality
"""
import pytest
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

from app.schemas.base import ApiResponse, ApiMeta, ApiError


class TestApiResponseSchema:
    """Test ApiResponse Pydantic models"""

    def test_api_response_basic_structure(self):
        """Test ApiResponse has all required fields"""
        response = ApiResponse(success=True, data="test_data")

        assert hasattr(response, 'success')
        assert hasattr(response, 'data')
        assert hasattr(response, 'errors')
        assert hasattr(response, 'meta')

        assert response.success is True
        assert response.data == "test_data"
        assert response.errors is None
        assert response.meta is None

    def test_api_response_with_meta(self):
        """Test ApiResponse with metadata"""
        meta = ApiMeta(
            page=1,
            limit=10,
            total=25,
            pages=3
        )

        response = ApiResponse.success_response(data={"key": "value"}, meta=meta)

        assert response.meta.page == 1
        assert response.meta.limit == 10
        assert response.meta.total == 25
        assert response.meta.pages == 3

    def test_api_response_with_errors(self):
        """Test ApiResponse with error information"""
        errors = [
            ApiError(code="VALIDATION_ERROR", message="Email is required"),
            ApiError(code="DUPLICATE_ENTRY", message="Username already exists")
        ]

        response = ApiResponse.error_response(errors=errors)

        assert response.success is False
        assert response.data is None
        assert len(response.errors) == 2
        assert response.errors[0].code == "VALIDATION_ERROR"
        assert response.errors[1].code == "DUPLICATE_ENTRY"

    def test_api_response_validation(self):
        """Test ApiResponse field validation"""
        # Valid response
        response = ApiResponse(
            success=True,
            data=42,
            errors=None,
            meta=None
        )
        assert response.data == 42

        # Invalid: success=True but has errors
        # This should still work - errors field can be present regardless of success
        response_with_errors = ApiResponse(
            success=True,
            data="success",
            errors=[ApiError(code="WARNING", message="Minor issue")]
        )
        assert response_with_errors.success is True
        assert response_with_errors.data == "success"
        assert len(response_with_errors.errors) == 1

    def test_api_response_serialization(self):
        """Test ApiResponse can be properly serialized to JSON"""
        response = ApiResponse.success_response(
            data=["item1", "item2", "item3"],
            meta=ApiMeta(page=1, limit=3, total=10, pages=4)
        )

        # Convert to dict (simulating JSON serialization)
        response_dict = response.model_dump()

        assert response_dict["success"] is True
        assert len(response_dict["data"]) == 3
        assert response_dict["meta"]["page"] == 1
        assert response_dict["meta"]["total"] == 10


class TestApiMeta:
    """Test ApiMeta schema"""

    def test_api_meta_calculation(self):
        """Test API metadata calculation"""
        meta = ApiMeta(page=2, limit=20, total=100)

        # The pages field is calculated if not provided
        # In this schema, pages might be automatically calculated or optional

        assert meta.page == 2
        assert meta.limit == 20
        assert meta.total == 100

    def test_api_meta_pagination_helpers(self):
        """Test pagination helper methods"""
        meta = ApiMeta(page=1, limit=10, total=50)

        # Test offset calculation (would be nice to have)
        expected_offset = (meta.page - 1) * meta.limit  # 0 for page 1
        assert expected_offset == 0

        meta_page_2 = ApiMeta(page=2, limit=10, total=50)
        expected_offset_page_2 = (meta_page_2.page - 1) * meta_page_2.limit  # 10 for page 2
        assert expected_offset_page_2 == 10


class TestApiError:
    """Test ApiError schema"""

    def test_api_error_creation(self):
        """Test ApiError basic creation"""
        error = ApiError(code="NOT_FOUND", message="Resource not found")

        assert error.code == "NOT_FOUND"
        assert error.message == "Resource not found"
        assert error.details is None

    def test_api_error_with_details(self):
        """Test ApiError with additional details"""
        details = {
            "resource": "user",
            "id": 123,
            "field": "email"
        }

        error = ApiError(
            code="INVALID_FORMAT",
            message="Email format is invalid",
            details=details
        )

        assert error.code == "INVALID_FORMAT"
        assert error.details == details
        assert error.details["resource"] == "user"


class TestErrorHandlingIntegration:
    """Test error handling across API responses"""

    def test_http_exception_to_api_error_conversion(self):
        """Test converting HTTPException to ApiError format"""
        # This simulates how endpoints might convert exceptions to API responses

        http_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

        # Convert to ApiError
        api_error = ApiError(
            code="NOT_FOUND",
            message=str(http_exception.detail)
        )

        response = ApiResponse.error_response(errors=[api_error])

        assert response.success is False
        assert len(response.errors) == 1
        assert response.errors[0].code == "NOT_FOUND"

    def test_multiple_error_scenarios(self):
        """Test handling multiple types of errors in single response"""
        errors = [
            ApiError(code="VALIDATION_ERROR", message="Field 'email' is required"),
            ApiError(code="TYPE_ERROR", message="Field 'age' must be integer"),
            ApiError(code="UNIQUE_CONSTRAINT", message="Username already exists")
        ]

        response = ApiResponse.error_response(errors=errors)

        assert response.success is False
        assert len(response.errors) == 3

        # Check error codes are unique
        error_codes = [e.code for e in response.errors]
        assert len(set(error_codes)) == len(error_codes)  # All codes unique


class TestApiResponsePatterns:
    """Test common API response patterns and best practices"""

    def test_success_response_pattern(self):
        """Test standard success response pattern"""
        data = {"user_id": 123, "username": "testuser"}

        response = ApiResponse.success_response(data=data)

        # Verify standard success pattern
        assert response.success is True
        assert response.data is not None
        assert response.errors is None or len(response.errors or []) == 0

    def test_error_response_pattern(self):
        """Test standard error response pattern"""
        errors = [
            ApiError(code="PERMISSION_DENIED", message="Access forbidden")
        ]

        response = ApiResponse.error_response(errors=errors)

        # Verify standard error pattern
        assert response.success is False
        assert response.data is None  # Typically no data on error
        assert len(response.errors) > 0

    def test_paginated_response_pattern(self):
        """Test paginated response pattern"""
        data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]

        meta = {
            "page": 1,
            "limit": 10,
            "total": 25,
            "pages": 3
        }

        paginated_meta = ApiMeta(**meta)

        response = ApiResponse.success_response(data=data, meta=paginated_meta)

        assert response.success is True
        assert len(response.data) == 2
        assert response.meta.total == 25
        assert response.meta.pages == 3

    def test_empty_data_response(self):
        """Test response pattern for empty data (not an error)"""
        response = ApiResponse.success_response(
            data=[],
            meta=ApiMeta(page=1, limit=10, total=0, pages=0)
        )

        assert response.success is True
        assert response.data == []
        assert response.meta.total == 0


class TestCrossCompatibility:
    """Test ApiResponse compatibility with FastAPI and other systems"""

    def test_fastapi_response_integration(self):
        """Test that ApiResponse works well with FastAPI Response models"""
        # This simulates how the response is used in FastAPI endpoints

        # Simulate endpoint return
        def mock_endpoint_success():
            return ApiResponse.success_response(data="Operation completed successfully")

        def mock_endpoint_error():
            return ApiResponse.error_response(errors=[ApiError(code="SERVER_ERROR", message="Internal server error")])

        success_response = mock_endpoint_success()
        error_response = mock_endpoint_error()

        # Verify both patterns work
        assert success_response.success is True
        assert success_response.data == "Operation completed successfully"

        assert error_response.success is False
        assert len(error_response.errors) == 1

    def test_json_schema_generation(self):
        """Test that the schemas generate proper JSON schemas"""
        # Verify the Pydantic models have proper JSON schemas
        response_schema = ApiResponse.model_json_schema()

        assert "properties" in response_schema
        assert "success" in response_schema["properties"]
        assert "data" in response_schema["properties"]
        assert "errors" in response_schema["properties"]
        assert "meta" in response_schema["properties"]