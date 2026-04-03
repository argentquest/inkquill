"""Service helpers for temperature optimizer."""

# /story_app/app/services/temperature_optimizer.py

import logging
from typing import Dict, Optional, Tuple
from enum import Enum
import re

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Enum for different types of AI tasks"""
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
    CONTEXT_RETRIEVAL = "context_retrieval"
    METADATA_EXTRACTION = "metadata_extraction"
    SCENE_WRITING = "scene_writing"
    ACT_WRITING = "act_writing"
    STORY_GENERATION = "story_generation"

class TemperatureOptimizer:
    """
    Dynamic temperature optimization service that adjusts AI model temperature
    based on model capabilities, task type, and user intent.
    """
    
    # Model-specific optimal temperatures for different tasks
    MODEL_TASK_TEMPERATURES = {
        # Premium creative models
        "DeepSeek-V3-0324": {
            TaskType.CREATIVE_WRITING: 0.85,
            TaskType.DIALOGUE_WRITING: 0.9,
            TaskType.SCENE_WRITING: 0.85,
            TaskType.ACT_WRITING: 0.8,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 1.0,
            TaskType.STORY_GENERATION: 0.8,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "gpt-4o": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.SCENE_WRITING: 0.8,
            TaskType.ACT_WRITING: 0.75,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.METADATA_EXTRACTION: 0.1,
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.BRAINSTORMING: 0.95,
            TaskType.STORY_GENERATION: 0.75,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "gpt-4o-mini": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.8,
            TaskType.SCENE_WRITING: 0.75,
            TaskType.ACT_WRITING: 0.7,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.9,
            TaskType.STORY_GENERATION: 0.7,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "gpt-4.1-mini": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.8,
            TaskType.SCENE_WRITING: 0.75,
            TaskType.ACT_WRITING: 0.7,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.9,
            TaskType.STORY_GENERATION: 0.7,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        # Additional large-model presets
        "mistral-medium-2505": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.SCENE_WRITING: 0.8,
            TaskType.ACT_WRITING: 0.75,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.35,
            TaskType.BRAINSTORMING: 0.95,
            TaskType.STORY_GENERATION: 0.75,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "Meta-Llama-4-Scout-17B-16E-Instruct": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.SCENE_WRITING: 0.8,
            TaskType.ACT_WRITING: 0.75,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.95,
            TaskType.STORY_GENERATION: 0.75,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        # OpenRouter Models
        "anthropic/claude-3.5-sonnet": {
            TaskType.CREATIVE_WRITING: 0.9,
            TaskType.DIALOGUE_WRITING: 0.95,
            TaskType.SCENE_WRITING: 0.9,
            TaskType.ACT_WRITING: 0.85,
            TaskType.WORLD_BUILDING: 0.85,
            TaskType.CHARACTER_DEVELOPMENT: 0.9,
            TaskType.CHAT_CONVERSATION: 0.8,
            TaskType.JSON_EXTRACTION: 0.25,
            TaskType.METADATA_EXTRACTION: 0.2,
            TaskType.TECHNICAL_WRITING: 0.35,
            TaskType.BRAINSTORMING: 1.1,
            TaskType.STORY_GENERATION: 0.85,
            TaskType.CONTEXT_RETRIEVAL: 0.15,
        },
        
        "deepseek/deepseek-r1": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.75,  # Reasoning models less creative with dialogue
            TaskType.SCENE_WRITING: 0.75,
            TaskType.ACT_WRITING: 0.7,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.65,  # Better at factual responses
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.METADATA_EXTRACTION: 0.1,
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.PLOT_PLANNING: 0.6,  # Excellent at logical plot structure
            TaskType.STORY_GENERATION: 0.7,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "openai/gpt-4o": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.SCENE_WRITING: 0.8,
            TaskType.ACT_WRITING: 0.75,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.METADATA_EXTRACTION: 0.1,
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.BRAINSTORMING: 0.95,
            TaskType.STORY_GENERATION: 0.75,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "google/gemini-2.0-flash-exp": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.SCENE_WRITING: 0.8,
            TaskType.ACT_WRITING: 0.75,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.95,
            TaskType.STORY_GENERATION: 0.75,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "google/gemini-2.0-flash-thinking-exp": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.7,
            TaskType.SCENE_WRITING: 0.75,
            TaskType.ACT_WRITING: 0.7,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.65,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.METADATA_EXTRACTION: 0.1,
            TaskType.TECHNICAL_WRITING: 0.25,
            TaskType.PLOT_PLANNING: 0.5,
            TaskType.STORY_GENERATION: 0.7,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "meta-llama/llama-3.1-405b-instruct": {
            TaskType.CREATIVE_WRITING: 0.8,
            TaskType.DIALOGUE_WRITING: 0.85,
            TaskType.SCENE_WRITING: 0.8,
            TaskType.ACT_WRITING: 0.75,
            TaskType.WORLD_BUILDING: 0.8,
            TaskType.CHARACTER_DEVELOPMENT: 0.85,
            TaskType.CHAT_CONVERSATION: 0.75,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.BRAINSTORMING: 0.95,
            TaskType.STORY_GENERATION: 0.75,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "qwen/qwen-2.5-coder-32b-instruct": {
            TaskType.TECHNICAL_WRITING: 0.3,
            TaskType.JSON_EXTRACTION: 0.15,
            TaskType.METADATA_EXTRACTION: 0.1,
            TaskType.CREATIVE_WRITING: 0.6,  # Not optimized for creativity
            TaskType.SCENE_WRITING: 0.6,
            TaskType.ACT_WRITING: 0.55,
            TaskType.CHAT_CONVERSATION: 0.5,
            TaskType.STORY_GENERATION: 0.6,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
        
        "mistralai/mixtral-8x7b-instruct": {
            TaskType.CREATIVE_WRITING: 0.75,
            TaskType.DIALOGUE_WRITING: 0.8,
            TaskType.SCENE_WRITING: 0.75,
            TaskType.ACT_WRITING: 0.7,
            TaskType.WORLD_BUILDING: 0.75,
            TaskType.CHARACTER_DEVELOPMENT: 0.8,
            TaskType.CHAT_CONVERSATION: 0.7,
            TaskType.JSON_EXTRACTION: 0.2,
            TaskType.METADATA_EXTRACTION: 0.15,
            TaskType.TECHNICAL_WRITING: 0.4,
            TaskType.STORY_GENERATION: 0.7,
            TaskType.CONTEXT_RETRIEVAL: 0.1,
        },
    }
    
    # Default temperatures by task type (fallback for unknown models)
    DEFAULT_TASK_TEMPERATURES = {
        TaskType.CREATIVE_WRITING: 0.8,
        TaskType.DIALOGUE_WRITING: 0.9,
        TaskType.SCENE_WRITING: 0.8,
        TaskType.ACT_WRITING: 0.75,
        TaskType.TECHNICAL_WRITING: 0.3,
        TaskType.WORLD_BUILDING: 0.8,
        TaskType.CHARACTER_DEVELOPMENT: 0.85,
        TaskType.PLOT_PLANNING: 0.6,
        TaskType.EDITING: 0.3,
        TaskType.BRAINSTORMING: 1.0,
        TaskType.JSON_EXTRACTION: 0.2,
        TaskType.METADATA_EXTRACTION: 0.15,
        TaskType.CHAT_CONVERSATION: 0.7,
        TaskType.STORY_GENERATION: 0.75,
        TaskType.CONTEXT_RETRIEVAL: 0.1,
    }
    
    # User intent modifiers based on keywords in instructions
    INTENT_MODIFIERS = {
        # Creativity modifiers
        "creative": +0.2,
        "experimental": +0.3,
        "wild": +0.4,
        "imaginative": +0.25,
        "artistic": +0.25,
        "poetic": +0.3,
        "unique": +0.2,
        "original": +0.2,
        "innovative": +0.25,
        
        # Conservative modifiers
        "conservative": -0.3,
        "consistent": -0.2,
        "clear": -0.2,
        "simple": -0.2,
        "straightforward": -0.3,
        "precise": -0.25,
        "accurate": -0.2,
        "focused": -0.2,
        "structured": -0.25,
        
        # Quality modifiers
        "detailed": +0.1,
        "complex": +0.1,
        "sophisticated": +0.15,
        "nuanced": +0.15,
        "subtle": +0.1,
        
        # Style modifiers
        "formal": -0.2,
        "casual": +0.1,
        "professional": -0.15,
        "playful": +0.2,
        "serious": -0.1,
    }
    
    @classmethod
    def get_optimal_temperature(
        cls,
        model_name: str,
        task_type: TaskType,
        base_temperature: float = 0.7,
        user_instruction: str = "",
        user_creativity_preference: float = 0.0
    ) -> Tuple[float, str]:
        """
        Get optimal temperature for a specific model and task.
        
        Args:
            model_name: The model name (e.g., "gpt-4o-mini")
            task_type: The type of task being performed
            base_temperature: Fallback temperature from model config
            user_instruction: User's instruction text for intent detection
            user_creativity_preference: User's creativity adjustment (-0.3 to +0.3)
            
        Returns:
            Tuple of (optimized_temperature, explanation)
        """
        
        explanation_parts = []
        
        # Get model-specific temperature if available
        if model_name in cls.MODEL_TASK_TEMPERATURES:
            model_temps = cls.MODEL_TASK_TEMPERATURES[model_name]
            if task_type in model_temps:
                optimal_temp = model_temps[task_type]
                explanation_parts.append(f"Model-optimized for {task_type.value.replace('_', ' ')}")
            else:
                # Use default for this task type
                optimal_temp = cls.DEFAULT_TASK_TEMPERATURES.get(task_type, base_temperature)
                explanation_parts.append(f"Task-optimized for {task_type.value.replace('_', ' ')}")
        else:
            # Unknown model, use task-based default
            optimal_temp = cls.DEFAULT_TASK_TEMPERATURES.get(task_type, base_temperature)
            explanation_parts.append(f"Task-optimized for {task_type.value.replace('_', ' ')} (unknown model)")
        
        # Apply user intent modifiers from instruction text
        intent_adjustment = 0.0
        if user_instruction:
            instruction_lower = user_instruction.lower()
            applied_modifiers = []
            
            for keyword, modifier in cls.INTENT_MODIFIERS.items():
                if keyword in instruction_lower:
                    intent_adjustment += modifier
                    applied_modifiers.append(keyword)
            
            if applied_modifiers:
                explanation_parts.append(f"Intent: {', '.join(applied_modifiers)} ({intent_adjustment:+.1f})")
        
        # Apply user creativity preference
        if user_creativity_preference != 0.0:
            explanation_parts.append(f"User preference: {user_creativity_preference:+.1f}")
        
        # Calculate final temperature
        final_temp = optimal_temp + intent_adjustment + user_creativity_preference
        
        # Clamp to reasonable bounds
        final_temp = max(0.0, min(1.5, final_temp))
        final_temp = round(final_temp, 2)
        
        # Build explanation
        base_explanation = f"Base: {base_temperature} → Optimal: {final_temp}"
        if explanation_parts:
            full_explanation = f"{base_explanation} ({'; '.join(explanation_parts)})"
        else:
            full_explanation = base_explanation
        
        logger.info(f"Temperature optimization: {model_name} + {task_type.value} = {final_temp}")
        logger.debug(f"Temperature explanation: {full_explanation}")
        
        return final_temp, full_explanation
    
    @classmethod
    def detect_task_from_instruction(cls, instruction: str, context: str = "") -> TaskType:
        """
        Auto-detect task type from user instruction and context.
        
        Args:
            instruction: User's instruction text
            context: Additional context (e.g., current content, scene type)
            
        Returns:
            Detected task type
        """
        
        combined_text = f"{instruction} {context}".lower()
        
        # Task detection with prioritized keywords
        task_patterns = {
            TaskType.JSON_EXTRACTION: [
                "json", "metadata", "extract", "data", "structure", "parse"
            ],
            TaskType.CONTEXT_RETRIEVAL: [
                "search", "find", "retrieve", "context", "related", "similar"
            ],
            TaskType.DIALOGUE_WRITING: [
                "dialogue", "conversation", "talking", "speech", "said", "asked", 
                "replied", "character speaks", "conversation between"
            ],
            TaskType.CHARACTER_DEVELOPMENT: [
                "character", "personality", "motivation", "backstory", "traits",
                "behavior", "thoughts", "feelings", "internal"
            ],
            TaskType.WORLD_BUILDING: [
                "world", "setting", "environment", "location", "place", "landscape",
                "geography", "culture", "society", "history"
            ],
            TaskType.PLOT_PLANNING: [
                "plot", "structure", "outline", "plan", "story arc", "narrative structure",
                "sequence", "events", "timeline"
            ],
            TaskType.SCENE_WRITING: [
                "scene", "moment", "action", "happening", "event", "sequence"
            ],
            TaskType.ACT_WRITING: [
                "act", "chapter", "section", "part", "segment"
            ],
            TaskType.EDITING: [
                "edit", "revise", "fix", "correct", "improve", "polish", "refine"
            ],
            TaskType.BRAINSTORMING: [
                "brainstorm", "ideas", "possibilities", "options", "alternatives",
                "creative ideas", "think of", "come up with"
            ],
            TaskType.TECHNICAL_WRITING: [
                "technical", "explain", "how", "documentation", "instructions",
                "process", "method", "tutorial"
            ],
        }
        
        # Score each task type based on keyword matches
        task_scores = {}
        for task_type, keywords in task_patterns.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                task_scores[task_type] = score
        
        # Return highest scoring task, or default to creative writing
        if task_scores:
            best_task = max(task_scores.items(), key=lambda x: x[1])[0]
            logger.debug(f"Task detection: '{instruction[:50]}...' → {best_task.value}")
            return best_task
        else:
            logger.debug(f"Task detection: '{instruction[:50]}...' → creative_writing (default)")
            return TaskType.CREATIVE_WRITING
    
    @classmethod
    def optimize_for_writing_assistant(
        cls,
        model_name: str,
        user_instruction: str,
        base_temperature: float,
        current_content: str = "",
        generation_mode: str = "Continue/Append"
    ) -> Tuple[float, TaskType, str]:
        """
        Optimize temperature specifically for writing assistant use cases.
        
        Args:
            model_name: AI model name
            user_instruction: User's writing instruction
            base_temperature: Base temperature from model config
            current_content: Current scene/act content for context
            generation_mode: Writing mode (Continue/Append, Replace, etc.)
            
        Returns:
            Tuple of (optimized_temp, detected_task, explanation)
        """
        
        # Detect task type from instruction and content
        task_type = cls.detect_task_from_instruction(user_instruction, current_content)
        
        # Adjust for generation mode
        mode_adjustment = 0.0
        if generation_mode == "Replace":
            mode_adjustment = -0.1  # More conservative for replacements
        elif generation_mode == "Brainstorm":
            mode_adjustment = +0.2  # More creative for brainstorming
        
        # Get optimal temperature
        optimal_temp, explanation = cls.get_optimal_temperature(
            model_name=model_name,
            task_type=task_type,
            base_temperature=base_temperature,
            user_instruction=user_instruction,
            user_creativity_preference=mode_adjustment
        )
        
        return optimal_temp, task_type, explanation
    
    @classmethod
    def optimize_for_chat(
        cls,
        model_name: str,
        user_message: str,
        base_temperature: float,
        world_context: Optional[Dict] = None
    ) -> Tuple[float, str]:
        """
        Optimize temperature for chat/conversation use cases.
        
        Args:
            model_name: AI model name
            user_message: User's chat message
            base_temperature: Base temperature from model config
            world_context: World context if available
            
        Returns:
            Tuple of (optimized_temp, explanation)
        """
        
        # Detect if this is a creative or factual query
        creative_indicators = [
            "creative", "story", "imagine", "what if", "describe", "write"
        ]
        factual_indicators = [
            "what", "who", "when", "where", "how", "explain", "tell me about"
        ]
        
        message_lower = user_message.lower()
        creative_score = sum(1 for indicator in creative_indicators if indicator in message_lower)
        factual_score = sum(1 for indicator in factual_indicators if indicator in message_lower)
        
        # Determine task type for chat
        if creative_score > factual_score:
            task_type = TaskType.CREATIVE_WRITING
        else:
            task_type = TaskType.CHAT_CONVERSATION
        
        optimal_temp, explanation = cls.get_optimal_temperature(
            model_name=model_name,
            task_type=task_type,
            base_temperature=base_temperature,
            user_instruction=user_message
        )
        
        return optimal_temp, explanation

