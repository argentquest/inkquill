We are done with the front end for the db

Next we will work on the Context portion


in the maintest.py 2025-05-10 15:00:10,266 - INFO -

--- Attempting Example SK Invocation (Live Azure Call for Chat) ---

2025-05-10 15:00:10,266 - ERROR -

ERROR during SK invocation: module 'semantic_kernel' has no attribute 'KernelArguments'

2025-05-10 15:00:10,266 - INFO - maintest.py script finished.

You're right, that error AttributeError: module 'semantic_kernel' has no attribute 'KernelArguments' indicates that KernelArguments is not directly accessible as sk.KernelArguments in the version of the Semantic Kernel Python SDK you are using.

In recent versions of the Semantic Kernel v1.x Python SDK, KernelArguments is typically found in semantic_kernel.functions.kernel_arguments.

I will update the maintest.py script in the Canvas to:

Correctly import KernelArguments.

==============================


 temperature=0.7, top_p=0.8, user=None, store=None, metadata=None, response_format=None, function_call=None, functions=None, messages=None, parallel_tool_calls=None, tools=None, tool_choice=None, structured_json_response=False, stream_options=None, max_completion_tokens=None, reasoning_effort=None, extra_body=None)}, function_choice_behavior=None)}
2025-05-10 15:03:03,196 - INFO -
--- Attempting Example SK Invocation (Live Azure Call for Chat) ---
2025-05-10 15:03:03,196 - INFO - [DummyRetrievalPlugin] Called with query: 'About the woods...', top_k: 1
2025-05-10 15:03:03,196 - INFO - Dummy Context Result: Simulated Context context for query 'About the woods'. Found 1 dummy chunks.
2025-05-10 15:03:03,196 - INFO - Streaming chat response:
Function failed. Error: ("<class 'semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion.AzureChatCompletion'> service failed to complete the prompt", AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}"))
2025-05-10 15:03:03,425 - ERROR - 
ERROR during SK invocation: ("<class 'semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion.AzureChatCompletion'> service failed to complete the prompt", AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}"))
2025-05-10 15:03:03,425 - INFO - maintest.py script finished.
PS C:\Code2025\rag> 

I think there is an issue with my open ai connection

The error message you're seeing is very specific and points directly to an issue with the Azure OpenAI credentials or configuration being used by the maintest.py script for the chat completion service:

AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}")
This 401 Access denied error means that when Semantic Kernel (via the AzureChatCompletion connector) tried to contact your Azure OpenAI service using the provided details, the service rejected the request due to an authentication failure.

The maintest.py script attempts to load the following environment variables (from your .env file or system environment) for Azure OpenAI:

AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION (defaults to "2024-02-01" in the script if not set)
CHAT_DEPLOYMENT_NAME (this is your specific model deployment name for the chat model)
The script did attempt the live call, which means it didn't detect purely placeholder values for these. However, the values it used were still incorrect or invalid for your Azure OpenAI service.

Here's what you need to meticulously check and verify:

Open your .env file (the one in the same directory as maintest.py, if you are using one) or check the environment variables in the shell where you are running python maintest.py.

Verify AZURE_OPENAI_ENDPOINT:

Go to the Azure portal, navigate to your Azure OpenAI resource.
Under "Keys and Endpoint", copy the Endpoint value exactly. It should look something like https://your-resource-name.openai.azure.com/.
Ensure this matches the value in your .env file or environment variable.
Verify AZURE_OPENAI_API_KEY:

In the same "Keys and Endpoint" section in the Azure portal, copy either KEY 1 or KEY 2.
Ensure this matches the value for AZURE_OPENAI_API_KEY exactly. There should be no extra characters or spaces.
Verify CHAT_DEPLOYMENT_NAME:

In Azure OpenAI Studio, go to "Deployments" (or "Management" -> "Deployments").
Find the Deployment name for your chat model (e.g., gpt-35-turbo, gpt-4, or whatever you named it). This is case-sensitive.
Ensure this exact name is used for the AZURE_OPENAI_CHAT_DEPLOYMENT_NAME variable.
Verify AZURE_OPENAI_API_VERSION:

The script defaults to 2024-02-01. This is a generally compatible recent version. However, ensure your Azure OpenAI resource supports this API version. You can check the Azure OpenAI documentation for supported API versions if you suspect an issue here, but the endpoint/key/deployment name are more common culprits for a 401.
Common Mistakes:

Typos: Even a small typo in the endpoint, key, or deployment name will cause a 401 error.
Extra Spaces: Leading or trailing spaces in the values in your .env file.
Wrong Key/Endpoint: Using a key from a different Azure OpenAI resource or an endpoint for a different service.
Incorrect Deployment Name: The deployment name must be exactly as it appears in Azure OpenAI Studio.
Subscription Issues: Ensure your Azure subscription is active and has no billing issues.
Region: While the error message mentions "wrong API endpoint" which could imply a regional mismatch, the primary check is the full endpoint URL. Ensure you're using the endpoint for the region where your Azure OpenAI resource is deployed.
Debugging Steps:

Focus on the .env file: If you are using a .env file with maintest.py (because of load_dotenv()), this is the most likely place for the incorrect values.
Print values carefully: The print_loaded_configuration() function in maintest.py masks parts of the API key and password. For your own local, temporary debugging, you could briefly modify it to print the full AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY (be very careful with this output and remove it immediately after checking), and CHAT_DEPLOYMENT_NAME just before the kernel_instance.add_service(AzureChatCompletion(...)) call to be absolutely sure what values are being passed to the SDK. Do not commit code that prints full API keys.
Test with a simple REST client: Use a tool like Postman or curl to make a basic API call to your Azure OpenAI endpoint with the key and deployment name to see if you get a successful response outside of the Python script. This can help isolate whether the issue is with the credentials themselves or how they are being used in the script.
The problem is almost certainly one of the configuration values being passed to the AzureChatCompletion service in initialize_kernel_for_test

We are still havibg issue with open ai

Added MainOpenAiTest.py and it connects properly


We are still having failire on endbedding

Microsoft Code Failed

import os
from openai import AzureOpenAI

endpoint = "https://esilv-mahkl2a3-eastus2.cognitiveservices.azure.com/"
model_name = "text-embedding-3-large"
deployment = "text-embedding-3-large"

api_version = "2024-02-01"

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    endpoint=endpoint,
    credential=AzureKeyCredential("<API_KEY>")
)

response = client.embeddings.create(
    input=["first phrase","second phrase","third phrase"],
    model=deployment
)

for item in response.data:
    length = len(item.embedding)
    print(
        f"data[{item.index}]: length={length}, "
        f"[{item.embedding[0]}, {item.embedding[1]}, "
        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
    )
print(response.usage)

Gemini to the Rescue

You're encountering that TypeError: AzureOpenAI.__init__() got an unexpected keyword argument 'endpoint' because the AzureOpenAI client from the openai library expects the endpoint URL to be passed as the azure_endpoint parameter, not just endpoint.

In your mainTestEmbedding.py script, you have:

Python

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    endpoint=endpoint, # <--- This is the argument causing the error
    credential=AzureKeyCredential("...")
)
To fix this, change endpoint=endpoint to azure_endpoint=endpoint:

import os
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential # Make sure this is imported

endpoint = "https://esilv-mahkl2a3-eastus2.cognitiveservices.azure.com/"
# model_name = "text-embedding-3-large" # Not used directly in client constructor
deployment = "text-embedding-3-large" # This is your deployment ID for the embedding model

# It seems you defined api_version twice, the one used by the client is what matters
# api_version_defined_earlier = "2024-02-01" # This one is not used in the client call

client = AzureOpenAI(
    api_version="2024-12-01-preview", # This is the API version used by the client
    azure_endpoint=endpoint,       # <<< CORRECTED HERE
    api_key="3nIVVI86djAEsg6nH50R5zYMIRnnLgJ1imYDl9PrdZiFMLyvOrSQJQQJ99BEACHYHv6XJ3w3AAAAACOGcrHI" # Use api_key directly
    # credential=AzureKeyCredential("...") # Using api_key is more common for AzureOpenAI,
                                         # but credential should also work if api_key is removed.
                                         # Let's stick to api_key for simplicity as in most examples.
)

response = client.embeddings.create(
    input=["first phrase","second phrase","third phrase"],
    model=deployment # This should be your embedding model's deployment name
)

for item in response.data:
    length = len(item.embedding)
    print(
        f"data[{item.index}]: length={length}, "
        f"[{item.embedding[0]}, {item.embedding[1]}, "
        f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
    )
print(response.usage)


So embedding model works fine!

TypeError: AzureOpenAI.__init__() got an unexpected keyword argument 'endpoint'
PS C:\Code2025\rag> & c:/Code2025/rag/.venv/Scripts/python.exe c:/Code2025/rag/app/mainTestEmbedding.py
data[0]: length=3072, [0.022330209612846375, -0.002088305074721575, ..., -0.014379994943737984, 0.006100048776715994]
data[1]: length=3072, [0.011640272103250027, 0.005252661183476448, ..., -0.028720801696181297, -0.0025770869106054306]
data[2]: length=3072, [0.016326788812875748, -0.0018455119570717216, ..., -0.005349587649106979, 0.006049444433301687]

Let's go back to MainTest

Streaming chat response:

Function failed. Error: ("<class 'semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion.AzureChatCompletion'> service failed to complete the prompt", AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}"))

2025-05-10 16:02:19,244 - ERROR - 

ERROR during SK invocation: ("<class 'semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion.AzureChatCompletion'> service failed to complete the prompt", AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}"))

2025-05-10 16:02:19,244 - INFO - maintest.py script finished.

Streaming chat response:

Function failed. Error: ("<class 'semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion.AzureChatCompletion'> service failed to complete the prompt", AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}"))

2025-05-10 16:02:19,244 - ERROR - 

ERROR during SK invocation: ("<class 'semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion.AzureChatCompletion'> service failed to complete the prompt", AuthenticationError("Error code: 401 - {'error': {'code': '401', 'message': 'Access denied due to invalid subscription key or wrong API endpoint. Make sure to provide a valid key for an active subscription and use a correct regional API endpoint for your resource.'}}"))

2025-05-10 16:02:19,244 - INFO - maintest.py script finished.


===================

   return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Python311\Lib\asyncio\base_events.py", line 653, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "c:\Code2025\rag\app\maintest.py", line 325, in main_test_logic
    chat_service_available = kernel.get_service(SK_TEST_CHAT_DEPLOYMENT_NAME, type=AzureChatCompletion) is not None # Check by deployment name or service_id
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Code2025\rag\.venv\Lib\site-packages\semantic_kernel\services\kernel_services_extension.py", line 106, in get_service
    raise KernelServiceNotFoundError(
semantic_kernel.exceptions.kernel_exceptions.KernelServiceNotFoundError: Service with service_id 'gpt-4.1-mini-2' does not exist or has a different type.
PS C:\Code2025\rag>

ou've pinpointed the issue precisely! The error semantic_kernel.exceptions.kernel_exceptions.KernelServiceNotFoundError: Service with service_id 'gpt-4.1-mini-2' does not exist or has a different type is very clear.

It's happening because this line in maintest.py:

Python

chat_service_available = kernel.get_service(SK_TEST_CHAT_DEPLOYMENT_NAME, type=AzureChatCompletion) is not None
is trying to retrieve a service using the deployment name (SK_TEST_CHAT_DEPLOYMENT_NAME, which is "gpt-4.1-mini-2") as the service_id.

However, when you added the service to the kernel, you used a different service_id:

Python

# In initialize_kernel_for_test:
chat_service_id = "azure_openai_chat_test_hardcoded"
# ...
kernel_instance.add_service(
    AzureChatCompletion(
        service_id=chat_service_id,  # This is "azure_openai_chat_test_hardcoded"
        deployment_name=SK_TEST_CHAT_DEPLOYMENT_NAME, # This is "gpt-4.1-mini-2"
        # ... other params
    )
)
To fix this, you need to use the actual service_id that was used during registration when calling kernel.get_service().

I will update the maintest.py script in the Canvas to use the correct service_id.

Key Changes:

Define SK_CHAT_SERVICE_ID and SK_EMBEDDING_SERVICE_ID: At the top, near the other configuration variables, I've added:
Python

# Define service IDs used for SK registration
SK_CHAT_SERVICE_ID = "azure_openai_chat_test_hardcoded"
SK_EMBEDDING_SERVICE_ID = "azure_openai_embedding_test_hardcoded"
Use Defined Service IDs in initialize_kernel_for_test: When adding services to the kernel, these constants are now used:
Python

# In initialize_kernel_for_test:
# ...
kernel_instance.add_service(
    AzureChatCompletion(
        service_id=SK_CHAT_SERVICE_ID, 
        # ...
    )
)
# ...
kernel_instance.add_service(
    AzureTextEmbedding(
        service_id=SK_EMBEDDING_SERVICE_ID, 
        # ...
    )
)
# ...
exec_settings = AzureChatPromptExecutionSettings(
    service_id=SK_CHAT_SERVICE_ID, # Also use it here for execution settings
    # ...
)
Corrected kernel.get_service Call: In main_test_logic, the check for service availability now uses the correct service_id:
Python

chat_service_available = False
try:
    # Use the SERVICE_ID used during registration
    if kernel.get_service(SK_CHAT_SERVICE_ID, type=AzureChatCompletion): 
        chat_service_available = True
        logger.info(f"Chat service '{SK_CHAT_SERVICE_ID}' found in kernel.")
except Exception as e:
    logger.warning(f"Chat service '{SK_CHAT_SERVICE_ID}' not found or error checking: {e}")
With these changes, kernel.get_service() is now looking for the service using the ID it was registered with ("azure_openai_chat_test_hardcoded"), which should resolve the KernelServiceNotFoundError.




