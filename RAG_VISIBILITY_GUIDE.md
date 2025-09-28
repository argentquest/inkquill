# RAG Visibility Guide

This guide explains how to make RAG (Retrieval Augmented Generation) usage visible in chat responses when discussing imported books and documents.

## Overview

When users chat about imported books/documents, they need to know:
1. Whether RAG is being used
2. What sources are being referenced
3. How relevant the retrieved content is
4. What specific parts of their documents are being used

## Implementation Approaches

### 1. Enhanced Chat Response with RAG Metadata

Modify your chat response structure to include RAG information:

```python
# In your chat service or response model
class ChatResponseWithRAG(BaseModel):
    message: str
    rag_used: bool = False
    rag_sources: List[Dict] = []
    rag_context_preview: Optional[str] = None
    confidence_score: Optional[float] = None

# Enhanced chat processing function
async def process_chat_with_rag_visibility(
    message: str,
    world_id: int,
    user_id: int,
    db: AsyncSession
) -> ChatResponseWithRAG:
    """Process chat message with RAG visibility"""
    
    # Perform RAG search
    rag_results = await search_world_context(message, world_id, user_id)
    
    if rag_results and len(rag_results) > 0:
        # Build context from RAG results
        context = build_context_from_results(rag_results)
        
        # Generate AI response with context
        ai_response = await generate_ai_response_with_context(message, context)
        
        # Build RAG metadata for response
        rag_sources = [
            {
                "document_id": result.get("document_id"),
                "document_name": result.get("document_name"),
                "chunk_text": result.get("content")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content"),
                "relevance_score": result.get("score"),
                "page_number": result.get("metadata", {}).get("page_number"),
                "source_type": result.get("metadata", {}).get("source_type", "document")
            }
            for result in rag_results[:3]  # Show top 3 sources
        ]
        
        # Calculate average confidence
        avg_confidence = sum(r.get("score", 0) for r in rag_results) / len(rag_results)
        
        return ChatResponseWithRAG(
            message=ai_response,
            rag_used=True,
            rag_sources=rag_sources,
            rag_context_preview=context[:300] + "..." if len(context) > 300 else context,
            confidence_score=round(avg_confidence, 2)
        )
    else:
        # No RAG results, use base AI response
        ai_response = await generate_ai_response(message)
        
        return ChatResponseWithRAG(
            message=ai_response,
            rag_used=False,
            rag_sources=[],
            rag_context_preview=None,
            confidence_score=None
        )
```

### 2. Visual Indicators in Frontend

Add visual cues to show RAG usage:

```typescript
// Chat message component with RAG indicators
interface ChatMessageProps {
    message: string;
    ragUsed: boolean;
    ragSources?: RagSource[];
    ragContextPreview?: string;
    confidenceScore?: number;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
    message,
    ragUsed,
    ragSources,
    ragContextPreview,
    confidenceScore
}) => {
    return (
        <div className="chat-message">
            <div className="message-content">
                {message}
            </div>
            
            {/* RAG Indicator */}
            {ragUsed && (
                <div className="rag-indicator">
                    <div className="rag-badge">
                        📚 Using your documents
                        {confidenceScore && (
                            <span className="confidence-score">
                                ({Math.round(confidenceScore * 100)}% relevance)
                            </span>
                        )}
                    </div>
                    
                    {/* Sources dropdown */}
                    <details className="rag-sources">
                        <summary>View sources ({ragSources?.length || 0})</summary>
                        <div className="sources-list">
                            {ragSources?.map((source, index) => (
                                <div key={index} className="source-item">
                                    <div className="source-header">
                                        <strong>{source.document_name}</strong>
                                        {source.page_number && (
                                            <span className="page-number">Page {source.page_number}</span>
                                        )}
                                        <span className="relevance-score">
                                            {Math.round(source.relevance_score * 100)}% relevant
                                        </span>
                                    </div>
                                    <div className="source-preview">
                                        "{source.chunk_text}"
                                    </div>
                                </div>
                            ))}
                        </div>
                    </details>
                </div>
            )}
            
            {/* No RAG indicator */}
            {!ragUsed && (
                <div className="no-rag-indicator">
                    <span className="no-rag-badge">🤖 General knowledge</span>
                </div>
            )}
        </div>
    );
};
```

### 3. CSS Styling for RAG Indicators

```css
/* RAG visibility styles */
.rag-indicator {
    margin-top: 8px;
    padding: 8px;
    background-color: #e8f5e8;
    border-left: 4px solid #4caf50;
    border-radius: 4px;
    font-size: 0.9em;
}

.rag-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: #2e7d32;
}

.confidence-score {
    font-size: 0.8em;
    color: #666;
}

.rag-sources {
    margin-top: 8px;
}

.rag-sources summary {
    cursor: pointer;
    color: #1976d2;
    font-size: 0.85em;
}

.rag-sources summary:hover {
    text-decoration: underline;
}

.sources-list {
    margin-top: 8px;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.source-item {
    margin-bottom: 12px;
    padding: 8px;
    background-color: white;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
}

.source-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    flex-wrap: wrap;
}

.page-number {
    font-size: 0.8em;
    color: #666;
    background-color: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
}

.relevance-score {
    font-size: 0.8em;
    color: #4caf50;
    font-weight: 500;
}

.source-preview {
    font-style: italic;
    color: #555;
    font-size: 0.85em;
    line-height: 1.4;
}

.no-rag-indicator {
    margin-top: 8px;
    padding: 6px 8px;
    background-color: #f3f4f6;
    border-left: 4px solid #9ca3af;
    border-radius: 4px;
}

.no-rag-badge {
    font-size: 0.85em;
    color: #6b7280;
}
```

### 4. Enhanced Backend RAG Search with Metadata

```python
async def search_world_context_with_metadata(
    query: str, 
    world_id: int, 
    user_id: int,
    include_metadata: bool = True
) -> List[Dict]:
    """Enhanced RAG search that returns detailed metadata"""
    
    # Your existing search logic
    search_results = await ai_search_service.search_documents(
        query=query,
        filters={
            "world_id": world_id,
            "user_id": user_id
        }
    )
    
    enhanced_results = []
    for result in search_results:
        # Get document details from database
        document = await get_document_by_id(result.get("document_id"))
        
        enhanced_result = {
            "content": result.get("content"),
            "score": result.get("score"),
            "document_id": result.get("document_id"),
            "document_name": document.original_filename if document else "Unknown Document",
            "document_type": document.document_type if document else "unknown",
            "chunk_id": result.get("chunk_id"),
            "metadata": {
                "page_number": result.get("metadata", {}).get("page_number"),
                "chunk_index": result.get("metadata", {}).get("chunk_index"),
                "source_type": "imported_book" if document and document.document_type == "TEXT" else "document",
                "upload_date": document.created_at.isoformat() if document else None,
                "file_size": document.file_size if document else None
            }
        }
        enhanced_results.append(enhanced_result)
    
    return enhanced_results

# Add this to your chat processing
async def process_world_chat_message(
    message: str,
    world_id: int,
    user_id: int,
    db: AsyncSession
):
    """Process chat message with enhanced RAG visibility"""
    
    # Search for relevant context
    rag_results = await search_world_context_with_metadata(
        query=message,
        world_id=world_id,
        user_id=user_id
    )
    
    # Build response with RAG metadata
    if rag_results:
        # Create context for AI
        context_pieces = []
        for result in rag_results[:5]:  # Use top 5 results
            context_pieces.append(f"Source: {result['document_name']}\nContent: {result['content']}")
        
        context = "\n\n".join(context_pieces)
        
        # Generate AI response with context
        system_prompt = f"""You are discussing a world and its lore. Use the following context from the user's imported documents to answer their question accurately:

CONTEXT:
{context}

Answer based on the provided context. If the context doesn't contain relevant information, say so clearly."""
        
        ai_response = await generate_ai_response(message, system_prompt)
        
        # Return response with RAG metadata
        return {
            "message": ai_response,
            "rag_used": True,
            "rag_sources": [
                {
                    "document_id": r["document_id"],
                    "document_name": r["document_name"],
                    "chunk_text": r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                    "relevance_score": r["score"],
                    "page_number": r["metadata"].get("page_number"),
                    "source_type": r["metadata"].get("source_type")
                }
                for r in rag_results[:3]
            ],
            "context_used": len(rag_results),
            "confidence_score": sum(r["score"] for r in rag_results) / len(rag_results)
        }
    else:
        # No relevant context found
        ai_response = await generate_ai_response(message)
        
        return {
            "message": ai_response + "\n\n*Note: No relevant information found in your imported documents for this query.*",
            "rag_used": False,
            "rag_sources": [],
            "context_used": 0,
            "confidence_score": None
        }
```

### 5. WebSocket Integration for Real-time RAG Feedback

```python
# In your WebSocket chat handler
class WorldChatWebSocket:
    async def handle_message(self, websocket: WebSocket, data: dict):
        message = data.get("message")
        world_id = data.get("world_id")
        
        # Send typing indicator
        await websocket.send_json({
            "type": "typing",
            "message": "Searching your documents..."
        })
        
        # Process with RAG
        response = await process_world_chat_message(
            message=message,
            world_id=world_id,
            user_id=self.user_id,
            db=self.db
        )
        
        # Send response with RAG metadata
        await websocket.send_json({
            "type": "message",
            "content": response["message"],
            "rag_used": response["rag_used"],
            "rag_sources": response["rag_sources"],
            "context_used": response["context_used"],
            "confidence_score": response["confidence_score"],
            "timestamp": datetime.utcnow().isoformat()
        })
```

### 6. Debug Mode for Development

```python
# Add debug mode to see detailed RAG information
async def process_chat_debug_mode(
    message: str,
    world_id: int,
    user_id: int,
    debug: bool = False
):
    """Chat processing with optional debug information"""
    
    if debug:
        # Return detailed RAG information for development
        rag_results = await search_world_context_with_metadata(message, world_id, user_id)
        
        debug_info = {
            "query": message,
            "rag_search_performed": True,
            "results_found": len(rag_results),
            "search_results": [
                {
                    "score": r["score"],
                    "content_preview": r["content"][:100] + "...",
                    "document": r["document_name"],
                    "metadata": r["metadata"]
                }
                for r in rag_results
            ],
            "context_length": sum(len(r["content"]) for r in rag_results),
            "documents_searched": len(set(r["document_id"] for r in rag_results))
        }
        
        return {
            "response": await generate_response_with_rag(message, rag_results),
            "debug": debug_info
        }
    else:
        # Normal processing
        return await process_world_chat_message(message, world_id, user_id)
```

### 7. User Settings for RAG Visibility

```python
# Add user preference for RAG visibility
class UserChatSettings(BaseModel):
    show_rag_sources: bool = True
    show_confidence_scores: bool = True
    show_document_previews: bool = True
    rag_transparency_level: str = "detailed"  # "minimal", "standard", "detailed"

# In chat processing, respect user preferences
async def format_response_for_user(response_data: dict, user_settings: UserChatSettings):
    """Format chat response based on user preferences"""
    
    if not user_settings.show_rag_sources:
        response_data.pop("rag_sources", None)
    
    if not user_settings.show_confidence_scores:
        response_data.pop("confidence_score", None)
    
    if user_settings.rag_transparency_level == "minimal":
        # Only show basic RAG indicator
        response_data["rag_sources"] = []
        response_data["rag_context_preview"] = None
    
    return response_data
```

## Testing RAG Visibility

### 1. Test Queries to Verify RAG Usage

```python
# Test queries that should trigger RAG
test_queries = [
    "What happened in chapter 3?",
    "Tell me about the main character",
    "What is the setting of the story?",
    "How does the book end?",
    "Who are the supporting characters?"
]

# Test queries that should NOT trigger RAG
general_queries = [
    "What's the weather like?",
    "How do I cook pasta?",
    "What year is it?",
    "Tell me a joke"
]
```

### 2. RAG Performance Monitoring

```python
# Add logging to track RAG usage
import logging

logger = logging.getLogger("rag_monitor")

async def log_rag_usage(query: str, results_count: int, confidence: float, world_id: int):
    """Log RAG usage for monitoring"""
    logger.info(f"RAG Query: {query[:50]}... | Results: {results_count} | Confidence: {confidence:.2f} | World: {world_id}")
```

## Best Practices

1. **Clear Visual Indicators**: Make it obvious when RAG is being used
2. **Source Attribution**: Always show which documents are being referenced
3. **Confidence Scores**: Help users understand how relevant the retrieved content is
4. **Fallback Messaging**: Clearly indicate when no relevant documents are found
5. **User Control**: Allow users to toggle RAG visibility features
6. **Performance**: Don't let RAG metadata slow down the chat experience

## Troubleshooting

### Common Issues:

1. **RAG not triggering**: Check if documents are properly indexed
2. **Poor relevance**: Review search query processing and document chunking
3. **Performance slow**: Optimize search queries and limit result count
4. **UI cluttered**: Allow users to minimize RAG information