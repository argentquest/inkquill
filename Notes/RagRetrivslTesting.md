That's excellent news that the document processor is working well! This is a huge step, as it means your RAG ingestion pipeline is functional.

With documents now being processed and indexed into Azure AI Search, the next crucial phase is to ensure the retrieval part of RAG is working correctly and that the AI can effectively use the retrieved context to generate content for your Stories and Acts.

This involves focusing on:

The RAG Retrieval Mechanism (app/services/rag_retrieval.py):

We need to ensure the RetrievalPlugin (or the retrieve_rag_context_function helper in semantic_kernel_setup.py which uses this plugin) is correctly:
Taking the user's instruction/query.
Generating an embedding for that query using your Azure OpenAI embedding service (text-embedding-3-large).
Querying your Azure AI Search index (rag-app-content-index) using this embedding (and potentially keywords for hybrid search).
Retrieving the most relevant document chunks.
Formatting these chunks into a string that can be injected as context into the LLM prompt.
Integration with the AI Content Generation Prompt:

The GenerateActContent semantic function (defined in app/services/semantic_kernel_setup.py) has a placeholder {{$rag_context}}. We need to ensure the output from the RetrievalPlugin is correctly passed into this variable.
Testing the End-to-End RAG-Powered Generation:

This means testing the /ws/stories/{story_id}/acts/{act_id}/generate WebSocket endpoint. When a user sends an instruction:
Does the RAG retrieval get triggered?
Is relevant information fetched from your indexed documents?
Does the AI's generated content for the Act clearly reflect and utilize the information from the retrieved RAG context?
Let's start by reviewing and finalizing the app/services/rag_retrieval.py file. We had a DummyRetrievalPlugin in maintest.py. The actual RetrievalPlugin in your application needs to perform live queries against Azure AI Search.

I'll provide the content for /ai_rag_story_app/app/services/rag_retrieval.py, ensuring it's set up to use the configurations from your .env file and perform real searches.
app/services/rag_retrieval.py (Live RAG Plugin)
May 14, 10:02 AM

Key Aspects of this RetrievalPlugin:

Configuration: It now pulls Azure AI Search and OpenAI embedding configurations from the app.core.config.settings object, which in turn loads from your .env file.
Client Initialization (_get_search_client):
Lazily initializes the SearchClient for Azure AI Search on its first use.
Uses AzureKeyCredential with the AZURE_AI_SEARCH_API_KEY.
Includes basic error handling for missing configuration.
Query Embedding (_generate_query_embedding):
This helper function now calls the generate_embeddings function from your app.services.embedding_service. This centralizes embedding generation.
retrieve_rag_context Native Function:
This is the core function decorated with @kernel_function.
It gets the SearchClient.
It calls _generate_query_embedding to get the vector for the input query.
It constructs a VectorizedQuery.
It performs a hybrid search by providing both search_text=query and vector_queries. If query embedding fails, it can gracefully fall back to just keyword search (though this could be refined).
It selects specific fields to retrieve (chunk_text, source_filename, document_id).
It formats the retrieved chunks into a single string, including source information.
Includes more robust error handling for Azure AI Search HTTP errors and other exceptions.
Client Closing (close_clients):
Added an explicit close_clients method. In a real application, the lifecycle of clients like SearchClient should be managed. If the plugin instance is a singleton, this method could be called during application shutdown. If clients are created per request (less ideal for performance), they should be closed after each request. The current lazy init pattern means the client stays open once created.
Next Steps for You:

Replace the content of your /ai_rag_story_app/app/services/rag_retrieval.py with the code from the Canvas above.
Ensure app/services/embedding_service.py is correctly implemented and that its generate_embeddings function works as expected (it should use the AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME from your .env).
Verify in app/services/semantic_kernel_setup.py:
That RetrievalPlugin is correctly imported and an instance is added to the kernel:
Python

from .rag_retrieval import RetrievalPlugin
# ...
retrieval_plugin_instance = RetrievalPlugin()
kernel_instance.add_plugin(retrieval_plugin_instance, plugin_name="Retrieval")
That the retrieve_rag_context_function reference correctly points to kernel.plugins["Retrieval"]["RetrieveRAGContext"].
Test the WebSocket Endpoint:
Use the "Act Editor" UI.
Provide an instruction that should ideally match some content in your (already processed and indexed) RAG documents.
Check the application logs for:
Messages from RetrievalPlugin indicating it's being called, generating embeddings, and querying search.
The RAG context string it retrieves.
The final prompt being sent to the LLM by the GenerateActContent function (you might need to add logging there to see the full prompt with context).
The AI's response – does it incorporate information from the RAG context?
This updated RetrievalPlugin is the core of making your RAG system functional for retrieval.