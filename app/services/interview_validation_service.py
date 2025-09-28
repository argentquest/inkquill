"""
Interview Validation Service
Handles JSON schema validation for interview questions and responses
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import logging

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    jsonschema = None

logger = logging.getLogger(__name__)


class InterviewValidationService:
    """Service for validating interview JSON data against schemas"""
    
    def __init__(self):
        self.schema_dir = Path(__file__).parent.parent / "data" / "schemas"
        self._questions_schema = None
        self._response_schema = None
    
    @property
    def questions_schema(self) -> Dict[str, Any]:
        """Lazy load questions schema"""
        if self._questions_schema is None:
            self._questions_schema = self._load_schema("interview_questions_schema.json")
        return self._questions_schema
    
    @property
    def response_schema(self) -> Dict[str, Any]:
        """Lazy load response schema"""
        if self._response_schema is None:
            self._response_schema = self._load_schema("interview_response_schema.json")
        return self._response_schema
    
    def _load_schema(self, filename: str) -> Dict[str, Any]:
        """Load JSON schema from file"""
        schema_path = self.schema_dir / filename
        
        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            raise FileNotFoundError(f"Schema file not found: {filename}")
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            logger.debug(f"Loaded schema: {filename}")
            return schema
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file {filename}: {e}")
            raise ValueError(f"Invalid JSON schema file: {filename}")
        except Exception as e:
            logger.error(f"Error loading schema {filename}: {e}")
            raise
    
    def validate_questions(self, questions_data: Dict[str, Any]) -> bool:
        """
        Validate interview questions against schema
        
        Args:
            questions_data: The questions JSON data to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            HTTPException: If validation fails
        """
        logger.info(f"validate_questions called for interview_id: {questions_data.get('interview_id')}")
        logger.info(f"JSONSCHEMA_AVAILABLE: {JSONSCHEMA_AVAILABLE}")
        
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema library not available, performing basic validation only")
            return self._basic_questions_validation(questions_data)
        
        try:
            logger.info("Loading questions schema...")
            schema = self.questions_schema
            logger.info(f"Questions schema loaded successfully, has {len(schema.keys())} top-level keys")
            
            logger.info("Starting jsonschema validation...")
            jsonschema.validate(questions_data, schema)
            logger.info(f"Questions validation passed for interview: {questions_data.get('interview_id')}")
            return True
            
        except jsonschema.ValidationError as e:
            error_msg = f"Invalid questions format: {e.message}"
            if e.absolute_path:
                error_msg += f" at path: {'.'.join(str(p) for p in e.absolute_path)}"
            
            logger.warning(f"Questions validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
        except Exception as e:
            logger.error(f"Unexpected error during questions validation: {e}")
            raise HTTPException(status_code=500, detail="Schema validation error")
    
    def validate_response(self, response_data: Dict[str, Any]) -> bool:
        """
        Validate interview response against schema
        
        Args:
            response_data: The response JSON data to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            HTTPException: If validation fails
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema library not available, performing basic validation only")
            return self._basic_response_validation(response_data)
        
        try:
            jsonschema.validate(response_data, self.response_schema)
            logger.info(f"Response validation passed for user: {response_data.get('user_id')}")
            return True
            
        except jsonschema.ValidationError as e:
            error_msg = f"Invalid response format: {e.message}"
            if e.absolute_path:
                error_msg += f" at path: {'.'.join(str(p) for p in e.absolute_path)}"
            
            logger.warning(f"Response validation failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
        except Exception as e:
            logger.error(f"Unexpected error during response validation: {e}")
            raise HTTPException(status_code=500, detail="Schema validation error")
    
    def validate_response_against_questions(
        self, 
        response_data: Dict[str, Any], 
        questions_data: Dict[str, Any]
    ) -> List[str]:
        """
        Cross-validate response data against the actual questions
        
        Args:
            response_data: User's response data
            questions_data: The interview questions
            
        Returns:
            List[str]: List of validation warnings (empty if all valid)
        """
        warnings = []
        
        try:
            # Get question definitions
            questions = {q['id']: q for q in questions_data.get('questions', [])}
            responses = response_data.get('responses', {})
            
            for question_id, response in responses.items():
                if question_id not in questions:
                    warnings.append(f"Response for unknown question: {question_id}")
                    continue
                
                question = questions[question_id]
                
                # Check required questions
                if question.get('required', True) and response.get('skipped', False):
                    warnings.append(f"Required question was skipped: {question_id}")
                
                # Validate option values for choice questions
                if question.get('ui_type') in ['single_choice', 'multiple_choice']:
                    valid_values = {opt['value'] for opt in question.get('options', [])}
                    selected_values = response.get('selected_values', [])
                    
                    for value in selected_values:
                        if value not in valid_values:
                            warnings.append(f"Invalid option value '{value}' for question: {question_id}")
                    
                    # Check selection count for single choice
                    if question.get('ui_type') == 'single_choice' and len(selected_values) > 1:
                        warnings.append(f"Single choice question has multiple selections: {question_id}")
                    
                    # Check minimum selections
                    min_selections = question.get('min_selections', 1 if question.get('required') else 0)
                    if not response.get('skipped') and len(selected_values) < min_selections:
                        warnings.append(f"Insufficient selections for question {question_id}: got {len(selected_values)}, need {min_selections}")
                
                # Validate text input length
                elif question.get('ui_type') == 'text_input':
                    text_value = response.get('text_value', '')
                    max_length = question.get('max_length', 10000)
                    
                    if len(text_value) > max_length:
                        warnings.append(f"Text too long for question {question_id}: {len(text_value)} > {max_length}")
            
            # Check for missing required questions
            for question_id, question in questions.items():
                if question.get('required', True) and question_id not in responses:
                    warnings.append(f"Missing response for required question: {question_id}")
            
        except Exception as e:
            logger.error(f"Error during cross-validation: {e}")
            warnings.append(f"Cross-validation error: {str(e)}")
        
        if warnings:
            logger.warning(f"Cross-validation warnings: {warnings}")
        
        return warnings
    
    def sanitize_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and sanitize response data
        
        Args:
            response_data: Raw response data
            
        Returns:
            Dict[str, Any]: Cleaned response data
        """
        try:
            # Create a deep copy to avoid modifying original
            import copy
            sanitized = copy.deepcopy(response_data)
            
            # Sanitize text inputs (basic HTML escape)
            responses = sanitized.get('responses', {})
            for question_id, response in responses.items():
                if 'text_value' in response:
                    # Basic HTML escaping
                    text = response['text_value']
                    text = text.replace('&', '&amp;')
                    text = text.replace('<', '&lt;')
                    text = text.replace('>', '&gt;')
                    text = text.replace('"', '&quot;')
                    text = text.replace("'", '&#x27;')
                    
                    # Limit length
                    response['text_value'] = text[:10000]
                
                # Ensure selected_values is unique
                if 'selected_values' in response:
                    response['selected_values'] = list(set(response['selected_values']))
            
            # Sanitize metadata
            metadata = sanitized.get('metadata', {})
            if 'user_agent' in metadata:
                metadata['user_agent'] = metadata['user_agent'][:500]
            
            logger.debug("Response data sanitized successfully")
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing response data: {e}")
            # Return original data if sanitization fails
            return response_data
    
    def _basic_questions_validation(self, questions_data: Dict[str, Any]) -> bool:
        """
        Basic validation when jsonschema is not available
        
        Args:
            questions_data: The questions JSON data to validate
            
        Returns:
            bool: True if basic validation passes
            
        Raises:
            HTTPException: If basic validation fails
        """
        try:
            # Check required top-level fields
            if not isinstance(questions_data, dict):
                raise HTTPException(status_code=400, detail="Questions data must be an object")
            
            if "interview_id" not in questions_data:
                raise HTTPException(status_code=400, detail="Missing required field: interview_id")
            
            if "questions" not in questions_data:
                raise HTTPException(status_code=400, detail="Missing required field: questions")
            
            questions = questions_data["questions"]
            if not isinstance(questions, list) or len(questions) == 0:
                raise HTTPException(status_code=400, detail="Questions must be a non-empty array")
            
            # Basic question validation
            for i, question in enumerate(questions):
                if not isinstance(question, dict):
                    raise HTTPException(status_code=400, detail=f"Question {i} must be an object")
                
                required_fields = ["id", "order", "question", "ui_type", "required"]
                for field in required_fields:
                    if field not in question:
                        raise HTTPException(status_code=400, detail=f"Question {i} missing required field: {field}")
                
                # Validate ui_type
                valid_ui_types = ["single_choice", "multiple_choice", "text_input"]
                if question["ui_type"] not in valid_ui_types:
                    raise HTTPException(status_code=400, detail=f"Question {i} has invalid ui_type: {question['ui_type']}")
                
                # Validate options for choice questions
                if question["ui_type"] in ["single_choice", "multiple_choice"]:
                    if "options" not in question or not isinstance(question["options"], list):
                        raise HTTPException(status_code=400, detail=f"Question {i} requires options array")
                    
                    if len(question["options"]) == 0:
                        raise HTTPException(status_code=400, detail=f"Question {i} must have at least one option")
            
            logger.info(f"Basic questions validation passed for interview: {questions_data.get('interview_id')}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in basic questions validation: {e}")
            raise HTTPException(status_code=500, detail="Basic validation error")
    
    def _basic_response_validation(self, response_data: Dict[str, Any]) -> bool:
        """
        Basic validation when jsonschema is not available
        
        Args:
            response_data: The response JSON data to validate
            
        Returns:
            bool: True if basic validation passes
            
        Raises:
            HTTPException: If basic validation fails
        """
        try:
            # Check required top-level fields
            if not isinstance(response_data, dict):
                raise HTTPException(status_code=400, detail="Response data must be an object")
            
            required_fields = ["interview_id", "user_id", "responses"]
            for field in required_fields:
                if field not in response_data:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            # Check user_id is positive integer
            if not isinstance(response_data["user_id"], int) or response_data["user_id"] <= 0:
                raise HTTPException(status_code=400, detail="user_id must be a positive integer")
            
            # Check responses is object
            responses = response_data["responses"]
            if not isinstance(responses, dict) or len(responses) == 0:
                raise HTTPException(status_code=400, detail="responses must be a non-empty object")
            
            # Basic response validation
            for question_id, response in responses.items():
                if not isinstance(response, dict):
                    raise HTTPException(status_code=400, detail=f"Response for {question_id} must be an object")
                
                if "question_id" not in response:
                    raise HTTPException(status_code=400, detail=f"Response for {question_id} missing question_id")
                
                if "answered_at" not in response:
                    raise HTTPException(status_code=400, detail=f"Response for {question_id} missing answered_at")
                
                # Check that response has either selected_values, text_value, or is skipped
                has_selected = "selected_values" in response and isinstance(response["selected_values"], list)
                has_text = "text_value" in response and isinstance(response["text_value"], str)
                is_skipped = response.get("skipped", False)
                
                if not (has_selected or has_text or is_skipped):
                    raise HTTPException(status_code=400, detail=f"Response for {question_id} must have selected_values, text_value, or be skipped")
            
            logger.info(f"Basic response validation passed for user: {response_data.get('user_id')}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in basic response validation: {e}")
            raise HTTPException(status_code=500, detail="Basic validation error")


# Global instance
validation_service = InterviewValidationService()