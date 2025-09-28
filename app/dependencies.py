# C:\Code2025\rag\app\dependencies.py
import logging
from fastapi import Request, HTTPException, status

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.services.azure_ai_search_service import AzureAISearchService

logger = logging.getLogger(__name__)

def get_search_service(request: Request) -> 'AzureAISearchService':
    if not hasattr(request.app.state, 'search_service') or \
       request.app.state.search_service is None:
        logger.error("Dependency 'get_search_service': app.state.search_service instance not found or is None.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service instance not available in application state."
        )
        
    search_service_instance = request.app.state.search_service
    
    if not search_service_instance.get_search_client():
        logger.error(
            "Dependency 'get_search_service': Search client within AzureAISearchService is not available (init failed)."
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure AI Search client is not ready. Check server configuration or logs."
        )
    return search_service_instance