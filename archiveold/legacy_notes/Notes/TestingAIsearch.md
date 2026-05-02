Created a Free AI Search Service

Using Free Services

Okay, I will add a test for the Azure AI Search service to the maintest_sk_logic.py script in the Canvas. This test will verify connectivity and check if the specified index exists by attempting to retrieve its statistics.

This is similar to the AI Search test we previously had in the maintest_infra_checks.py script.

I will update the maintest_sk_logic.py script in the Canvas.

Key Additions and Changes:

Imports for Azure AI Search:
Python

from azure.search.documents.indexes.aio import SearchIndexClient # To get index stats
from azure.core.credentials import AzureKeyCredential # For AI Search API Key
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError # For Azure SDK errors
Configuration Variables for AI Search: Added AZURE_AI_SEARCH_ENDPOINT, AZURE_AI_SEARCH_API_KEY, and AZURE_AI_SEARCH_INDEX_NAME to the configuration loading section at the top of the script.
Logging AI Search Config: Added these to print_sk_configuration().
New Test Function test_azure_ai_search_direct_connection():
Purpose: This async function tests connectivity to Azure AI Search.
Client Initialization: It uses SearchIndexClient with AzureKeyCredential (using AZURE_AI_SEARCH_API_KEY).
Operation: Calls search_index_client.get_index_statistics(name=AZURE_AI_SEARCH_INDEX_NAME). This is a good basic check as it verifies the endpoint, key, and that the specified index exists and is accessible.
Success/Failure Logging: Logs success and some basic stats (document count, storage size) or detailed error messages if the connection, authentication, or index retrieval fails. It specifically catches ResourceNotFoundError if the index doesn't exist and HttpResponseError for other Azure SDK HTTP issues.
Placeholder Check: Skips the test if essential AI Search configuration is using placeholder values.
Client Closing: Ensures the SearchIndexClient is closed in a finally block.
Call from main():
await test_azure_ai_search_direct_connection() is added to the sequence of tests in the main() async function, typically before initialize_kernel_for_sk_test(kernel).
Before Running:

Install/Update Azure AI Search SDK:
Bash

pip install "azure-search-documents>=11.4.0"
(Ensure you have a version that supports the async SearchIndexClient well; 11.4.0b8+ or stable 11.4+ is generally good).
Configure .env for Azure AI Search: Add or update these variables in your .env file (in the same directory as maintest_sk_logic.py):
Code snippet

AZURE_AI_SEARCH_ENDPOINT="https://your-search-service-name.search.windows.net"
AZURE_AI_SEARCH_API_KEY="your_search_service_admin_or_query_key" # Admin key needed to get stats usually
AZURE_AI_SEARCH_INDEX_NAME="rag-app-content-index" # The name of the index you defined
Index Must Exist: For the get_index_statistics call to succeed without a ResourceNotFoundError, the index (rag-app-content-index or whatever you named it) must already be created in your Azure AI Search service.
API Key Permissions: The API key used needs sufficient permissions to get index statistics. An admin key will definitely work. A query key might not.
This new test will help you verify that your environment can successfully connect to your Azure AI Search service and interact with the specified index.

dont we need to define the index first



Show thinking
You are absolutely right to ask that! Yes, for the test_azure_ai_search_direct_connection() function in maintest_sk_logic.py (Canvas &lt;doc id="maintest_sk_logic_py_v1"/>) to successfully get the index statistics, the Azure AI Search index (named by AZURE_AI_SEARCH_INDEX_NAME, defaulting to rag-app-content-index) must already exist in your Azure AI Search service.

The test script, as it's currently written, does not create the index. It only tries to connect to the service and retrieve statistics for an existing index.

Here's the workflow:

You (the developer) create the Azure AI Search index first:
This is a one-time setup step for your Azure AI Search service.
You would use the schema we defined previously (in the document &lt;doc id="azure_ai_search_schema_v1">Azure AI Search: Index Schema for Context&lt;/doc>) to create this index. You can do this through:
The Azure Portal.
The Azure AI Search SDKs (e.g., using SearchIndexClient from azure-search-documents in a separate Python script).
The Azure AI Search REST API.
Run maintest_sk_logic.py:
The test_azure_ai_search_direct_connection() function will then attempt to connect and call get_index_statistics().
If the index exists and your API key has permissions, this test will pass.
If the index does not exist, the test will fail with a ResourceNotFoundError, as noted in the try...except block of that test function.
So, to answer your question directly: yes, the index definition (schema creation) needs to happen before this specific test in maintest_sk_logic.py can pass by successfully retrieving statistics. The test itself is designed to verify connectivity to an existing, pre-defined index structure.

The actual populating of the index with data (chunks and embeddings) is handled by the document_processor.py in the main application, not by this standalone test script.

Okay, I will provide the schema for the Azure AI Search index again. This outlines the fields, their types, and configurations for your Context system.

Azure AI Search: Index Schema for Context Content
Objective:
This schema defines the structure for the Azure AI Search index that will store processed document chunks and their vector embeddings. This index is the backbone of the direct context assembly system, enabling efficient search and retrieval of relevant context to augment Large Language Model (LLM) prompts.

1. Index Naming:

Proposed Index Name: rag-app-content-index
2. Fields Definition:

id
Data Type (Edm): Edm.String
Attributes: Key, Retrievable, Filterable
Description: Primary Key. Unique identifier for each chunk (e.g., doc<DB_DOCUMENT_ID>_chunk<CHUNK_NUMBER>). Must be URL-safe.
document_id
Data Type (Edm): Edm.String
Attributes: Retrievable, Filterable, Sortable, Facetable
Description: ID of the original document from PostgreSQL UploadedDocument table. Links chunk to source.
user_id
Data Type (Edm): Edm.String
Attributes: Retrievable, Filterable, Facetable
Description: ID of the user who uploaded the document (for per-user Context).
source_filename
Data Type (Edm): Edm.String
Attributes: Retrievable, Filterable, Sortable
Description: Original filename (e.g., "project_brief.pdf").
chunk_text
Data Type (Edm): Edm.String
Attributes: Retrievable, Searchable
Description: Actual text content of the chunk. Used for keyword search.
chunk_text_vector
Data Type (Edm): Collection(Edm.Single)
Attributes: Retrievable, Searchable
Description: Vector Embedding. Stores the numerical vector representation of chunk_text (e.g., from text-embedding-ada-002 or text-embedding-3-large). Used for vector search.
page_number (Optional)
Data Type (Edm): Edm.Int32
Attributes: Retrievable, Filterable, Sortable, Facetable
Description: Original page number where the chunk originated (useful for PDFs).
uploaded_at
Data Type (Edm): Edm.DateTimeOffset
Attributes: Retrievable, Filterable, Sortable
Description: Timestamp (UTC) when the original document was uploaded.
tags (Optional)
Data Type (Edm): Collection(Edm.String)
Attributes: Retrievable, Filterable, Searchable, Facetable
Description: List of keywords/tags associated with the document/chunk.
processing_status (Optional)
Data Type (Edm): Edm.String
Attributes: Retrievable, Filterable, Facetable
Description: Status in the processing pipeline (e.g., "Processed").
3. Vector Search Profile / Configuration:

Defines how chunk_text_vector is searched.

Profile Name: default-hnsw-cosine-profile
Algorithm Configuration Name: default-hnsw-config
Kind: hnsw (Hierarchical Navigable Small Worlds).
HNSW Parameters:
m: 4 (Default)
efConstruction: 400 (Default - affects index build quality vs. time)
efSearch: 500 (Default - affects search speed vs. recall)
metric: cosine (Standard for text embeddings like text-embedding-ada-002 or text-embedding-3-large).
Dimensions: Must match your embedding model's output dimensions (e.g., 1536 for text-embedding-ada-002, or 3072 for text-embedding-3-large).
Vectorizer (Optional): Can define connection to Azure OpenAI embedding model (azureOpenAI kind).
Vectorizer Name: azure-openai-embedding-vectorizer
Kind: azureOpenAI
Azure OpenAI Parameters: resourceUri, deploymentId, apiKey (from Key Vault or MI), modelVersion.
4. Analyzers (for chunk_text):

Use standard.lucene (default) or a language-specific analyzer (e.g., en.microsoft) for keyword search processing.
5. Semantic Search Configuration (Recommended for Hybrid Search):

Improves hybrid search relevance.

Semantic Configuration Name: default-semantic-configuration
Title Field: source_filename
Content Fields: chunk_text
Keyword Fields: tags (if used)
Use queryType: 'semantic' when querying to enable semantic ranking.
6. Implementation Steps:

Provision Azure AI Search Service: Create an instance in Azure.
Create the Index: Define the index using this schema via Azure portal, SDKs, or REST API.
Configure Semantic Search: Enable and configure in the Azure portal if desired.

{
  "name": "rag-app-content-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "retrievable": true,
      "filterable": true,
      "sortable": false,
      "facetable": false,
      "searchable": false 
    },
    {
      "name": "document_id",
      "type": "Edm.String",
      "retrievable": true,
      "filterable": true,
      "sortable": true,
      "facetable": true,
      "searchable": false
    },
    {
      "name": "user_id",
      "type": "Edm.String",
      "retrievable": true,
      "filterable": true,
      "sortable": false,
      "facetable": true,
      "searchable": false
    },
    {
      "name": "source_filename",
      "type": "Edm.String",
      "retrievable": true,
      "filterable": true,
      "sortable": true,
      "facetable": false,
      "searchable": true,
      "analyzer": "standard.lucene"
    },
    {
      "name": "chunk_text",
      "type": "Edm.String",
      "retrievable": true,
      "filterable": false,
      "sortable": false,
      "facetable": false,
      "searchable": true,
      "analyzer": "standard.lucene" 
    },
    {
      "name": "chunk_text_vector",
      "type": "Collection(Edm.Single)",
      "retrievable": true,
      "searchable": true,
      "dimensions": 1536, 
      "vectorSearchProfile": "default-hnsw-cosine-profile"
    },
    {
      "name": "page_number",
      "type": "Edm.Int32",
      "retrievable": true,
      "filterable": true,
      "sortable": true,
      "facetable": true,
      "searchable": false
    },
    {
      "name": "uploaded_at",
      "type": "Edm.DateTimeOffset",
      "retrievable": true,
      "filterable": true,
      "sortable": true,
      "facetable": false,
      "searchable": false
    },
    {
      "name": "tags",
      "type": "Collection(Edm.String)",
      "retrievable": true,
      "filterable": true,
      "searchable": true,
      "facetable": true
    },
    {
      "name": "processing_status",
      "type": "Edm.String",
      "retrievable": true,
      "filterable": true,
      "facetable": true,
      "searchable": false
    }
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "default-hnsw-cosine-profile",
        "algorithm": "default-hnsw-config",
        "vectorizer": null // We are providing pre-computed embeddings
        // If using a service-side vectorizer, define it here and in the "vectorizers" section
        // "vectorizer": "azure-openai-embedding-vectorizer" 
      }
    ],
    "algorithms": [
      {
        "name": "default-hnsw-config",
        "kind": "hnsw",
        "hnswParameters": {
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500,
          "metric": "cosine"
        }
      }
    ]
    // "vectorizers": [ // Define if using a service-side vectorizer
    //   {
    //     "name": "azure-openai-embedding-vectorizer",
    //     "kind": "azureOpenAI",
    //     "azureOpenAIParameters": {
    //       "resourceUri": "YOUR_AZURE_OPENAI_ENDPOINT", 
    //       "deploymentId": "YOUR_EMBEDDING_MODEL_DEPLOYMENT_NAME", 
    //       "apiKey": null, // Use Managed Identity if possible, or set API key
    //       "authIdentity": null // Set to use Managed Identity if apiKey is null
    //     }
    //   }
    // ]
  },
  "semantic": {
    "configurations": [
      {
        "name": "default-semantic-configuration",
        "prioritizedFields": {
          "titleField": {
            "fieldName": "source_filename"
          },
          "prioritizedContentFields": [
            {
              "fieldName": "chunk_text"
            }
          ],
          "prioritizedKeywordsFields": [
            {
              "fieldName": "tags"
            }
          ]
        }
      }
    ]
  },
  "suggesters": [], // Add suggesters if needed for type-ahead suggestions
  "scoringProfiles": [], // Add custom scoring profiles if needed
  "analyzers": [], // Add custom analyzers if needed (beyond standard ones used in fields)
  "charFilters": [],
  "tokenFilters": [],
  "tokenizers": [],
  "corsOptions": null // Configure if direct browser access is needed
}

Key points in this JSON definition:

name: The name of your index (rag-app-content-index).
fields: An array defining each field in your index.
Each field has a name, type (Edm data type), and attributes like key, retrievable, filterable, searchable, sortable, facetable.
For chunk_text_vector, the type is Collection(Edm.Single), searchable is true, dimensions is set (e.g., 1536 for text-embedding-ada-002 or 3072 for text-embedding-3-large - you'll need to adjust this based on your chosen embedding model), and vectorSearchProfile links to the profile defined below.
searchable text fields like chunk_text and source_filename have analyzer: "standard.lucene" specified as an example. You can choose language-specific analyzers if needed.
vectorSearch: This section defines the vector search capabilities.
profiles: Defines named configurations for vector search. We have default-hnsw-cosine-profile.
algorithm: Links to an algorithm configuration (e.g., default-hnsw-config).
vectorizer: Set to null because we are providing pre-computed embeddings. If you were to use Azure AI Search's integrated vectorization, you would define a vectorizer here and in the vectorizers section.
algorithms: Defines the vector search algorithms. We use hnsw with specified parameters (m, efConstruction, efSearch, metric: "cosine").
vectorizers: Commented out, but this is where you'd define a connection to an embedding model (like Azure OpenAI) if you wanted Azure AI Search to generate embeddings for you from a text field.
semantic: Defines the semantic search configuration.
configurations: An array for semantic configurations. We've defined default-semantic-configuration using source_filename as the title field and chunk_text as a content field.
suggesters, scoringProfiles, analyzers, charFilters, tokenFilters, tokenizers, corsOptions: These are other standard parts of an index definition, left empty or null for now but can be configured if needed.
Important:

Dimensions: You must set the dimensions attribute in the chunk_text_vector field definition to match the output dimensionality of your chosen embedding model (e.g., 1536 for text-embedding-ada-002, 3072 for text-embedding-3-large). I've put 1536 as a placeholder.
Vectorizer Section: The vectorizers section within vectorSearch is commented out because our current plan is to generate embeddings in the document_processor.py and send them to Azure AI Search. If you wanted Azure AI Search to do the embedding for you (Integrated Vectorization), you would uncomment and configure this section.

Added the following JSON

{
    "name": "rag-app-content-index",
    "fields": [
        {
            "name": "id",
            "type": "Edm.String",
            "key": true,
            "retrievable": true,
            "filterable": true,
            "sortable": false,
            "facetable": false,
            "searchable": false
        },
        {
            "name": "document_id",
            "type": "Edm.String",
            "retrievable": true,
            "filterable": true,
            "sortable": true,
            "facetable": true,
            "searchable": false
        },
        {
            "name": "user_id",
            "type": "Edm.String",
            "retrievable": true,
            "filterable": true,
            "sortable": false,
            "facetable": true,
            "searchable": false
        },
        {
            "name": "source_filename",
            "type": "Edm.String",
            "retrievable": true,
            "filterable": true,
            "sortable": true,
            "facetable": false,
            "searchable": true,
            "analyzer": "standard.lucene"
        },
        {
            "name": "chunk_text",
            "type": "Edm.String",
            "retrievable": true,
            "filterable": false,
            "sortable": false,
            "facetable": false,
            "searchable": true,
            "analyzer": "standard.lucene"
        },
        {
            "name": "chunk_text_vector",
            "type": "Collection(Edm.Single)",
            "retrievable": true,
            "searchable": true,
            "dimensions": 1536,
            "vectorSearchProfile": "default-hnsw-cosine-profile"
        },
        {
            "name": "page_number",
            "type": "Edm.Int32",
            "retrievable": true,
            "filterable": true,
            "sortable": true,
            "facetable": true,
            "searchable": false
        },
        {
            "name": "uploaded_at",
            "type": "Edm.DateTimeOffset",
            "retrievable": true,
            "filterable": true,
            "sortable": true,
            "facetable": false,
            "searchable": false
        },
        {
            "name": "tags",
            "type": "Collection(Edm.String)",
            "retrievable": true,
            "filterable": true,
            "searchable": true,
            "facetable": true
        },
        {
            "name": "processing_status",
            "type": "Edm.String",
            "retrievable": true,
            "filterable": true,
            "facetable": true,
            "searchable": false
        }
    ],
    "vectorSearch": {
        "profiles": [
            {
                "name": "default-hnsw-cosine-profile",
                "algorithm": "default-hnsw-config",
                "vectorizer": null
            }
        ],
        "algorithms": [
            {
                "name": "default-hnsw-config",
                "kind": "hnsw",
                "hnswParameters": {
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            }
        ]
    },
    "semantic": {
        "configurations": [
            {
                "name": "default-semantic-configuration",
                "prioritizedFields": {
                    "titleField": {
                        "fieldName": "source_filename"
                    },
                    "prioritizedContentFields": [
                        {
                            "fieldName": "chunk_text"
                        }
                    ],
                    "prioritizedKeywordsFields": [
                        {
                            "fieldName": "tags"
                        }
                    ]
                }
            }
        ]
    },
    "suggesters": [],
    "scoringProfiles": [],
    "charFilters": [],
    "tokenFilters": [],
    "tokenizers": [],
    "corsOptions": null
}


Now we are going to test this

=====================


025-05-13 14:20:31,254 - INFO - Attempting to connect to Endpoint: https://wswriter.search.windows.net
2025-05-13 14:20:34,909 - INFO - Target Index Name: rag-app-content-index
2025-05-13 14:20:45,515 - INFO - Attempting to get statistics for index 'rag-app-content-index'...
2025-05-13 14:21:02,667 - ERROR - FAILURE: Error during get index statistics. Error: TypeError: SearchIndexClient.get_index_statistics() missing 1 required positional argument: 'index_name'


Okay, I see the TypeError in your logs for the test_get_index_statistics function:
TypeError: SearchIndexClient.get_index_statistics() missing 1 required positional argument: 'index_name'

This error message is quite specific. It indicates that the get_index_statistics method, as it's being found in your environment, expects an argument literally named index_name, and it's not receiving it in a way it recognizes (likely as the first positional argument after self, or as a keyword argument named index_name).

In the current code within the Canvas (test_ai_search_service_py_v1), the call is:

Python

index_stats = await search_index_client.get_index_statistics(name=AZURE_AI_SEARCH_INDEX_NAME)
The official Azure SDK documentation for recent versions of azure-search-documents (like 11.4.0+) specifies the parameter as name. However, the error message your Python environment is producing suggests it's looking for index_name.

This could be due to:

An older version of the azure-search-documents SDK being used in your virtual environment than expected, where the parameter name might have been different.
A very unusual local environment issue.
To directly address the error message, I will change the keyword argument in the call from name to index_name. This is a diagnostic step to see if it resolves the TypeError. If it does, it strongly points to an SDK version mismatch or an undocumented parameter name in the version you have.

I will now edit the test_ai_search_service.py script in the Canvas.

Key Change in the Canvas:

In the test_get_index_statistics function, the line:
Python

index_stats = await search_index_client.get_index_statistics(name=AZURE_AI_SEARCH_INDEX_NAME)
has been changed to:
Python

index_stats = await search_index_client.get_index_statistics(index_name=AZURE_AI_SEARCH_INDEX_NAME)
I've also added a specific except TypeError as te: block to catch this if it's still an issue and log a more targeted message.
Please try running test_ai_search_service.py again with this modification. If this resolves the TypeError, it suggests that the version of the azure-search-documents SDK in your environment expects index_name as the parameter name for this specific method, which is unusual for the documented recent versions but directly addresses the error message you received. If it still fails with a different error, or the same TypeError, we may need to investigate your installed SDK version more closely.


==========================

I think the index is empty 2025-05-13 14:28:01,899 - INFO - Attempting to get statistics for index 'rag-app-content-index'...

2025-05-13 14:28:23,804 - INFO - SUCCESS: Retrieved stats for index 'rag-app-content-index'.

2025-05-13 14:28:55,733 - ERROR - FAILURE: Error during get index statistics. Error: AttributeError: 'dict' object has no attribute 'document_count'




Show thinking




Okay, I see the problem in your logs for the test_ai_search_service.py script. The error AttributeError: 'dict' object has no attribute 'document_count' is occurring after the line "SUCCESS: Retrieved stats for index 'rag-app-content-index'."

This means that the index_stats object returned by await search_index_client.get_index_statistics(index_name=AZURE_AI_SEARCH_INDEX_NAME) is actually a dictionary (or a dictionary-like object where attributes are not directly accessible as object.attribute).

To fix this, we need to access the values using dictionary key notation, like index_stats['document_count'] or index_stats.get('document_count').

I will update the test_get_index_statistics function in the Canvas for test_ai_search_service.py to correctly access these values.

Key Changes in the Canvas (test_ai_search_service_py_v1):

In test_get_index_statistics():
The lines accessing index_stats.document_count and index_stats.storage_size have been changed to be more robust:
Python

doc_count = getattr(index_stats, 'document_count', index_stats.get('document_count', 'N/A') if isinstance(index_stats, dict) else 'N/A')
storage_size = getattr(index_stats, 'storage_size', index_stats.get('storage_size', 'N/A') if isinstance(index_stats, dict) else 'N/A')
This tries to access them as attributes first (getattr). If that fails (which it would if index_stats is a plain dict), it then tries to access them as dictionary keys (index_stats.get('document_count', 'N/A')).
Added a log message to print the raw index_stats object if direct attribute access fails, which will help you see its actual structure.
In test_ai_search_document_operations() for upload_results[0]:
Made error message extraction more robust by checking for error_message and error.message attributes.
Python

if not upload_results[0].succeeded:
    error_detail = upload_results[0].error_message if hasattr(upload_results[0], 'error_message') and upload_results[0].error_message else (upload_results[0].error.message if hasattr(upload_results[0], 'error') and upload_results[0].error else "Unknown upload error.")
    status_code_detail = f"(Status: {upload_results[0].status_code})" if hasattr(upload_results[0], 'status_code') and upload_results[0].status_code else ""
    raise Exception(f"Failed to upload test document '{upload_results[0].key}': {error_detail} {status_code_detail}")
This change should correctly handle the index_stats object whether it's a direct object with attributes or a dictionary-like structure, thus resolving the AttributeError.

===================

Exception has occurred: ImportError
cannot import name 'IndexStatistics' from 'azure.search.documents.indexes.models' (c:\Code2025\rag\.venv\Lib\site-packages\azure\search\documents\indexes\models\__init__.py)
  File "C:\Code2025\rag\app\test_ai_search_service.py", line 19, in <module>
    from azure.search.documents.indexes.models import IndexStatistics # To check type if needed
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ImportError: cannot import name 'IndexStatistics' from 'azure.search.documents.indexes.models' (c:\Code2025\rag\.venv\Lib\site-packages\azure\search\documents\indexes\models\__init__.py)



Okay, I see the ImportError: cannot import name 'IndexStatistics' from 'azure.search.documents.indexes.models'. This means that in the version of the azure-search-documents SDK you have installed, the IndexStatistics class is not available at that specific import path, or it might not be intended for direct import.

The good news is that the code in test_get_index_statistics() within the Canvas (test_ai_search_service_py_v1) is already designed to be somewhat flexible in how it accesses the document_count and storage_size from the index_stats object (using getattr and checking if it's a dict). The direct import of IndexStatistics was primarily for type hinting or an explicit type check, which isn't strictly necessary for the functionality.

To resolve this ImportError, we can simply remove the problematic import line. The rest of the logic should still function as intended.

I will update the test_ai_search_service.py script in the Canvas.

Key Change in the Canvas:

The line from azure.search.documents.indexes.models import IndexStatistics # To check type if needed has been removed from the top of the file.
The logic for accessing doc_count and storage_size in test_get_index_statistics was already designed to try getattr and then dict.get() if attribute access fails, so it should be resilient to index_stats being a dictionary-like object rather than a specific IndexStatistics class instance. I've slightly refined this access pattern for clarity:
Python

doc_count = getattr(index_stats, 'document_count', None)
if doc_count is None and isinstance(index_stats, dict): # Fallback for dict-like objects
    doc_count = index_stats.get('document_count', 'N/A')

storage_size = getattr(index_stats, 'storage_size', None)
if storage_size is None and isinstance(index_stats, dict): # Fallback for dict-like objects
    storage_size = index_stats.get('storage_size', 'N/A')
And added logging of the raw index_stats object and its type if these direct accesses fail, which will help in understanding the structure returned by your SDK version.
This change should prevent the ImportError. Please try running the script again.


==============================

Looks like the vector size is incorrect

2025-05-13 14:35:58,600 - INFO - Attempting to upload test document with id: maintest-doc-2ac5236f-ca78-452c-8d16-f159f0455599
2025-05-13 14:36:08,206 - ERROR - FAILURE: HTTP error during Azure AI Search document operations. Status: 400. Error: (OperationNotAllowed) The request is invalid. Details: actions : 0: There's a mismatch in vector dimensions. The vector field 'chunk_text_vector', with dimension of '1536', expects a length of '1536'. However, the provided vector has a length of '3072'. Please ensure that the vector length matches the expected length of the vector field. Read the following documentation for more details: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-configure-compression-storage.
Code: OperationNotAllowed
Message: The request is invalid. Details: actions : 0: There's a mismatch in vector dimensions. The vector field 'chunk_text_vector', with dimension of '1536', expects a length of '1536'. However, the provided vector has a length of '3072'. Please ensure that the vector length matches the expected length of the vector field. Read the following documentation for more details: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-configure-compression-storage.
Exception Details:      (IndexDocumentsFieldError) 0: There's a mismatch in vector dimensions. The vector field 'chunk_text_vector', with dimension of '1536', expects a length of '1536'. However, the provided vector has a length of '3072'. Please ensure that the vector length matches the expected length of the vector field. Read the following documentation for more details: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-configure-compression-storage. Parameters: actions
        Code: IndexDocumentsFieldError
        Message: 0: There's a mismatch in vector dimensions. The vector field 'chunk_text_vector', with dimension of '1536', expects a length of '1536'. However, the provided vector has a length of '3072'. Please ensure that the vector length matches the expected length of the vector field. Read the following documentation for more details: https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-configure-compression-storage. Parameters: actions
2025-05-13 14:36:13,324 - ERROR -    Reason: Bad Request
2025-05-13 14:36:17,441 - INFO - Attempting to delete test document: maintest-doc-2ac5236f-ca78-452c-8d16-f159f0455599
2025-05-13 14:36:17,731 - INFO - SUCCESS: Test document deleted from search index.
2025-05-13 14:36:17,731 - INFO - --- Document Operations Test Failed ---
2025-05-13 14:36:17,731 - INFO - test_ai_search_service.py script finished.
PS C:\Code2025\rag> 

The error message is very clear and points to a mismatch between your Azure AI Search index configuration and the data your test script (test_ai_search_service.py in the Canvas &lt;doc id="test_ai_search_service_py_v1"/>) is trying to send:

FAILURE: HTTP error during Azure AI Search document operations. Status: 400. Error: (OperationNotAllowed) The request is invalid. Details: actions : 0: There's a mismatch in vector dimensions. The vector field 'chunk_text_vector', with dimension of '1536', expects a length of '1536'. However, the provided vector has a length of '3072'.
Here's what's happening:

Your Azure AI Search Index (rag-app-content-index): The field named chunk_text_vector in this index is currently configured to expect vector embeddings that have 1536 dimensions. This is typical for older embedding models like text-embedding-ada-002.
Your Test Script (test_ai_search_service.py):
You have AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="text-embedding-3-large" in your .env file. This model produces embeddings with 3072 dimensions.
The script correctly sets EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "3072")). If EMBEDDING_DIMENSION is not in your .env, it defaults to 3072.
The dummy document it tries to upload creates a vector [0.01] * EMBEDDING_DIMENSION, which will therefore be a 3072-dimensional vector.
The Mismatch: The script is sending a 3072-dimension vector, but your Azure AI Search index is expecting a 1536-dimension vector for the chunk_text_vector field. This causes the "mismatch in vector dimensions" error.
How to Fix This:

You need to align the dimension expected by your Azure AI Search index with the dimension produced by your chosen embedding model (text-embedding-3-large, which is 3072).

The primary fix is to update your Azure AI Search index schema:

Go to the Azure Portal and navigate to your Azure AI Search service (wswriter.search.windows.net).
Find your index named rag-app-content-index.
Edit the index definition (schema). You need to find the field definition for chunk_text_vector.
Change the dimensions property of the chunk_text_vector field from 1536 to 3072.
If you used the JSON definition I provided earlier (&lt;doc id="azure_ai_search_schema_json_v1"/>), you would modify this part:
JSON

{
  "name": "chunk_text_vector",
  "type": "Collection(Edm.Single)",
  "retrievable": true,
  "searchable": true,
  "dimensions": 3072, // <<< CHANGE THIS FROM 1536 to 3072
  "vectorSearchProfile": "default-hnsw-cosine-profile"
}
Save the updated index definition.
Note: Changing the dimensions of an existing vector field might require you to re-index any existing data in that field. Since your index is likely empty or only has test data, this should be straightforward. If it has significant data, plan for re-indexing.
Once your Azure AI Search index is updated to expect 3072 dimensions for chunk_text_vector:

Ensure your .env file for test_ai_search_service.py has:
Code snippet

AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="text-embedding-3-large"
EMBEDDING_DIMENSION="3072" 
(The script already defaults EMBEDDING_DIMENSION to 3072 if not set, which is correct for text-embedding-3-large).
Re-run python test_ai_search_service.py.
The test_ai_search_document_operations() function should then be able to upload the dummy document successfully because the vector dimensions will match.

Note: I had to recreate the index by removing it first and use the revised JSON file


Good news it passed all of the test,  the test document was uploded, and delete but the azure portal document count did not show that there was a file.  Which is fine.


