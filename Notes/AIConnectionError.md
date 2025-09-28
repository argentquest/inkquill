RROR: Failed to register GenerateActContent function: module 'semantic_kernel' has no attribute 'OpenAIChatPromptExecutionSettings'

Semantic Kernel initialization complete.

Warning: Could not get function reference after initialization: 'StorytellingPlugin'. Ensure functions were registered with these names.

BTW the app still start as I can show the friont end

Okay, I see the error messages. The main issue is:
AttributeError: module 'semantic_kernel' has no attribute 'OpenAIChatPromptExecutionSettings'

This means that OpenAIChatPromptExecutionSettings is not the correct way to access or define execution settings for your chat completion service with the version of Semantic Kernel you are using. The subsequent warning about not finding 'StorytellingPlugin' is likely because the function registration failed due to this initial error.

For Azure OpenAI chat completions with Semantic Kernel (especially recent versions of the v1.x Python SDK), the execution settings class is typically specific to the Azure connector. It's often AzureChatPromptExecutionSettings or found within semantic_kernel.connectors.ai.open_ai or semantic_kernel.connectors.ai.

Let's correct this in your /ai_rag_story_app/app/services/semantic_kernel_setup.py file. I'll assume the correct class is AzureChatPromptExecutionSettings from semantic_kernel.connectors.ai.open_ai.

I will provide the updated content for that file.

Import AzureChatPromptExecutionSettings:
Python

from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion,
    AzureTextEmbedding,
    AzureChatPromptExecutionSettings # <<< CORRECTED
)
Use AzureChatPromptExecutionSettings: When defining execution_settings for the GenerateActContent semantic function, we now use the correct class:
Python

execution_settings = AzureChatPromptExecutionSettings(
    service_id=chat_service_id, # Ensure this matches the service_id used for AzureChatCompletion
    max_tokens=2000,
    temperature=0.7,
    top_p=0.8,
)
Service ID Consistency: I've explicitly defined chat_service_id = "azure_openai_chat" and used it both when adding the AzureChatCompletion service and in the AzureChatPromptExecutionSettings. This is crucial for Semantic Kernel to know which configured AI service to use for that specific function.
Function Reference Retrieval: Updated the "Export References" section to more robustly check if the plugins and functions exist before trying to assign them. This will help pinpoint if the registration itself failed.
Please replace the content of your /ai_rag_story_app/app/services/semantic_kernel_setup.py with this corrected version. After saving, try running your application again: