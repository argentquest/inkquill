That's excellent! It sounds like the core functionality for managing stories, acts, and the AI-assisted writing (including Context and prompt selection) is now in a good state.

Now that these foundational pieces are working, here are a few suggestions for what you could consider next to improve and expand your "AI Storytelling Assistant" concept. I'll try to offer a mix of UI/UX enhancements, AI interaction improvements, and content organization ideas:

1. Implement a Rich Text Editor for Act Content:

Current State: The Act.description (main content) is likely edited in a plain <textarea> on the "Act Editor" page.
Suggestion: Integrate a web-based WYSIWYG (What You See Is What You Get) HTML editor like TinyMCE, CKEditor 5, or Quill.js.
Benefits:
Allows users to format their act content with bold, italics, lists, headings, etc., making their narratives more structured and readable.
Provides a more professional and user-friendly writing experience.
Implementation Sketch:
Include the chosen editor's JS/CSS in base.html or act_editor_ui.html.
Initialize the editor on the <textarea id="act-content-editor">.
Update act_editor.js to get HTML content from the editor's API when saving (editor.getContent()) and send this HTML string to your backend.
Ensure your Act.description database column (which is Text) can store HTML.
Crucially: Sanitize any HTML on the backend with a library like Bleach before displaying it outside the editor to prevent XSS attacks.
2. Enhance Context Interaction: Display Retrieved Context:

Current State: The Context context is fetched by the backend and injected into the LLM prompt, but the user doesn't directly see what information was retrieved.
Suggestion: On the "Act Editor" page, after the user provides an instruction and before (or alongside) the AI generates content, display the top 2-3 snippets of text that the context system assembled from uploaded documents and story data.
Benefits:
Transparency: Users understand what information the AI is basing its generation on.
Control & Iteration: If the assembled context is irrelevant or not what the user intended, they can rephrase their instruction to guide the context assembly better before the LLM generates a potentially off-target response.
Trust: Builds trust in the AI's output by showing its "sources."
Implementation Sketch:
The WebSocket endpoint (ai_assisted_writing.py) would first call the retrieve_context_context_function.
It would send a distinct WebSocket message to the client containing these retrieved snippets (e.g., {"type": "context_context", "data": ["snippet1...", "snippet2..."]}).
act_editor.js would listen for this message type and display the snippets in a dedicated div on the page.
The backend would then proceed to call the generate_act_content_function with this same Context context.
3. Advanced Prompt Management & Usage:

A. Display Active System Prompt on Act Editor:
Current State: An Act can have a system_prompt_id.
Suggestion: On the "Act Editor" page, clearly display the title (and maybe a snippet) of the currently associated system prompt for that Act. This reminds the user of the overarching guidance the AI is receiving for that specific act.
Implementation: The act_editor_ui view in views.py already fetches and passes the act object which can have its system_prompt relationship eager-loaded. The Jinja2 template can then display act.system_prompt.title.
B. Expand "Select a saved prompt" Dropdown:
Current State: The dropdown in the Act Editor likely shows only the user's "my-prompts."
Suggestion: Allow this dropdown to also list relevant shared or public prompts (e.g., prompts of type ACT, SCENE_GENERATION, or GENERAL that are marked as active and perhaps globally available or shared by other users if you implement sharing).
Implementation:
The populatePromptDropdown function in act_editor.js would need to call an API endpoint that returns both user-specific and relevant shared prompts.
Your /api/v1/prompts/ router could have a new endpoint or modify the existing /shared endpoint to better suit this.
C. "Quick Use" for Prompts in Prompt Library:
Suggestion: On the prompt_list.html page, next to each prompt, add a "Use for new Act instruction" button. Clicking this could:
Navigate to the "Act Editor" for a selected (or new) Act.
Pre-fill the "Your Instruction for the AI" textarea with the content of the chosen prompt.
Implementation: This would involve some client-side JavaScript on prompt_list.html to handle the button click, potentially storing the prompt content in localStorage or passing it via query parameters to the Act Editor URL.
4. Character/Persona Integration (Building on previous thoughts):

Current State: We have a Persona model defined.
Suggestion:
Implement the UI for creating and managing Personas (similar to what you did for Prompts).
Allow linking Personas to a Story (e.g., a list of main characters for that story).
On the "Act Editor" page, display the Personas associated with the current Story.
Modify the GenerateActContent prompt template and the KernelArguments in ai_assisted_writing.py to include information about these "active" Personas (e.g., their names, key traits from Persona.description or a new Persona.summary field).
Benefits: The AI can then generate content that is more consistent with the defined characters, use their names correctly, and reflect their personalities.
These are a few directions you could take. I'd recommend picking one or two that you feel would add the most value or are most interesting to you right now. For example, implementing the Rich Text Editor and displaying assembled document context would be significant UX and AI interaction improvements.



Updated Priority List & Development Plan - AI Storytelling Assistant
(Assuming the NameError in semantic_kernel_setup.py and the subsequent Pydantic ValidationError for input_variables are now resolved by using input_variables=[] or None for PromptTemplateConfig and defining plugin name constants globally in semantic_kernel_setup.py.)
I. Current High Priority - Stabilize Core AI Functionality
Goal: Ensure AI Act Review Feature is Fully Functional (Backend & Frontend Integration)
Current Status:
Frontend (act_ai_review_page.html and act_ai_review_page.js) is set up to display Act content (read-only Quill) and make an API call to /api/v1/acts/{act_id}/trigger-ai-review.
Backend (app/routers/act.py) is receiving the request but currently returns a 503 because the review_act_content_function (pointing to ReviewActContentEnhanced) is None.
app/services/semantic_kernel_setup.py was recently updated to fix PydanticValidationError by using input_variables=[] for ReviewActContentEnhanced.
The enhanced_act_review_prompt.txt was updated to require a root JSON object with "suggestions": [] and "metrics": {}.
Task: Resolve "AI Review SK function not available" (503 Error).
Explanation: The immediate goal is to ensure that the ReviewActContentEnhanced Semantic Kernel function is correctly registered during application startup and is accessible to the API endpoint in app/routers/act.py. This involves verifying that no errors occur during its registration in semantic_kernel_setup.py and that the exported variable review_act_content_function correctly holds the function reference.
Next Actions:
Thoroughly examine application startup logs for any errors or warnings specifically from semantic_kernel_setup.py related to the registration of ReviewActContentEnhanced or the StoryAnalysisPlugin. Pay attention to the DEBUG SK_SETUP: print statements.
If registration errors persist, double-check the PromptTemplateConfig for ReviewActContentEnhanced (template name, function name, plugin name consistency) and ensure the AzureChatCompletion service it depends on is successfully added to the kernel.
Task: Ensure Backend API Correctly Parses LLM JSON and Returns Structured Response.
Explanation: Once the SK function is callable, the backend API endpoint (trigger_ai_review_for_act_content_api) must correctly invoke it, receive the JSON string from the LLM, parse it into a Python dictionary (expecting {"suggestions": [], "metrics": {}}), and then serialize this structure (e.g., using the ActAIReviewResponse Pydantic model) back to the frontend.
Next Actions:
Implement robust parsing of the LLM's JSON response in the API endpoint.
Add detailed logging of the raw LLM output and the parsed Python objects in the backend.
Ensure the API returns the data in the format expected by the frontend (i.e., the ActAIReviewResponse schema).
Task: Ensure Frontend Correctly Renders Suggestions and New Metrics.
Explanation: The act_ai_review_page.js needs to correctly fetch the API response, parse the suggestions array and the metrics object, and then dynamically render both into their respective sections on the act_ai_review.html page.
Next Actions:
Verify the fetchAIReviewSuggestions function in act_ai_review_page.js correctly handles the {suggestions: [], metrics: {}} structure.
Implement or verify the renderMetrics JavaScript function to display the metrics data.
Test the UI thoroughly to ensure both suggestions and metrics are displayed clearly.
Labels: priority:critical, feature:ai-review, bug, area:backend, area:frontend, area:ai-rag
II. Medium Priority - Refactoring & Enhancements
Task: Refactor semantic_kernel_setup.py into Smaller, Modular Plugin Setup Files.
Explanation: The current semantic_kernel_setup.py is becoming large as it registers all Semantic Kernel functions for various features (Act writing, Scene writing, Context text generation for world elements, world import, AI review, etc.). Breaking this down will improve code organization, readability, and maintainability. The goal is to have a core file that initializes the kernel and its AI services (AzureChatCompletion, AzureTextEmbedding), and then separate Python files for each logical "plugin" (e.g., Storytelling, StoryAnalysis, WorldBuilding) that are responsible for loading their specific prompts and registering their functions with the shared kernel instance.
Proposed Structure (Example):
app/services/sk_kernel_instance.py: Initializes sk.Kernel(), adds Azure AI services.
app/services/sk_plugins/story_analysis_plugin_setup.py: Loads enhanced_act_review_prompt.txt, registers ReviewActContentEnhanced function.
app/services/sk_plugins/storytelling_plugin_setup.py: Registers functions for narrative generation.
And so on for other groups of functions.
Benefits: Easier to find specific function definitions, manage prompts, and reduces the chance of conflicts or overly complex single files.
Next Actions (After AI Review is stable):
Create sk_kernel_instance.py and the sk_plugins directory structure.
Migrate the registration logic for one plugin's worth of functions at a time (e.g., start with all functions in StoryAnalysisPlugin).
Update sk_kernel_instance.py to call the registration function from the new plugin setup file.
Adapt routers/services that use these SK functions to get their references from the central kernel instance (e.g., kernel.plugins.get("StoryAnalysisPlugin").get("ReviewActContentEnhanced")) or via a consolidated export from sk_kernel_instance.py.
Test thoroughly after each plugin migration.
Labels: priority:medium, refactor, area:backend, area:ai-rag, maintainability
Task: Complete Context Population for AI Review Prompt.
Explanation: The enhanced_act_review_prompt.txt includes placeholders like {{$previous_acts_summaries}} and {{$linked_story_elements_context}}. The backend API endpoint needs to be fully implemented to fetch and correctly format this data from the database to provide the richest possible context to the AI coach.
Next Actions:
In app/routers/act.py (or your AI review endpoint), implement the logic to query the database for previous act summaries and linked characters/locations/lore for the current story.
Format this data into clear, concise strings suitable for inclusion in the LLM prompt.
Pass these formatted strings to the KernelArguments when invoking the review_act_content_function.
Labels: priority:medium, feature:ai-review, area:backend, area:ai-rag
Task: Stabilize and Test Act Editor & Scene Editor AI Interactions.
Explanation: Ensure the WebSocket-based AI assistance for generating/editing Act narrative (ai_assisted_writing.py) and Scene narrative/metadata (ai_scene_writing.py) is robust, handles streaming correctly, and integrates well with their respective SK functions. This includes verifying the two-call approach for Scenes (narrative then metadata).
Next Actions: Systematic testing of all AI interaction flows in the Act and Scene editors.
Labels: priority:medium, feature:ai-writing, area:backend, area:frontend, area:ai-rag
(Other medium and low priority items from your "May22OutstandingIssues.md" would follow here, re-prioritized as needed after the above are stable.)
Summary of "What We Are Trying To Do":
AI Review Feature:
Goal: Provide users with structured, actionable feedback from an AI on their Act content. This feedback should include qualitative suggestions categorized by writing aspects (pacing, character, etc.) and quantitative metrics.
Mechanism:
A user navigates to an "AI Review" page for a specific Act.
The Act's current narrative content is displayed (read-only using Quill).
The user clicks a button ("Get AI Review Suggestions").
The frontend (act_ai_review_page.js) calls a backend API endpoint.
The backend API endpoint (app/routers/act.py) gathers all necessary context (story details, act details, previous acts, linked world elements, and the act's narrative content).
It invokes a Semantic Kernel function (ReviewActContentEnhanced) which uses a detailed system prompt (enhanced_act_review_prompt.txt) to instruct an LLM (Azure OpenAI) to analyze the Act content and context.
The LLM is instructed to return its feedback as a single JSON object containing two main keys: a suggestions array (each item being a feedback object with id, category, suggestion_text, etc.) and a metrics object (containing ratings and justifications for various writing quality aspects).
The backend parses this JSON response and sends it back to the frontend.
The frontend JavaScript (act_ai_review_page.js) receives this structured data and dynamically renders the suggestions and metrics on the page for the user.
Semantic Kernel Breakdown (Refactor):
Goal: Improve the organization and maintainability of the Semantic Kernel setup code.
Current Problem: app/services/semantic_kernel_setup.py is becoming a single large file containing the registration logic for all Semantic Kernel functions used across the application.
Proposed Solution:
Create a central file (app/services/sk_kernel_instance.py) that is responsible only for creating the main sk.Kernel() instance and adding the core AI services (like AzureChatCompletion from Azure OpenAI).
Create a new sub-directory, e.g., app/services/sk_plugins/.
Within this directory, create separate Python files for each logical grouping of semantic functions (a "plugin"). For example:
story_analysis_plugin_setup.py would handle loading prompts and registering functions related to analyzing content (like ReviewActContentEnhanced, GenerateActMetadata).
storytelling_plugin_setup.py would handle functions for generating narrative content.
...and so on for other categories like world building, scene extraction, etc.
Each of these plugin setup files would define a function (e.g., register_story_analysis_functions(kernel, chat_service_id)) that takes the kernel instance and necessary service IDs as input and adds its specific functions to that kernel.
The main sk_kernel_instance.py would import these registration functions and call them to populate the kernel.
Routers and other services that need to invoke SK functions would then get them from the globally initialized kernel instance by their plugin name and function name (e.g., kernel.plugins["StoryAnalysisPlugin"]["ReviewActContentEnhanced"]).
This refactoring will make the SK setup cleaner, easier to manage as you add more AI capabilities, and individual plugin setups more isolated.
This updated list and explanation should provide a clear path forward. The immediate next step is to get those startup logs for semantic_kernel_setup.py to ensure ReviewActContentEnhanced is being registered correctly.

