import os
from openai import AzureOpenAI
from app.core.config import settings

endpoint = settings.AZURE_OPENAI_ENDPOINT
model_name = "gpt-4.1-mini"
deployment = settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT or "gpt-4o"

subscription_key = settings.AZURE_OPENAI_API_KEY
api_version = settings.AZURE_OPENAI_API_VERSION

if not endpoint or not subscription_key:
    raise ValueError("Azure OpenAI configuration missing. Please check your .env file.")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=str(endpoint),
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        }
    ],
    max_completion_tokens=settings.AI_MAX_TOKEN_SETTINGS.get("test", 800),
    temperature=settings.AI_TEMPERATURE_SETTINGS.get("test", 1.0),
    top_p=settings.AI_TOP_P_SETTINGS.get("test", 1.0),
    frequency_penalty=0.0,
    presence_penalty=0.0,
    model=deployment
)

print(response.choices[0].message.content)