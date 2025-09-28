#!/usr/bin/env python3
"""
Azure AI Search Service Migration Script

This script migrates all indexed content from an old Azure AI Search service to a new one by:
1. Reading all uploaded documents from the database
2. Checking if their files still exist on disk
3. Re-processing and re-indexing them on the new search service
4. Re-indexing all world elements (characters, locations, lore items) from database

Usage:
    python migrate_search_service.py [--dry-run] [--documents-only] [--elements-only]
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

# Import your app modules
from app.db.database import async_session_local
from app.models.uploaded_document import UploadedDocument, DocumentStatus, SourceElementTypeEnum
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.world import World
from app.crud import document as crud_document
from app.processing.rag_ingestion import process_uploaded_document_task
from app.processing.world_element_processor import generate_and_index_world_element_rag_text_task
from app.core.config import settings
from fastapi import BackgroundTasks

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchServiceMigrator:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.stats = {
            'documents_found': 0,
            'documents_existing': 0,
            'documents_processed': 0,
            'documents_failed': 0,
            'elements_found': 0,
            'elements_processed': 0,
            'elements_failed': 0
        }

    async def migrate_documents(self) -> None:
        """Migrate all documents that still exist on disk"""
        logger.info("🔍 Starting document migration...")
        
        async with async_session_local() as db:
            # Get all documents with COMPLETED status (successfully processed before)
            result = await db.execute(
                select(UploadedDocument)
                .where(UploadedDocument.status == DocumentStatus.COMPLETED)
                .order_by(UploadedDocument.id)
            )
            documents = result.scalars().all()
            
            self.stats['documents_found'] = len(documents)
            logger.info(f"📄 Found {len(documents)} completed documents in database")
            
            for doc in documents:
                await self._process_single_document(doc, db)
    
    async def _process_single_document(self, doc: UploadedDocument, db: AsyncSession) -> None:
        """Process a single document for migration"""
        logger.info(f"📄 Processing document {doc.id}: {doc.filename}")
        
        # Check if file exists on disk
        file_path = self._resolve_file_path(doc.blob_storage_path)
        
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"❌ File not found for document {doc.id}: {doc.blob_storage_path}")
            return
            
        self.stats['documents_existing'] += 1
        logger.info(f"✅ File exists: {file_path}")
        
        if self.dry_run:
            logger.info(f"🔄 [DRY RUN] Would re-process document {doc.id}")
            return
        
        try:
            # Generate a new job ID for tracking
            job_id = f"migration_{doc.id}_{int(asyncio.get_event_loop().time())}"
            
            # Reset document status to trigger re-processing
            await crud_document.update_document_status(
                db, doc.id, DocumentStatus.UPLOADED, 
                error_message=None
            )
            await db.commit()
            
            # Re-process the document
            await process_uploaded_document_task(
                job_id=job_id,
                db_document_id=doc.id,
                file_path_on_disk=file_path
            )
            
            self.stats['documents_processed'] += 1
            logger.info(f"✅ Successfully re-processed document {doc.id}")
            
        except Exception as e:
            self.stats['documents_failed'] += 1
            logger.error(f"❌ Failed to process document {doc.id}: {e}")
    
    def _resolve_file_path(self, blob_storage_path: str) -> Optional[str]:
        """
        Resolve the blob storage path to actual file path on disk.
        Adjust this logic based on how your app stores files.
        """
        # Common patterns for local storage:
        
        # Pattern 1: If blob_storage_path is relative to uploads directory
        uploads_dir = Path("uploads")  # Adjust based on your setup
        if uploads_dir.exists():
            full_path = uploads_dir / blob_storage_path
            if full_path.exists():
                return str(full_path)
        
        # Pattern 2: If blob_storage_path is already an absolute path
        if os.path.isabs(blob_storage_path) and os.path.exists(blob_storage_path):
            return blob_storage_path
        
        # Pattern 3: Check temp directories or other common locations
        temp_path = Path("/tmp") / blob_storage_path.split("/")[-1]  # Just filename
        if temp_path.exists():
            return str(temp_path)
        
        # Add more patterns based on your file storage setup
        logger.debug(f"Could not resolve file path for: {blob_storage_path}")
        return None
    
    async def migrate_world_elements(self) -> None:
        """Migrate all world elements (characters, locations, lore items)"""
        logger.info("🌍 Starting world elements migration...")
        
        async with async_session_local() as db:
            # Get all characters with their worlds eagerly loaded
            characters_result = await db.execute(
                select(Character).options(selectinload(Character.world))
            )
            characters = characters_result.scalars().all()
            
            # Get all locations with their worlds eagerly loaded
            locations_result = await db.execute(
                select(Location).options(selectinload(Location.world))
            )
            locations = locations_result.scalars().all()
            
            # Get all lore items with their worlds eagerly loaded
            lore_result = await db.execute(
                select(LoreItem).options(selectinload(LoreItem.world))
            )
            lore_items = lore_result.scalars().all()
            
            total_elements = len(characters) + len(locations) + len(lore_items)
            self.stats['elements_found'] = total_elements
            
            logger.info(f"🌍 Found {len(characters)} characters, {len(locations)} locations, {len(lore_items)} lore items")
            
            # Process characters
            for char in characters:
                await self._process_world_element(char, "character", db)
            
            # Process locations
            for loc in locations:
                await self._process_world_element(loc, "location", db)
            
            # Process lore items
            for lore in lore_items:
                await self._process_world_element(lore, "lore_item", db)
    
    async def _process_world_element(self, element: Any, element_type: str, db: AsyncSession) -> None:
        """Process a single world element for migration"""
        # LoreItem uses 'title' instead of 'name'
        element_name = element.title if element_type == "lore_item" else element.name
        logger.info(f"🌍 Processing {element_type} {element.id}: {element_name}")
        
        if self.dry_run:
            logger.info(f"🔄 [DRY RUN] Would re-index {element_type} {element.id}")
            return
        
        try:
            dummy_bg_tasks = BackgroundTasks()
            
            # Get user_id from the world relationship (already eagerly loaded)
            user_id = element.world.user_id
            
            await generate_and_index_world_element_rag_text_task(
                element_type_str=element_type,
                element_id=element.id,
                user_id=user_id,
                world_id=element.world_id,
                background_tasks=dummy_bg_tasks,
                model_config_id=None  # Use default model
            )
            
            self.stats['elements_processed'] += 1
            logger.info(f"✅ Successfully re-indexed {element_type} {element.id}")
            
        except Exception as e:
            self.stats['elements_failed'] += 1
            logger.error(f"❌ Failed to process {element_type} {element.id}: {e}", exc_info=True)
    
    def print_summary(self) -> None:
        """Print migration summary"""
        logger.info("📊 Migration Summary:")
        logger.info(f"   Documents found: {self.stats['documents_found']}")
        logger.info(f"   Documents with existing files: {self.stats['documents_existing']}")
        logger.info(f"   Documents processed: {self.stats['documents_processed']}")
        logger.info(f"   Documents failed: {self.stats['documents_failed']}")
        logger.info(f"   World elements found: {self.stats['elements_found']}")
        logger.info(f"   World elements processed: {self.stats['elements_processed']}")
        logger.info(f"   World elements failed: {self.stats['elements_failed']}")

async def main():
    parser = argparse.ArgumentParser(description="Migrate Azure AI Search Service")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually doing it")
    parser.add_argument("--documents-only", action="store_true", help="Only migrate documents")
    parser.add_argument("--elements-only", action="store_true", help="Only migrate world elements")
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("🔄 Running in DRY RUN mode - no changes will be made")
    
    # Verify configuration
    if not settings.AZURE_AI_SEARCH_ENDPOINT or not settings.AZURE_AI_SEARCH_API_KEY:
        logger.error("❌ Azure AI Search configuration is missing. Please check your environment variables.")
        return
    
    logger.info(f"🔧 Using search endpoint: {settings.AZURE_AI_SEARCH_ENDPOINT}")
    logger.info(f"🔧 Using search index: {settings.AZURE_AI_SEARCH_INDEX_NAME}")
    
    migrator = SearchServiceMigrator(dry_run=args.dry_run)
    
    try:
        if not args.elements_only:
            await migrator.migrate_documents()
        
        if not args.documents_only:
            await migrator.migrate_world_elements()
            
    except KeyboardInterrupt:
        logger.info("⏹️ Migration interrupted by user")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
    finally:
        migrator.print_summary()

if __name__ == "__main__":
    asyncio.run(main())