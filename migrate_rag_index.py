# migrate_rag_index.py
import asyncio
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

# --- BEGIN LOGGING SETUP ---
# Create a 'logs' directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(log_dir, f"migrate_rag_index_{run_timestamp}.log")

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
# --- END LOGGING SETUP ---

# Load environment variables first
logger.info("Loading environment variables...")
load_dotenv()

# Now, safe to import application components that rely on settings
from fastapi import BackgroundTasks
from app.db.database import async_session_local
from app.crud import character, location, lore_item
from app.processing.world_element_processor import generate_and_index_world_element_rag_text_task
from app.models.world import World
from sqlalchemy.future import select

# Import services needed for initialization
from app.services import embedding_service


async def migrate_all_world_elements():
    """
    Fetches all world elements (characters, locations, lore items) across all worlds
    and triggers the RAG re-indexing background task for each one.
    This task will use the new settings from the .env file (ada-002, 1536d, new index name).
    """
    logger.info("--- Starting RAG Migration for all World Elements ---")
    
    all_tasks_to_run = []

    async with async_session_local() as db:
        all_worlds_result = await db.execute(select(World))
        all_worlds = all_worlds_result.scalars().all()
        
        logger.info(f"Found {len(all_worlds)} worlds to process.")

        for world in all_worlds:
            logger.info(f"Processing World ID: {world.id} (User ID: {world.user_id})")
            dummy_bg_tasks = BackgroundTasks() # We manage tasks ourselves here

            # Characters
            chars = await character.get_characters_by_world(db, world_id=world.id, limit=10000)
            for char in chars:
                logger.info(f"  - Scheduling RAG re-indexing for Character ID: {char.id}")
                all_tasks_to_run.append(
                    generate_and_index_world_element_rag_text_task(
                        "character", char.id, world.user_id, world.id, dummy_bg_tasks
                    )
                )

            # Locations
            locs = await location.get_locations_by_world(db, world_id=world.id, limit=10000)
            for loc in locs:
                logger.info(f"  - Scheduling RAG re-indexing for Location ID: {loc.id}")
                all_tasks_to_run.append(
                    generate_and_index_world_element_rag_text_task(
                        "location", loc.id, world.user_id, world.id, dummy_bg_tasks
                    )
                )

            # Lore Items
            lores = await lore_item.get_lore_items_by_world(db, world_id=world.id, limit=10000)
            for lore in lores:
                logger.info(f"  - Scheduling RAG re-indexing for Lore Item ID: {lore.id}")
                all_tasks_to_run.append(
                    generate_and_index_world_element_rag_text_task(
                        "lore_item", lore.id, world.user_id, world.id, dummy_bg_tasks
                    )
                )

    if all_tasks_to_run:
        logger.info(f"Executing a total of {len(all_tasks_to_run)} RAG indexing tasks concurrently...")
        # Note: Depending on the number of items, this might hit API rate limits.
        # For very large datasets, you might add a semaphore here to limit concurrency.
        await asyncio.gather(*all_tasks_to_run)
    
    logger.info("--- World Element Migration Finished ---")


async def migrate_user_documents():
    """Placeholder for migrating user-uploaded documents."""
    logger.warning("--- User Document Migration SKIPPED ---")


async def main():
    logger.info("======================================================================")
    logger.info(" RAG Index Migration Script to 1536 Dimensions (text-embedding-ada-002)")
    logger.info("======================================================================")
    logger.info(f"Logging detailed output to: {log_file_path}")
    logger.info("This script will re-process all world elements using the new embedding model.")
    logger.info("Ensure your .env file is correctly configured to point to the NEW search index and embedding model.")
    
    logger.info("Initializing required services for migration...")
    embedding_service.initialize_embedding_client()
    
    try:
        await migrate_all_world_elements()
        await migrate_user_documents()
    finally:
        logger.info("Cleaning up services...")
        await embedding_service.close_embedding_client()
    
    logger.info("Migration script finished. Your new 1536d index should now be populated.")


if __name__ == "__main__":
    asyncio.run(main())