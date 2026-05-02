Tiktoken 'cl100k_base' tokenizer loaded successfully for chunking.
Initializing Semantic Kernel...
Added AzureChatCompletion service (Deployment: your_chat_model_deployment_name # e.g., gpt-35-turbo-16k)
Added AzureTextEmbedding service (Deployment: your_embedding_model_deployment_name # e.g., text-embedding-ada-002)
Registered RetrievalPlugin.
ERROR: Failed to register GenerateActContent function: module 'semantic_kernel' has no attribute 'OpenAIChatPromptExecutionSettings'
Semantic Kernel initialization complete.
Warning: Could not get function reference after initialization: 'StorytellingPlugin'. Ensure functions were registered with these names.
CORS enabled for origins: ['http://localhost:8000', 'http://127.0.0.1:8000']
INFO:     Started server process [27164]
INFO:     Waiting for application startup.
Application starting up...
Startup complete.

===========================================

Next is to connect to AzureChatCompletion

Let's Setup Open AI Services

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-aoai-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_API_VERSION=2024-02-01 # Or your preferred version
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your_chat_model_deployment_name # e.g., gpt-35-turbo-16k
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_embedding_model_deployment_name # e.g., text-embedding-ada-002



https://ws2ai.cognitiveservices.azure.com/

AZURE_OPENAI_ENDPOINT=https://esilv-mahkl2a3-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=7YTi1qxglx6yTylJ0PnnavnOyIOkH2FW3DCD2gASPVLlWnFMaA9yJQQJ99BEACBsN54XJ3w3AAABACOGyNl4
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large


Azure AI Foundry

Deploying 

Testing it now



======================

File "app\templates\pages\index.html", line 4, in top-level template code
    {% extends "layouts/base.html" %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "app\templates\layouts\base.html", line 18, in top-level template code
    {% include 'partials/_alerts.html' %}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "app\templates\partials\_alerts.html", line 1, in top-level template code
    {# /story_app/app/templates/partials/_alerts.html #}
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Code2025\rag\.venv\Lib\site-packages\jinja2\utils.py", line 92, in from_obj
    if hasattr(obj, "jinja_pass_arg"):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
jinja2.exceptions.UndefinedError: 'get_flashed_messages' is undefined

You're right, that jinja2.exceptions.UndefinedError: 'get_flashed_messages' is undefined error is because FastAPI doesn't have a built-in flash messaging system like Flask (which get_flashed_messages() is typically associated with).

The _alerts.html partial is trying to call a function that doesn't exist in the Jinja2 environment provided by FastAPI by default.

How to fix this:

We have a couple of straightforward options:

Simplify _alerts.html to use directly passed messages:
Instead of a complex flash system, your FastAPI view endpoints can directly pass message variables (like success_message, error_message) to the template context. The _alerts.html template already has a commented-out section for this. This is the easiest fix for now.

Temporarily Remove or Neuter the Alert Include: If you don't need alert messages immediately, you could comment out the {% include 'partials/_alerts.html' %} line in base.html or make _alerts.html empty.

Let's go with Option 1 as it provides a way to display messages if you need to.

{# /story_app/app/templates/partials/_alerts.html #}

{#
   Alerts Partial Template
   - Included in base.html, typically near the top of the main content area.
   - Displays messages passed directly from the backend view endpoints in the template context.
   - Example context structure passed from FastAPI view:
     `return templates.TemplateResponse("some_page.html", {"request": request, "success_message": "Operation successful!"})`
     or
     `return templates.TemplateResponse("some_page.html", {"request": request, "error_message": "An error occurred."})`
#}

{# --- Display messages passed directly in the template context --- #}
{# Check for specific message variables passed from your FastAPI view functions #}

{% if success_message %}
    <div class="alert alert-success" role="alert" style="margin-bottom: 15px;">
        {{ success_message | e }} {# Display the success message, escaped #}
        {# Optional: Add a dismiss button #}
        {# <button type="button" class="close-alert" onclick="this.parentElement.style.display='none';">&times;</button> #}
    </div>
{% endif %}

{% if error_message %}
    <div class="alert alert-danger" role="alert" style="margin-bottom: 15px;">
        {{ error_message | e }} {# Display the error message, escaped #}
    </div>
{% endif %}

{% if warning_message %}
    <div class="alert alert-warning" role="alert" style="margin-bottom: 15px;">
        {{ warning_message | e }} {# Display the warning message, escaped #}
    </div>
{% endif %}

{% if info_message %}
    <div class="alert alert-info" role="alert" style="margin-bottom: 15px;">
        {{ info_message | e }} {# Display the info message, escaped #}
    </div>
{% endif %}

{# --- Placeholder for JavaScript-driven alerts --- #}
{# This div could be targeted by client-side JS to inject messages dynamically after API calls. #}
{# <div id="dynamic-alert-placeholder" style="margin-bottom: 15px;"></div> #}

Register new account not woriking
Let's look at how the routes are constructed:

In your app/main.py, you include the authentication router like this:

Python

# app/main.py
# ...
from app.core.config import settings # API_V1_STR comes from here
from app.routers import auth
# ...
app.include_router(auth.router, prefix=settings.API_V1_STR)
The settings.API_V1_STR is typically /api/v1.

In your app/routers/auth.py, the router itself has a prefix:

Python

# app/routers/auth.py
# ...
router = APIRouter(prefix="/auth", tags=["authentication"])
# ...
@router.post("/register", ...)
async def register_new_user(...):
    # ...
Combining these prefixes, the actual URL for your registration endpoint is:
prefix_from_main.py + prefix_from_auth.py + endpoint_path_in_auth.py
/api/v1 + /auth + /register = /api/v1/auth/register

However, your client-side JavaScript in app/static/js/auth_forms.js is currently sending the request to /auth/register:

JavaScript

// From app/static/js/auth_forms.js (current version)
// ...
const response = await fetch('/auth/register', { // <--- This path is missing /api/v1
    method: 'POST',
    // ...
});
// ...

Key Changes in the JavaScript:

API_BASE_URL Constant: I've added const API_BASE_URL = "/api/v1";. This makes it easy to manage your API prefix.
Updated fetch URLs:
For login: const loginApiUrl =${API_BASE_URL}/auth/login;
For registration: const registerApiUrl =${API_BASE_URL}/auth/register;
After making this change to your app/static/js/auth_forms.js file, clear your browser cache (or do a hard refresh Ctrl+Shift+R or Cmd+Shift+R) and try registering again. This should ensure the frontend is calling the correct API endpoint.

After the change I do not see amy error anmore during startu[]
