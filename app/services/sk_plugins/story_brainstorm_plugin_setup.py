"""
Story Brainstorm Plugin Setup for Semantic Kernel

This module registers the story brainstorm functions with the Semantic Kernel.
"""

from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Plugin name constant
STORY_BRAINSTORM_PLUGIN_NAME = "StoryBrainstormPlugin"


def setup_story_brainstorm_plugin(kernel_instance, chat_service_id: str):
    """Register story brainstorm functions with the kernel"""
    
    # Load prompt templates
    import os
    prompts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'prompts', 'system')
    
    # Load story concepts generation prompt
    concepts_prompt_file = os.path.join(prompts_dir, 'story_concepts_generation.txt')
    with open(concepts_prompt_file, 'r', encoding='utf-8') as f:
        STORY_CONCEPTS_PROMPT = f.read()
    
    # Load three-act structure generation prompt
    three_acts_prompt_file = os.path.join(prompts_dir, 'three_act_structure_generation.txt')
    with open(three_acts_prompt_file, 'r', encoding='utf-8') as f:
        THREE_ACTS_PROMPT = f.read()
    
    # Setup execution settings
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
    
    # Story concepts generation function
    try:
        concepts_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id,
            ai_model_id=settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT,
            max_tokens=4000,
            temperature=0.8,
            top_p=0.9
        )
        
        concepts_prompt_config = PromptTemplateConfig(
            template=STORY_CONCEPTS_PROMPT,
            name="GenerateStoryConcepts",
            template_format="semantic-kernel",
            description="Generate 15 unique story concepts based on user preferences",
            execution_settings={chat_service_id: concepts_exec_settings}
        )
        
        kernel_instance.add_function(
            function_name="GenerateStoryConcepts",
            plugin_name=STORY_BRAINSTORM_PLUGIN_NAME,
            prompt_template_config=concepts_prompt_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORY_BRAINSTORM_PLUGIN_NAME}): Registered GenerateStoryConcepts.")
    except Exception as e:
        logger.error(f"SK_PLUGIN_SETUP ({STORY_BRAINSTORM_PLUGIN_NAME}): ERROR registering GenerateStoryConcepts: {e}", exc_info=True)
    
    # Three-act structure generation function
    try:
        three_acts_exec_settings = OpenAIChatPromptExecutionSettings(
            service_id=chat_service_id,
            ai_model_id=settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT,
            max_tokens=2000,
            temperature=0.7,
            top_p=0.8
        )
        
        three_acts_prompt_config = PromptTemplateConfig(
            template=THREE_ACTS_PROMPT,
            name="GenerateThreeActStructure",
            template_format="semantic-kernel", 
            description="Generate detailed three-act story structure",
            execution_settings={chat_service_id: three_acts_exec_settings}
        )
        
        kernel_instance.add_function(
            function_name="GenerateThreeActStructure",
            plugin_name=STORY_BRAINSTORM_PLUGIN_NAME,
            prompt_template_config=three_acts_prompt_config
        )
        logger.info(f"SK_PLUGIN_SETUP ({STORY_BRAINSTORM_PLUGIN_NAME}): Registered GenerateThreeActStructure.")
    except Exception as e:
        logger.error(f"SK_PLUGIN_SETUP ({STORY_BRAINSTORM_PLUGIN_NAME}): ERROR registering GenerateThreeActStructure: {e}", exc_info=True)