#!/usr/bin/env python3
"""
Script to query and clean up Azure AI Search service documents.
- Finds documents where world_id is not set
- Finds documents with world_id that don't exist in the database
- Optionally deletes orphaned documents
"""

import asyncio
import os
import sys
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.services.azure_ai_search_service import AzureAISearchService
from app.db.database import async_session_local
from app.crud import world as crud_world
from app.models.world import World
from sqlalchemy.future import select


async def get_valid_world_ids() -> Set[str]:
    """
    Get all valid world IDs from the database.
    
    Returns:
        Set of valid world IDs as strings
    """
    print("Fetching valid world IDs from database...")
    
    async with async_session_local() as db:
        try:
            # Get all worlds from database directly using SQLAlchemy
            result = await db.execute(select(World))
            worlds = result.scalars().all()
            world_ids = {str(world.id) for world in worlds}
            
            print(f"Found {len(world_ids)} valid world IDs in database")
            return world_ids
            
        except Exception as e:
            print(f"Error fetching world IDs from database: {e}")
            raise


async def query_documents_with_invalid_world_id(valid_world_ids: Set[str]) -> List[Dict[str, Any]]:
    """
    Query Azure AI Search for documents with world_id that don't exist in the database.
    
    Args:
        valid_world_ids: Set of valid world IDs from database
        
    Returns:
        List of documents with invalid world_id
    """
    print(f"Searching for documents with invalid world_id...")
    print(f"Valid world IDs: {len(valid_world_ids)} total")
    print("-" * 60)
    
    # Initialize the search service
    search_service = AzureAISearchService(
        endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT),
        api_key=settings.AZURE_AI_SEARCH_API_KEY,
        index_name=settings.AZURE_AI_SEARCH_INDEX_NAME
    )
    
    if not search_service.search_client:
        raise RuntimeError("Failed to initialize Azure AI Search client")
    
    try:
        # First, get all documents that have a world_id set (not null/empty)
        search_filter = "(world_id ne null) and (world_id ne '')"
        
        print(f"Search filter for documents with world_id: {search_filter}")
        
        documents_with_world_id = await search_service.perform_search_async(
            query_text="*",
            top_k=10000,  # Large number to get all documents
            filter=search_filter,
            select=["id", "document_id", "user_id", "source_filename", "uploaded_at", "world_id", "element_type", "source_element_id"]
        )
        
        print(f"Found {len(documents_with_world_id)} documents with world_id set")
        
        # Filter for documents with invalid world_id
        invalid_documents = []
        for doc in documents_with_world_id:
            world_id = doc.get('world_id')
            if world_id and str(world_id) not in valid_world_ids:
                invalid_documents.append(doc)
        
        print(f"Found {len(invalid_documents)} documents with invalid world_id")
        return invalid_documents
        
    except Exception as e:
        print(f"Error querying search service: {e}")
        raise
    finally:
        # Close the search service connections
        if search_service and search_service.search_client:
            await search_service.close_async_clients()


async def query_documents_without_world_id() -> List[Dict[str, Any]]:
    """
    Query Azure AI Search for documents where world_id is null, empty, or not set.
    
    Returns:
        List of documents without world_id
    """
    print(f"Connecting to Azure AI Search: {settings.AZURE_AI_SEARCH_ENDPOINT}")
    print(f"Index: {settings.AZURE_AI_SEARCH_INDEX_NAME}")
    print("-" * 60)
    
    # Initialize the search service
    search_service = AzureAISearchService(
        endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT),
        api_key=settings.AZURE_AI_SEARCH_API_KEY,
        index_name=settings.AZURE_AI_SEARCH_INDEX_NAME
    )
    
    if not search_service.search_client:
        raise RuntimeError("Failed to initialize Azure AI Search client")
    
    # Query for documents without world_id
    # This searches for documents where world_id is null, empty, or missing
    search_filter = "(world_id eq null) or (world_id eq '') or not (world_id ne null)"
    
    print(f"Search filter: {search_filter}")
    print("-" * 60)
    
    try:
        # Perform the search with a filter using the correct method
        documents = await search_service.perform_search_async(
            query_text="*",  # Match all documents
            top_k=1000,  # Adjust this limit as needed
            filter=search_filter,
            select=["id", "document_id", "user_id", "source_filename", "uploaded_at", "world_id", "element_type", "source_element_id"]
        )
        
        return documents
        
    except Exception as e:
        print(f"Error querying search service: {e}")
        raise
    finally:
        # Close the search service connections
        if search_service and search_service.search_client:
            await search_service.close_async_clients()


async def delete_documents_by_ids(document_ids: List[str], description: str) -> bool:
    """
    Delete documents from Azure AI Search by their IDs.
    
    Args:
        document_ids: List of document IDs to delete
        description: Description of what's being deleted (for logging)
        
    Returns:
        True if all deletions succeeded, False otherwise
    """
    if not document_ids:
        print(f"No {description} to delete.")
        return True
    
    print(f"Deleting {len(document_ids)} {description}...")
    
    # Initialize the search service
    search_service = AzureAISearchService(
        endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT),
        api_key=settings.AZURE_AI_SEARCH_API_KEY,
        index_name=settings.AZURE_AI_SEARCH_INDEX_NAME
    )
    
    if not search_service.search_client:
        raise RuntimeError("Failed to initialize Azure AI Search client for deletion")
    
    try:
        # Prepare documents for deletion (need to specify the key field)
        documents_to_delete = [{"id": doc_id} for doc_id in document_ids]
        
        # Use the search client's delete_documents method
        delete_results = await search_service.search_client.delete_documents(documents=documents_to_delete)
        
        # Check results
        success_count = 0
        for i, result in enumerate(delete_results):
            if result.succeeded:
                success_count += 1
            else:
                error_msg = getattr(result.error, 'message', "Unknown error") if result.error else "Unknown error"
                print(f"  Failed to delete document '{document_ids[i]}': {error_msg}")
        
        print(f"Successfully deleted {success_count}/{len(document_ids)} {description}")
        return success_count == len(document_ids)
        
    except Exception as e:
        print(f"Error deleting {description}: {e}")
        return False
    finally:
        # Close the search service connections
        if search_service and search_service.search_client:
            await search_service.close_async_clients()


async def confirm_deletion(documents: List[Dict[str, Any]], description: str) -> bool:
    """
    Ask user for confirmation before deleting documents.
    
    Args:
        documents: List of documents to delete
        description: Description of what's being deleted
        
    Returns:
        True if user confirms deletion, False otherwise
    """
    if not documents:
        return False
    
    print(f"\n⚠️  DELETION CONFIRMATION")
    print(f"You are about to delete {len(documents)} {description}")
    print("This action cannot be undone!")
    print("\nDocuments to be deleted:")
    
    for doc in documents[:10]:  # Show first 10 for confirmation
        world_id = doc.get('world_id', 'N/A')
        filename = doc.get('source_filename', 'N/A')
        doc_id = doc.get('id', 'N/A')
        print(f"  - {doc_id} (world_id: {world_id}, file: {filename})")
    
    if len(documents) > 10:
        print(f"  ... and {len(documents) - 10} more documents")
    
    while True:
        response = input(f"\nConfirm deletion of {len(documents)} {description}? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please answer 'yes' or 'no'")


async def display_results(documents: List[Dict[str, Any]], title: str = "Documents") -> None:
    """
    Display the search results in a formatted way.
    
    Args:
        documents: List of documents to display
        title: Title for the results section
    """
    if not documents:
        print(f"✅ No {title.lower()} found!")
        return
    
    print(f"Found {len(documents)} {title.lower()}:")
    print("=" * 80)
    
    # Group by element_type for better organization
    by_type = {}
    for doc in documents:
        element_type = doc.get('element_type', 'unknown')
        if element_type not in by_type:
            by_type[element_type] = []
        by_type[element_type].append(doc)
    
    for element_type, docs in by_type.items():
        print(f"\n📁 Element Type: {element_type.upper()} ({len(docs)} documents)")
        print("-" * 60)
        
        for doc in docs:
            print(f"  ID: {doc.get('id', 'N/A')}")
            print(f"  Document ID: {doc.get('document_id', 'N/A')}")
            print(f"  User ID: {doc.get('user_id', 'N/A')}")
            print(f"  Filename: {doc.get('source_filename', 'N/A')}")
            print(f"  Uploaded: {doc.get('uploaded_at', 'N/A')}")
            print(f"  World ID: {doc.get('world_id', 'NULL/EMPTY')}")
            print(f"  Source Element ID: {doc.get('source_element_id', 'N/A')}")
            print()


async def count_total_documents() -> int:
    """
    Get the total count of documents in the search index for comparison.
    
    Returns:
        Total number of documents in the index
    """
    search_service = AzureAISearchService(
        endpoint=str(settings.AZURE_AI_SEARCH_ENDPOINT),
        api_key=settings.AZURE_AI_SEARCH_API_KEY,
        index_name=settings.AZURE_AI_SEARCH_INDEX_NAME
    )
    
    try:
        # Search for all documents to get count
        documents = await search_service.perform_search_async(
            query_text="*",
            top_k=10000,  # Large number to get all documents for counting
            select=["id"]
        )
        
        # Return the count of documents
        return len(documents)
        
    except Exception as e:
        print(f"Error counting total documents: {e}")
        return -1
    finally:
        # Close the search service connections
        if search_service and search_service.search_client:
            await search_service.close_async_clients()


async def main():
    """Main function to run the query and optionally clean up orphaned documents."""
    print("Azure AI Search - Document Cleanup Tool")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Parse command line arguments for delete mode
    delete_mode = "--delete" in sys.argv or "-d" in sys.argv
    if delete_mode:
        print("🗑️  DELETE MODE ENABLED - Will prompt for deletion of orphaned documents")
    else:
        print("🔍 QUERY MODE - Will only display results (use --delete to enable deletion)")
    print()
    
    try:
        # Verify configuration
        if not settings.AZURE_AI_SEARCH_ENDPOINT:
            print("❌ ERROR: AZURE_AI_SEARCH_ENDPOINT not configured")
            return
        
        if not settings.AZURE_AI_SEARCH_API_KEY:
            print("❌ ERROR: AZURE_AI_SEARCH_API_KEY not configured")
            return
        
        if not settings.AZURE_AI_SEARCH_INDEX_NAME:
            print("❌ ERROR: AZURE_AI_SEARCH_INDEX_NAME not configured")
            return
        
        # Get total document count for context
        print("Getting total document count...")
        total_docs = await count_total_documents()
        if total_docs >= 0:
            print(f"Total documents in index: {total_docs}")
        print()
        
        # Get valid world IDs from database
        valid_world_ids = await get_valid_world_ids()
        print()
        
        # Query for documents without world_id
        print("Searching for documents without world_id...")
        documents_without_world = await query_documents_without_world_id()
        print()
        
        # Query for documents with invalid world_id
        print("Searching for documents with invalid world_id...")
        documents_with_invalid_world = await query_documents_with_invalid_world_id(valid_world_ids)
        print()
        
        # Display results
        print("RESULTS:")
        print("=" * 80)
        
        print("\n1️⃣ DOCUMENTS WITHOUT WORLD_ID:")
        await display_results(documents_without_world, "documents without world_id")
        
        print("\n2️⃣ DOCUMENTS WITH INVALID WORLD_ID:")
        await display_results(documents_with_invalid_world, "documents with invalid world_id")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY:")
        if total_docs >= 0:
            print(f"  Total documents in index: {total_docs}")
        print(f"  Valid world IDs in database: {len(valid_world_ids)}")
        print(f"  Documents without world_id: {len(documents_without_world)}")
        print(f"  Documents with invalid world_id: {len(documents_with_invalid_world)}")
        
        total_orphaned = len(documents_without_world) + len(documents_with_invalid_world)
        if total_docs > 0:
            percentage = (total_orphaned / total_docs) * 100
            print(f"  Total orphaned documents: {total_orphaned} ({percentage:.1f}%)")
        
        # Handle deletion if in delete mode
        if delete_mode and total_orphaned > 0:
            print("\n🗑️  DELETION OPTIONS:")
            print("-" * 40)
            
            # Handle documents with invalid world_id
            if documents_with_invalid_world:
                print(f"\nFound {len(documents_with_invalid_world)} documents with invalid world_id")
                if await confirm_deletion(documents_with_invalid_world, "documents with invalid world_id"):
                    document_ids = [doc['id'] for doc in documents_with_invalid_world]
                    success = await delete_documents_by_ids(document_ids, "documents with invalid world_id")
                    if success:
                        print("✅ Successfully deleted documents with invalid world_id")
                    else:
                        print("❌ Some deletions failed")
                else:
                    print("❌ Deletion cancelled for documents with invalid world_id")
            
            # Handle documents without world_id
            if documents_without_world:
                print(f"\nFound {len(documents_without_world)} documents without world_id")
                if await confirm_deletion(documents_without_world, "documents without world_id"):
                    document_ids = [doc['id'] for doc in documents_without_world]
                    success = await delete_documents_by_ids(document_ids, "documents without world_id")
                    if success:
                        print("✅ Successfully deleted documents without world_id")
                    else:
                        print("❌ Some deletions failed")
                else:
                    print("❌ Deletion cancelled for documents without world_id")
        
        elif total_orphaned > 0:
            print("\n💡 TO CLEAN UP ORPHANED DOCUMENTS:")
            print("  Run the script with --delete flag to enable deletion mode")
            print("  Example: python query_missing_world_id.py --delete")
        
        elif total_orphaned == 0:
            print("\n✅ NO CLEANUP NEEDED - All documents have valid world associations!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())