# app/maintest_sk_logic.py (Enhanced for Dynamic Model Testing - v2)
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
    AzureChatPromptExecutionSettings
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
import os
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

from sqlalchemy.future import select
from app.db.database import async_session_local
from app.models.ai_model_config import AIModelConfiguration, AIProviderEnum, AIModelTypeEnum

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration Loading
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

db_loaded_models = {}

async def load_models_from_db():
    logger.info("\n--- Loading AI Model Configurations from Database ---")
    async with async_session_local() as db:
        result = await db.execute(
            select(AIModelConfiguration).filter_by(is_active=True, model_type=AIModelTypeEnum.GENERATION)
        )
        models = result.scalars().all()
    
    for model in models:
        db_loaded_models[model.id] = model
        logger.info(f"Loaded model config: ID={model.id}, Name='{model.display_name}', Model='{model.model_name}'")
    logger.info("--- Finished loading model configurations ---")


async def initialize_kernel_dynamically(kernel_instance: sk.Kernel) -> bool:
    logger.info("\n--- Dynamically Initializing Semantic Kernel ---")
    if not db_loaded_models:
        logger.error("No models were loaded from the database. Cannot initialize kernel.")
        return False

    registered_deployments = set()
    for config in db_loaded_models.values():
        if config.model_name not in registered_deployments and config.provider == AIProviderEnum.AZURE:
            try:
                service_id = config.model_name
                deployment_name = config.model_name
                kernel_instance.add_service(
                    AzureChatCompletion(
                        service_id=service_id,
                        deployment_name=deployment_name,
                        endpoint=AZURE_OPENAI_ENDPOINT,
                        api_key=AZURE_OPENAI_API_KEY,
                        api_version=AZURE_OPENAI_API_VERSION,
                    )
                )
                registered_deployments.add(deployment_name)
                logger.info(f"SUCCESS: Added AzureChatCompletion service for '{deployment_name}' with service_id '{service_id}'")
            except Exception as e:
                logger.error(f"ERROR adding service for model '{config.model_name}': {e}", exc_info=True)
    
    # --- FIX: Modify prompt to handle JSON mode conditionally ---
    prompt = """
    Write a single, very short, and dramatic sentence about a {{$topic}}. 
    {{$json_instruction}}
    """
    prompt_config = sk.prompt_template.PromptTemplateConfig(
        template=prompt, name="ShortSentence", template_format="semantic-kernel"
    )
    kernel_instance.add_function(
        function_name="ShortSentence", plugin_name="TestPlugin", prompt_template_config=prompt_config
    )
    logger.info("--- Kernel initialization complete ---")
    return True

async def main():
    logger.info("Starting maintest_sk_logic.py (Dynamic Test)...")
    await load_models_from_db()

    kernel = sk.Kernel()
    is_initialized = await initialize_kernel_dynamically(kernel)
    if not is_initialized:
        logger.critical("Aborting test due to kernel initialization failure.")
        return

    test_function = kernel.plugins.get("TestPlugin", {}).get("ShortSentence")
    if not test_function:
        logger.error("ShortSentence function not found in TestPlugin. Aborting.")
        return

    logger.info("\n--- Testing Each Loaded Generative Model Configuration ---")
    
    for config_id, config in db_loaded_models.items():
        logger.info(f"\n--- Testing Config ID: {config_id}, Name: '{config.display_name}' ---")
        
        try:
            # --- FIX: Conditionally set response_format and json_instruction ---
            response_format_value = None
            json_instruction_value = ""
            if config.is_json_mode:
                response_format_value = {"type": "json_object"}
                json_instruction_value = "Your output must be a valid JSON object with a single key 'sentence' containing the dramatic sentence."
            
            exec_settings = AzureChatPromptExecutionSettings(
                service_id=config.model_name,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                top_p=config.top_p,
                presence_penalty=config.presence_penalty,
                frequency_penalty=config.frequency_penalty,
                response_format=response_format_value, # Use the conditional value
            )
            
            args = KernelArguments(
                topic="dragon's final breath", 
                json_instruction=json_instruction_value, # Pass the conditional instruction
                settings=exec_settings
            )
            # --- END FIX ---
            
            result = await kernel.invoke(test_function, arguments=args)
            logger.info(f"  > SUCCESS: AI Response: {result}")
            
        except Exception as e:
            logger.error(f"  > FAILED: Error invoking config '{config.display_name}': {e}", exc_info=True)

    logger.info("\n--- Dynamic model test script finished. ---")


if __name__ == "__main__":
    asyncio.run(main())