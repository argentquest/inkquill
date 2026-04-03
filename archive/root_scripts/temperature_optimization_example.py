#!/usr/bin/env python3
"""
Example: Dynamic Temperature Selection for Enhanced Creative Writing
This shows how to optimize temperature based on writing context.
"""

from typing import Dict, Optional
from enum import Enum

class WritingContext(Enum):
    DIALOGUE = "dialogue"
    ACTION = "action" 
    DESCRIPTION = "description"
    INTROSPECTION = "introspection"
    WORLD_BUILDING = "world_building"
    TECHNICAL = "technical"

class TemperatureOptimizer:
    """Dynamically selects optimal temperature based on writing context"""
    
    # Temperature mapping for different contexts
    CONTEXT_TEMPERATURES: Dict[WritingContext, float] = {
        WritingContext.DIALOGUE: 0.9,          # High creativity for character voices
        WritingContext.ACTION: 0.7,            # Balanced for exciting but clear action
        WritingContext.DESCRIPTION: 0.8,       # Creative but coherent descriptions
        WritingContext.INTROSPECTION: 0.85,    # High creativity for internal thoughts
        WritingContext.WORLD_BUILDING: 0.8,    # Creative but consistent world details
        WritingContext.TECHNICAL: 0.3,         # Low for clear, consistent explanations
    }
    
    # Temperature adjustments based on user instruction keywords
    INSTRUCTION_MODIFIERS: Dict[str, float] = {
        "creative": +0.2,
        "experimental": +0.3,
        "wild": +0.4,
        "conservative": -0.3,
        "consistent": -0.2,
        "clear": -0.2,
        "detailed": +0.1,
        "simple": -0.2,
        "complex": +0.1,
        "poetic": +0.3,
        "straightforward": -0.3,
    }
    
    @classmethod
    def get_optimal_temperature(
        cls, 
        base_temperature: float,
        writing_context: Optional[WritingContext] = None,
        user_instruction: str = "",
        content_analysis: Optional[str] = None
    ) -> float:
        """
        Calculate optimal temperature based on context and user intent.
        
        Args:
            base_temperature: Default temperature from model config
            writing_context: Type of content being written
            user_instruction: User's writing instruction
            content_analysis: Analysis of existing content
            
        Returns:
            Optimized temperature value
        """
        
        # Start with base temperature
        optimal_temp = base_temperature
        
        # Adjust based on writing context
        if writing_context and writing_context in cls.CONTEXT_TEMPERATURES:
            context_temp = cls.CONTEXT_TEMPERATURES[writing_context]
            # Blend with base temperature (70% context, 30% base)
            optimal_temp = (context_temp * 0.7) + (base_temperature * 0.3)
        
        # Apply instruction-based modifiers
        instruction_lower = user_instruction.lower()
        for keyword, modifier in cls.INSTRUCTION_MODIFIERS.items():
            if keyword in instruction_lower:
                optimal_temp += modifier
        
        # Analyze content for automatic context detection
        if content_analysis:
            detected_context = cls._analyze_content_context(content_analysis)
            if detected_context:
                context_adjustment = cls.CONTEXT_TEMPERATURES[detected_context]
                optimal_temp = (optimal_temp * 0.8) + (context_adjustment * 0.2)
        
        # Clamp to reasonable bounds
        optimal_temp = max(0.1, min(1.5, optimal_temp))
        
        return round(optimal_temp, 2)
    
    @classmethod
    def _analyze_content_context(cls, content: str) -> Optional[WritingContext]:
        """Analyze content to detect writing context automatically"""
        content_lower = content.lower()
        
        # Simple keyword-based detection (could be enhanced with ML)
        if any(word in content_lower for word in ['"', "'", "said", "asked", "replied"]):
            return WritingContext.DIALOGUE
        elif any(word in content_lower for word in ["ran", "fought", "charged", "attacked"]):
            return WritingContext.ACTION
        elif any(word in content_lower for word in ["thought", "felt", "remembered", "wondered"]):
            return WritingContext.INTROSPECTION
        elif any(word in content_lower for word in ["landscape", "building", "appearance", "looked like"]):
            return WritingContext.DESCRIPTION
        
        return None

# Example usage in your writing assistant:
def enhance_writing_with_dynamic_temperature(
    user_instruction: str,
    current_scene_content: str,
    base_model_temperature: float
) -> float:
    """
    Example integration with existing writing assistant
    """
    
    # Detect writing context from user instruction
    context = None
    instruction_lower = user_instruction.lower()
    
    if "dialogue" in instruction_lower or "conversation" in instruction_lower:
        context = WritingContext.DIALOGUE
    elif "action" in instruction_lower or "fight" in instruction_lower:
        context = WritingContext.ACTION
    elif "describe" in instruction_lower or "appearance" in instruction_lower:
        context = WritingContext.DESCRIPTION
    elif "thoughts" in instruction_lower or "internal" in instruction_lower:
        context = WritingContext.INTROSPECTION
    elif "world" in instruction_lower or "setting" in instruction_lower:
        context = WritingContext.WORLD_BUILDING
    
    # Get optimized temperature
    optimal_temp = TemperatureOptimizer.get_optimal_temperature(
        base_temperature=base_model_temperature,
        writing_context=context,
        user_instruction=user_instruction,
        content_analysis=current_scene_content
    )
    
    print(f"Base temp: {base_model_temperature} → Optimized: {optimal_temp}")
    print(f"Context: {context}, Instruction: '{user_instruction[:50]}...'")
    
    return optimal_temp

# Example scenarios:
if __name__ == "__main__":
    base_temp = 0.7
    
    # Scenario 1: Dialogue writing
    temp1 = enhance_writing_with_dynamic_temperature(
        "Add more creative dialogue between the characters",
        'The scene contained: "Hello," she said.',
        base_temp
    )
    
    # Scenario 2: Action scene
    temp2 = enhance_writing_with_dynamic_temperature(
        "Write a clear action sequence",
        "The battle raged on...",
        base_temp
    )
    
    # Scenario 3: Experimental creative writing
    temp3 = enhance_writing_with_dynamic_temperature(
        "Make this more experimental and poetic",
        "The character walked through the forest.",
        base_temp
    )
    
    print(f"\nResults:")
    print(f"Dialogue (creative): {temp1}")      # Should be ~0.9
    print(f"Action (clear): {temp2}")           # Should be ~0.5  
    print(f"Experimental: {temp3}")             # Should be ~1.1