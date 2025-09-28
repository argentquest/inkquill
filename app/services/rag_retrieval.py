# /ai_rag_story_app/app/services/rag_retrieval.py

import semantic_kernel as sk
from semantic_kernel.functions.kernel_function_decorator import kernel_function
import os
from typing import Optional, List, Dict, Any
import logging

from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

from .embedding_service import generate_embeddings 
from app.core.config import settings
from app.processing.chunking import count_tokens 

logger = logging.getLogger(__name__)

AZURE_AI_SEARCH_ENDPOINT = str(settings.AZURE_AI_SEARCH_ENDPOINT) if settings.AZURE_AI_SEARCH_ENDPOINT else None
AZURE_AI_SEARCH_API_KEY = settings.AZURE_AI_SEARCH_API_KEY 
AZURE_AI_SEARCH_INDEX_NAME = settings.AZURE_AI_SEARCH_INDEX_NAME

class RetrievalPlugin:
    """
    A Semantic Kernel Plugin for RAG lookups against Azure AI Search.
    Returns structured results including relevance scores.
    """
    _search_client_instance: Optional[SearchClient] = None
    _initialized_clients: bool = False

    async def _ensure_clients_initialized(self):
        if self._initialized_clients:
            return
        if AZURE_AI_SEARCH_ENDPOINT and AZURE_AI_SEARCH_API_KEY and AZURE_AI_SEARCH_INDEX_NAME:
            try:
                logger.info(f"Initializing Azure AI Search client for RAG: {AZURE_AI_SEARCH_ENDPOINT}, index: {AZURE_AI_SEARCH_INDEX_NAME}")
                search_credential = AzureKeyCredential(AZURE_AI_SEARCH_API_KEY)
                self._search_client_instance = SearchClient(
                    endpoint=AZURE_AI_SEARCH_ENDPOINT,
                    index_name=AZURE_AI_SEARCH_INDEX_NAME,
                    credential=search_credential
                )
                self._initialized_clients = True
                logger.info("Azure AI Search client initialized successfully for RetrievalPlugin.")
            except Exception as e:
                logger.error(f"ERROR: Failed to initialize Azure AI Search client in RetrievalPlugin: {e}", exc_info=True)
                self._search_client_instance = None
        else:
            logger.error("ERROR: Azure AI Search config missing for RetrievalPlugin.")
            self._search_client_instance = None

    async def _generate_query_embedding(self, text: str, user_id: int) -> Optional[List[float]]:
        if not text or text.isspace():
            logger.warning("[RAG EMBEDDING DEBUG] Attempted to generate embedding for empty query text.")
            return None
        logger.info(f"[RAG EMBEDDING DEBUG] Generating embedding for query:")
        logger.info(f"[RAG EMBEDDING DEBUG]   - User ID: {user_id}")
        logger.info(f"[RAG EMBEDDING DEBUG]   - Query text: '{text[:100]}...'")
        
        embeddings_list = await generate_embeddings(texts=[text], user_id=user_id) 
        
        if embeddings_list and embeddings_list[0]:
            logger.info(f"[RAG EMBEDDING DEBUG] Successfully generated query embedding:")
            logger.info(f"[RAG EMBEDDING DEBUG]   - Embedding dimensions: {len(embeddings_list[0])}")
            logger.info(f"[RAG EMBEDDING DEBUG]   - First 5 values: {embeddings_list[0][:5]}")
            return embeddings_list[0]
        else:
            logger.error(f"[RAG EMBEDDING DEBUG] Failed to generate embedding for query: '{text[:100]}...'")
            logger.error(f"[RAG EMBEDDING DEBUG]   - Embeddings list: {embeddings_list}")
            return None

    @kernel_function(
        description="Retrieves relevant document chunks from Azure AI Search. Returns a list of chunks with their content, source, and relevance scores.",
        name="RetrieveRAGContext"
    )
    async def retrieve_rag_context(
        self,
        query: str, 
        user_id: int,
        top_k: int = None,
        user_id_filter: Optional[str] = None,
        world_id_filter: Optional[str] = None,
        min_relevance_score: float = None,
        max_total_tokens: int = None
    ) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = settings.RAG_RETRIEVAL_TOP_K
        if min_relevance_score is None:
            min_relevance_score = settings.RAG_MIN_RELEVANCE_SCORE
        if max_total_tokens is None:
            max_total_tokens = 4000  # Default reasonable limit for context
            
        await self._ensure_clients_initialized()
        logger.info(f"[RAG RETRIEVAL DEBUG] ===== Starting RAG Retrieval =====")
        logger.info(f"[RAG RETRIEVAL DEBUG] Input parameters:")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - Query: '{query[:100]}...'")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - User ID: {user_id}")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - Top K: {top_k}")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - Min relevance score: {min_relevance_score}")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - Max total tokens: {max_total_tokens}")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - User ID filter: {user_id_filter}")
        logger.info(f"[RAG RETRIEVAL DEBUG]   - World ID filter: {world_id_filter}")
        
        if not self._search_client_instance:
            logger.error("[RAG RETRIEVAL DEBUG] Azure AI Search client not available - aborting search")
            return []

        query_vector = await self._generate_query_embedding(query, user_id=user_id)
        
        vector_query_part: Optional[VectorizedQuery] = None
        if query_vector:
            vector_query_part = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields="chunk_text_vector")
            logger.info(f"[RAG RETRIEVAL DEBUG] Vector query created with k_nearest_neighbors={top_k}")
        
        # --- BEGIN FIX: Build a more robust filter expression ---
        filter_parts = []
        if user_id_filter:
            # This part is mandatory for security.
            filter_parts.append(f"user_id eq '{user_id_filter}'")

        # Now, handle the world context logic
        if world_id_filter:
            # If a specific world is in context, search for documents in THAT world
            # OR documents that have NO world assigned (general user documents).
            world_filter_expression = f"(world_id eq '{world_id_filter}' or world_id eq null)"
            filter_parts.append(world_filter_expression)
        else:
            # If no specific world is in context (e.g., a non-story related search),
            # maybe we only want to search general documents.
            # This behavior can be adjusted, but for now we'll assume it searches all user docs if no world is specified.
            # The current logic already does this, so no change needed for the 'else' case.
            pass
        
        filter_expression = " and ".join(filter_parts) if filter_parts else None
        # --- END FIX ---

        retrieved_documents: List[Dict[str, Any]] = []
        try:
            search_text_for_query = query if query and not query.isspace() else None
            
            # Debug logging after variables are defined
            logger.info(f"[RAG SEARCH DEBUG] Filter expression: {filter_expression}")
            logger.info(f"[RAG SEARCH DEBUG] Search text: '{search_text_for_query[:100] if search_text_for_query else 'None'}...'")
            logger.info(f"[RAG SEARCH DEBUG] Vector search: {'Yes' if vector_query_part else 'No'}")
            logger.info(f"[RAG SEARCH DEBUG] Index name: {AZURE_AI_SEARCH_INDEX_NAME}")
            if not search_text_for_query and not vector_query_part:
                logger.warning("[RAG SEARCH DEBUG] No search text or vector query provided - returning empty results")
                return []

            async with self._search_client_instance as client: 
                logger.info(f"[RAG SEARCH DEBUG] Executing search with top={top_k}")
                results = await client.search(
                    search_text=search_text_for_query, 
                    vector_queries=[vector_query_part] if vector_query_part else None,
                    filter=filter_expression, 
                    select=["chunk_text", "source_filename", "document_id"],
                    top=top_k
                )
                # Process results with enhanced filtering and token counting
                total_tokens = 0
                scored_documents = []
                chunks_processed = 0
                chunks_filtered_out = 0
                
                async for result in results:
                    chunks_processed += 1
                    chunk_text = result.get('chunk_text', '')
                    relevance_score = result.get('@search.score', 0.0)
                    
                    logger.debug(f"[RAG SEARCH DEBUG] Processing chunk {chunks_processed}:")
                    logger.debug(f"[RAG SEARCH DEBUG]   - Source: {result.get('source_filename', 'Unknown')}")
                    logger.debug(f"[RAG SEARCH DEBUG]   - Score: {relevance_score:.4f}")
                    logger.debug(f"[RAG SEARCH DEBUG]   - Preview: '{chunk_text[:50]}...'")
                    
                    # Apply relevance score filtering
                    if relevance_score and relevance_score < min_relevance_score:
                        logger.debug(f"[RAG SEARCH DEBUG]   - FILTERED OUT: Score {relevance_score:.4f} < {min_relevance_score}")
                        chunks_filtered_out += 1
                        continue
                    
                    # Count tokens for this chunk
                    chunk_tokens = count_tokens(chunk_text)
                    
                    # Check if adding this chunk would exceed token limit
                    if total_tokens + chunk_tokens > max_total_tokens:
                        logger.info(f"[RAG SEARCH DEBUG] Stopping retrieval - token limit reached ({total_tokens + chunk_tokens} > {max_total_tokens})")
                        break
                    
                    retrieved_doc = {
                        "text": chunk_text,
                        "source_filename": result.get('source_filename', 'Unknown Source'),
                        "document_id": result.get('document_id', 'N/A'),
                        "score": relevance_score,
                        "token_count": chunk_tokens
                    }
                    
                    scored_documents.append(retrieved_doc)
                    total_tokens += chunk_tokens
                    logger.debug(f"[RAG SEARCH DEBUG]   - INCLUDED: Added {chunk_tokens} tokens (total: {total_tokens})")
                
                logger.info(f"[RAG SEARCH DEBUG] Search complete:")
                logger.info(f"[RAG SEARCH DEBUG]   - Chunks processed: {chunks_processed}")
                logger.info(f"[RAG SEARCH DEBUG]   - Chunks filtered out: {chunks_filtered_out}")
                logger.info(f"[RAG SEARCH DEBUG]   - Chunks included: {len(scored_documents)}")
                logger.info(f"[RAG SEARCH DEBUG]   - Total tokens: {total_tokens}")
                
                return scored_documents
        except Exception as e:
            logger.error(f"ERROR: An unexpected error occurred during RAG retrieval: {e}", exc_info=True)
            return []

    async def close_clients(self):
        if self._search_client_instance:
            try:
                await self._search_client_instance.close()
                self._search_client_instance = None
                self._initialized_clients = False 
                logger.info("Azure AI Search client closed by RetrievalPlugin.")
            except Exception as e:
                logger.error(f"Error closing Azure AI Search client in RetrievalPlugin: {e}")