#!/usr/bin/env python3
"""
Model-Specific Temperature Optimization for Your AI Models
Dynamically adjusts temperature based on model capabilities and task type.
"""

from typing import Dict, Optional
from enum import Enum

class TaskType(Enum):
    CREATIVE_WRITING = "creative_writing"
    DIALOGUE_WRITING = "dialogue_writing"
    TECHNICAL_WRITING = "technical_writing"
    WORLD_BUILDING = "world_building"
    CHARACTER_DEVELOPMENT = "character_development"
    PLOT_PLANNING = "plot_planning"
    EDITING = "editing"
    BRAINSTORMING = "brainstorming"
    JSON_EXTRACTION = "json_extraction"
    CHAT_CONVERSATION = "chat_conversation"

class ModelTemperatureOptimizer:
    """Optimizes temperature based on model capabilities and task requirements"""
    
    # Model-specific optimal temperatures for different tasks
    MODEL_TASK_TEMPERATURES = {
        # Premium Creative Models
        "DeepSeek-V3-0324": {
            TaskType.CREATIVE_WRITING: 0.85,
            TaskType.DIALOGUE_WRITING: 0.9,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 1.0,
        },
        
        "anthropic/claude-3.5-sonnet": {
            TaskType.CREATIVE_WRITING: 0.9,
            TaskType.DIALOGUE_WRITING: 0.95,
            TaskType.WORLD_BUILDING: 0.85,
            TaskType.CHARACTER_DEVELOPMENT: 0.9,
            TaskType.CHAT_CONVERSATION: 0.8,
            TaskType.JSON_EXTRACTION: 0.25,
            TaskType.TECHNICAL_WRITING: 0.35,
            TaskType.BRAINSTORMING: 1.1,
        },
        
        "gpt-4o": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.BRAINSTORMING: 0.95,
        },
        
        # Fast & Efficient Models
        "gpt-4o-mini": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.8,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.9,
        },
        
        "google/gemini-2.0-flash-exp": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.95,
        },
        
        # Reasoning Models
        "deepseek/deepseek-r1": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.75,  # Reasoning models less creative with dialogue
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.65,  # Better at factual responses
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.PLOT_PLANNING: 0.6,  # Excellent at logical plot structure
        },
        
        "google/gemini-2.0-flash-thinking-exp": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.7,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.65,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.25,
            TaskType.PLOT_PLANNING: 0.5,
        },
        
        # Specialized Models
        "qwen/qwen-2.5-coder-32b-instruct": {
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.CREATIVE_WRITING: 0.6,  # Not optimized for creativity
            TaskType.CHAT_CONVERSATION: 0.5,
        },
        
        # Cost-Effective Models
        "mistralai/mixtral-8x7b-instruct": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.8,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.TECHNICAL_WRITING: 0.4,
        },
    }
    
    # Default temperatures by task type (fallback for unknown models)
    DEFAULT_TASK_TEMPERATURES = {
        TaskType.CREATIVE_WRITING: 0.8,
        TaskType.DIALOGUE_WRITING: 0.9,
        TaskType.TECHNICAL_WRITING: 0.3,
        TaskType.WORLD_BUILDING: 0.8,
        TaskType.CHARACTER_DEVELOPMENT: 0.85,
        TaskType.PLOT_PLANNING: 0.6,
        TaskType.EDITING: 0.3,
        TaskType.BRAINSTORMING: 1.0,
        TaskType.JSON_EXTRACTION: 0.2,
        TaskType.CHAT_CONVERSATION: 0.7,
    }
    
    @classmethod
    def get_optimal_temperature(
        cls,
        model_name: str,
        task_type: TaskType,
        base_temperature: float = 0.7,
        user_creativity_preference: float = 0.0  # -0.3 to +0.3 adjustment
    ) -> float:
        """
        Get optimal temperature for a specific model and task.
        
        Args:
            model_name: The model name (e.g., "gpt-4o-mini")
            task_type: The type of task being performed
            base_temperature: Fallback temperature from model config
            user_creativity_preference: User's creativity adjustment
            
        Returns:
            Optimized temperature value
        """
        
        # Get model-specific temperature if available
        if model_name in cls.MODEL_TASK_TEMPERATURES:
            model_temps = cls.MODEL_TASK_TEMPERATURES[model_name]
            if task_type in model_temps:
                optimal_temp = model_temps[task_type]
            else:
                # Use default for this task type
                optimal_temp = cls.DEFAULT_TASK_TEMPERATURES.get(task_type, base_temperature)
        else:
            # Unknown model, use task-based default
            optimal_temp = cls.DEFAULT_TASK_TEMPERATURES.get(task_type, base_temperature)
        
        # Apply user creativity preference
        optimal_temp += user_creativity_preference
        
        # Clamp to reasonable bounds
        optimal_temp = max(0.0, min(1.5, optimal_temp))
        
        return round(optimal_temp, 2)
    
    @classmethod
    def detect_task_from_instruction(cls, instruction: str) -> TaskType:
        """Auto-detect task type from user instruction"""
        instruction_lower = instruction.lower()
        
        # Task detection keywords
        if any(word in instruction_lower for word in ["dialogue", "conversation", "talking", "speech"]):
            return TaskType.DIALOGUE_WRITING
        elif any(word in instruction_lower for word in ["world", "setting", "environment", "location"]):
            return TaskType.WORLD_BUILDING
        elif any(word in instruction_lower for word in ["character", "personality", "motivation", "backstory"]):
            return TaskType.CHARACTER_DEVELOPMENT
        elif any(word in instruction_lower for word in ["plot", "structure", "outline", "plan"]):
            return TaskType.PLOT_PLANNING
        elif any(word in instruction_lower for word in ["edit", "revise", "fix", "correct"]):
            return TaskType.EDITING
        elif any(word in instruction_lower for word in ["brainstorm", "ideas", "creative", "experimental"]):
            return TaskType.BRAINSTORMING
        elif any(word in instruction_lower for word in ["json", "data", "extract", "metadata"]):
            return TaskType.JSON_EXTRACTION
        elif any(word in instruction_lower for word in ["technical", "explain", "how", "documentation"]):
            return TaskType.TECHNICAL_WRITING
        else:
            return TaskType.CREATIVE_WRITING  # Default
    
    @classmethod
    def get_model_strengths(cls, model_name: str) -> Dict[str, str]:
        """Get model strengths for UI display"""
        strengths = {
            "DeepSeek-V3-0324": "671B parameters, excellent creative writing, 128K context",
            "anthropic/claude-3.5-sonnet": "Best creative writing, character development, dialogue",
            "gpt-4o": "Most powerful, complex reasoning, highest quality",
            "gpt-4o-mini": "Fast, cost-effective, good all-around",
            "google/gemini-2.0-flash-exp": "1M context, fast, efficient",
            "deepseek/deepseek-r1": "Advanced reasoning, plot planning, logical structure",
            "google/gemini-2.0-flash-thinking-exp": "Enhanced reasoning with thinking process",
            "qwen/qwen-2.5-coder-32b-instruct": "Code generation, technical writing",
            "mistralai/mixtral-8x7b-instruct": "Cost-effective, good creativity",
        }
        return strengths.get(model_name, "General purpose language model")

# Example usage functions
def optimize_writing_assistant_temperature(
    model_name: str,
    user_instruction: str,
    base_temperature: float,
    user_wants_more_creative: bool = False
) -> tuple[float, TaskType, str]:
    """
    Optimize temperature for writing assistant
    Returns: (optimized_temp, detected_task, explanation)
    """
    
    # Detect task type
    task_type = ModelTemperatureOptimizer.detect_task_from_instruction(user_instruction)
    
    # User creativity adjustment
    creativity_adj = 0.2 if user_wants_more_creative else 0.0
    
    # Get optimal temperature
    optimal_temp = ModelTemperatureOptimizer.get_optimal_temperature(
        model_name=model_name,
        task_type=task_type,
        base_temperature=base_temperature,
        user_creativity_preference=creativity_adj
    )
    
    # Generate explanation
    explanation = f"Optimized for {task_type.value.replace('_', ' ')} using {model_name}"
    if creativity_adj > 0:
        explanation += f" (increased creativity by {creativity_adj})"
    
    return optimal_temp, task_type, explanation

# Example scenarios with your models
if __name__ == "__main__":
    scenarios = [
        ("DeepSeek-V3-0324", "Write creative dialogue between two characters", 0.7),
        ("gpt-4o-mini", "Add more technical details to this scene", 0.7),
        ("deepseek/deepseek-r1", "Plan the overall plot structure", 0.7),
        ("google/gemini-2.0-flash-thinking-exp", "Brainstorm character motivations", 0.7),
        ("anthropic/claude-3.5-sonnet", "Write a poetic description of the landscape", 0.7),
    ]
    
    print("🎯 Temperature Optimization Examples:")
    print("=" * 60)
    
    for model, instruction, base_temp in scenarios:
        optimal_temp, task_type, explanation = optimize_writing_assistant_temperature(
            model, instruction, base_temp
        )
        
        print(f"\n📝 Model: {model}")
        print(f"💬 Instruction: \"{instruction}\"")
        print(f"🌡️  Base → Optimal: {base_temp} → {optimal_temp}")
        print(f"🎯 Task: {task_type.value}")
        print(f"💡 {explanation}")
        
        # Show impact
        impact = "More creative" if optimal_temp > base_temp else "More focused" if optimal_temp < base_temp else "Unchanged"
        print(f"📈 Impact: {impact}")