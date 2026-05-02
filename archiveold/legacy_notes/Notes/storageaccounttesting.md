Okay, I will add a new test to the maintest.py script in the Canvas to verify connectivity to your Azure Storage Account. This test will attempt to list the containers in the storage account, which is a good basic check.

Key Additions and Changes:

Imports for Azure Storage:
Python

from azure.storage.blob.aio import BlobServiceClient # For Azure Storage test
from azure.identity.aio import DefaultAzureCredential # For potential MI auth to storage
Configuration Variables for Storage: Added AZURE_STOContextE_CONNECTION_STRING and AZURE_STOContextE_ACCOUNT_NAME to the configuration loading section, with appropriate placeholder defaults.
Python

# Azure Storage Configuration
AZURE_STOContextE_CONNECTION_STRING = os.getenv("AZURE_STOContextE_CONNECTION_STRING", "STOContextE_CONNECTION_STRING_NOT_SET")
AZURE_STOContextE_ACCOUNT_NAME = os.getenv("AZURE_STOContextE_ACCOUNT_NAME", "STOContextE_ACCOUNT_NAME_NOT_SET")
Logging Storage Config: Added these to print_loaded_configuration().
test_azure_storage_connection() Async Function:
This new function is added.
It checks if placeholder values are being used for storage configuration and skips the test if so.
It attempts to initialize BlobServiceClient using either:
The connection string (if AZURE_STOContextE_CONNECTION_STRING is set and not a placeholder).
The account name with DefaultAzureCredential() (if AZURE_STOContextE_ACCOUNT_NAME is set and not a placeholder, and connection string isn't). This allows testing Managed Identity scenarios if you're running this script from an Azure environment with MI configured, or using local Azure CLI login.
If client initialization is successful, it attempts to list the containers in the storage account (blob_service_client.list_containers()).
It logs success if it can list containers (or if no containers are found, which is still a successful connection).
It logs detailed errors and troubleshooting tips if the connection or listing fails.
Ensures the BlobServiceClient and DefaultAzureCredential (if used) are closed in a finally block.
Call from main_test_logic():
await test_azure_storage_connection() is added to the sequence of tests in main_test_logic(), typically after the database and OpenAI tests.
To Use This New Test:

Ensure Azure Storage SDK is Installed: If not already included by other dependencies, you might need to add azure-storage-blob with async support to your environment where maintest.py runs:
Bash

pip install "azure-storage-blob[aio]" azure-identity
(The azure-identity is for DefaultAzureCredential).
Configure .env File: Add or update these variables in your .env file (in the same directory as maintest.py):
Option 1 (Connection String):
Code snippet

AZURE_STOContextE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=yourstorageaccount;AccountKey=YOUR_ACCOUNT_KEY;EndpointSuffix=core.windows.net"
# AZURE_STOContextE_ACCOUNT_NAME="yourstorageaccount" # Optional if using connection string
Option 2 (Account Name for Managed Identity / DefaultAzureCredential):
Code snippet

# AZURE_STOContextE_CONNECTION_STRING="" # Leave blank or omit if using MI
AZURE_STOContextE_ACCOUNT_NAME="yourstorageaccount"
If using this method locally, ensure you are logged in via Azure CLI (az login) with an account that has at least "Storage Blob Data Reader" or "Reader" permissions on the storage account.
Run the script: python maintest.py
The output will now include a section for the Azure Storage connection test.

sw2storystorage is storage account

Creating a blob container

created a container called stories

using access key for now

P575lgqdcsNdb9vZLqm6PGPUfPvLLg1PpvpM0mWJnVpToI7nMUJLM/gZMQzCMnBvS4qEySYcT3uI+AStflAqfA==

DefaultEndpointsProtocol=https;AccountName=sw2storystorage;AccountKey=P575lgqdcsNdb9vZLqm6PGPUfPvLLg1PpvpM0mWJnVpToI7nMUJLM/gZMQzCMnBvS4qEySYcT3uI+AStflAqfA==;EndpointSuffix=core.windows.net

It means we've successfully configured it to:

Load environment variables correctly.
Test password hashing.
Verify the database connection.
Test the Azure Storage Account operations (upload, read, delete).
Test the direct Azure OpenAI embedding service.
Initialize Semantic Kernel with the correct Azure OpenAI service configurations (chat and embedding).
And finally, successfully invoke a Semantic Kernel function that calls the Azure OpenAI chat completion service!
This is a huge step forward, as it validates all your core service connections and configurations in a standalone environment.

What would you like to work on next? We can:

Move on to implementing the actual application code, like the document_processor.py for the Context pipeline.
Start writing the pytest test files for the main application.
Review or refine any other part of the application design.
Look into any remaining files from the project structure.



