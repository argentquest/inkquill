import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class SimpleMathProvider(BaseCareCircleProvider):
    provider_key = "simple_math"
    is_safe_for_patient = True

    """
    Simple math problems with very basic arithmetic.
    Designed for elderly users - single digit numbers only.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a simple math problem.
        
        Returns:
            dict with math problem data
        """
        cfg = self.patient_config
        
        # Difficulty settings
        difficulty = self.difficulty_level
        
        if difficulty == "easy":
            # Single digit addition/subtraction
            num1 = random.randint(1, 5)
            num2 = random.randint(1, 5)
        elif difficulty == "medium":
            # Larger single digit
            num1 = random.randint(1, 9)
            num2 = random.randint(1, 9)
        else:  # hard
            # Double digit
            num1 = random.randint(10, 20)
            num2 = random.randint(1, 10)
        
        # Randomly choose addition or subtraction
        if random.choice([True, False]):
            # Addition
            answer = num1 + num2
            operator = "+"
            problem = f"{num1} {operator} {num2} = ?"
        else:
            # Subtraction (ensure positive result)
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
            operator = "-"
            problem = f"{num1} {operator} {num2} = ?"
        
        return {
            "title": "Easy Math",
            "instruction": "Can you solve this?",
            "problem": problem,
            "answer": str(answer),
        }
