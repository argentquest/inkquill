# Quick RAG Visibility Implementation

Based on your existing code, here's how to quickly add RAG visibility to your world chat system.

## 1. Update WorldChatService to Return RAG Metadata

Modify `/app/services/world_chat_service.py`:

```python
async def process_message(
    self,
    session_id: int,
    user_message: str,
    world_id: int,
    user_id: Optional[int],
    db: AsyncSession
) -> Dict:
    """Process a chat message and return AI response with RAG metadata"""
    try:
        # Store user message
        user_msg = await create_chat_message(
            db=db,
            session_id=session_id,
            content=user_message,
            is_from_user=True,
            user_id=user_id
        )
        
        # Load world context for RAG - PASS THE QUERY HERE
        context = await load_world_context(world_id, user_id, db, query=user_message)
        
        # Check if we got RAG results
        rag_used = len(context) > 0 and any(item.get('score', 0) < 1.0 for item in context)
        
        # Get Semantic Kernel instance
        kernel = await get_kernel_instance()
        
        # Get the chat function
        chat_function = kernel.get_function("WorldChatPlugin", "world_chat")
        
        # Prepare context for the function
        context_text = ""
        if context:
            context_text = "\n".join([
                f"Source: {item.get('source', 'Unknown')}\nContent: {item.get('content', '')}"
                for item in context
            ])
        
        # Execute the chat function
        result = await chat_function.invoke(
            kernel,
            user_message=user_message,
            world_context=context_text
        )
        
        ai_response = str(result)
        
        # Store AI response
        ai_msg = await create_chat_message(
            db=db,
            session_id=session_id,
            content=ai_response,
            is_from_user=False,
            user_id=user_id
        )
        
        # Track cost
        await self.cost_tracker.log_ai_call(
            user_id=user_id,
            operation_type="world_chat",
            model_name=settings.OPENAI_MODEL_NAME,
            prompt_tokens=len(user_message.split()) + len(context_text.split()),
            completion_tokens=len(ai_response.split()),
            total_cost=0.001
        )
        
        # NEW: Return RAG metadata
        return {
            "response": ai_response,
            "user_message_id": user_msg.id,
            "ai_message_id": ai_msg.id,
            # RAG metadata
            "rag_used": rag_used,
            "rag_sources": [
                {
                    "source": item.get('source'),
                    "content_preview": item.get('content', '')[:150] + "..." if len(item.get('content', '')) > 150 else item.get('content', ''),
                    "score": item.get('score'),
                    "type": item.get('type', 'document')
                }
                for item in context if item.get('score', 0) < 1.0  # Only show search results, not world elements
            ][:3],  # Limit to top 3
            "total_sources": len([item for item in context if item.get('score', 0) < 1.0])
        }
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise
```

## 2. Update WebSocket Response

Modify `/app/routers/world_chat.py`:

```python
# Send response back to client
await websocket.send_json({
    "response": result["response"],
    "user_message_id": result["user_message_id"],
    "ai_message_id": result["ai_message_id"],
    # NEW: Add RAG metadata
    "rag_used": result.get("rag_used", False),
    "rag_sources": result.get("rag_sources", []),
    "total_sources": result.get("total_sources", 0)
})
```

## 3. Update Frontend Chat Component

Add to your chat component (assuming React/TypeScript):

```typescript
interface ChatMessage {
    response: string;
    rag_used?: boolean;
    rag_sources?: Array<{
        source: string;
        content_preview: string;
        score: number;
        type: string;
    }>;
    total_sources?: number;
}

const ChatMessageComponent = ({ message }: { message: ChatMessage }) => {
    return (
        <div className="chat-message">
            <div className="message-content">
                {message.response}
            </div>
            
            {/* RAG Indicator */}
            {message.rag_used && (
                <div className="rag-indicator">
                    <div className="rag-badge">
                        📚 Used {message.total_sources || 0} sources from your documents
                    </div>
                    {message.rag_sources && message.rag_sources.length > 0 && (
                        <details className="rag-sources">
                            <summary>View sources</summary>
                            {message.rag_sources.map((source, idx) => (
                                <div key={idx} className="source-item">
                                    <strong>{source.source}</strong>
                                    <div className="source-preview">"{source.content_preview}"</div>
                                    <div className="source-score">
                                        Relevance: {Math.round(source.score * 100)}%
                                    </div>
                                </div>
                            ))}
                        </details>
                    )}
                </div>
            )}
            
            {/* No RAG Indicator */}
            {!message.rag_used && (
                <div className="no-rag-indicator">
                    <span className="no-rag-badge">🤖 General knowledge</span>
                </div>
            )}
        </div>
    );
};
```

## 4. CSS Styles

Add to your CSS:

```css
.rag-indicator {
    margin-top: 8px;
    padding: 8px;
    background-color: #e8f5e8;
    border-left: 4px solid #4caf50;
    border-radius: 4px;
    font-size: 0.9em;
}

.rag-badge {
    color: #2e7d32;
    font-weight: 500;
}

.rag-sources {
    margin-top: 8px;
}

.rag-sources summary {
    cursor: pointer;
    color: #1976d2;
    font-size: 0.85em;
}

.source-item {
    margin: 8px 0;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.source-preview {
    font-style: italic;
    color: #666;
    margin: 4px 0;
}

.source-score {
    font-size: 0.8em;
    color: #4caf50;
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

## 5. Testing Your Implementation

### Test Cases:

1. **RAG Should Trigger:**
   - "What happens in chapter 3 of the book?"
   - "Tell me about the main character"
   - "What is the setting described in the text?"

2. **RAG Should NOT Trigger:**
   - "What's the weather like today?"
   - "How do I cook pasta?"
   - "Tell me a joke"

### Debug Your RAG:

Add this to your `world_context_loader.py` to see what's happening:

```python
async def load_world_context(
    world_id: int, 
    user_id: Optional[int], 
    db: AsyncSession,
    query: Optional[str] = None,
    max_results: int = 10
) -> List[Dict]:
    try:
        context_items = []
        
        # DEBUG: Log the query
        logger.info(f"RAG Query: '{query}' for world {world_id}")
        
        # If we have a specific query, use RAG search
        if query and settings.AZURE_SEARCH_ENDPOINT:
            search_service = AzureAISearchService()
            
            # Search for relevant documents
            search_results = await search_service.search_documents(
                query=query,
                filters={
                    "world_id": world_id,
                    "user_id": user_id
                },
                top=max_results
            )
            
            # DEBUG: Log search results
            logger.info(f"RAG Search returned {len(search_results)} results")
            
            # Convert search results to context items
            for result in search_results:
                context_items.append({
                    "source": f"Document: {result.get('title', 'Unknown')}",
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "document_id": result.get("document_id"),
                    "metadata": result.get("metadata", {})
                })
        
        # If no specific query or no search results, load general world context
        if not context_items:
            # DEBUG: Log fallback
            logger.info(f"No RAG results, using world elements as fallback")
            context_items = await _load_world_elements_context(world_id, db)
        
        logger.info(f"Loaded {len(context_items)} context items for world {world_id}")
        return context_items
        
    except Exception as e:
        logger.error(f"Error loading world context: {e}")
        return []
```

## 6. Verify Your Setup

1. **Check if documents are indexed:**
   - Look in your Azure AI Search index
   - Verify documents have `world_id` and `user_id` fields

2. **Test the search directly:**
   ```python
   # In a Python console or test
   from app.services.azure_ai_search_service import AzureAISearchService
   
   search_service = AzureAISearchService()
   results = await search_service.search_documents(
       query="your test query",
       filters={"world_id": 1, "user_id": 1}
   )
   print(f"Found {len(results)} results")
   ```

3. **Check your logs:**
   - Look for "RAG Query:" and "RAG Search returned" messages
   - This will tell you if RAG is triggering

## Quick Visual Summary

When RAG is working, users will see:
- ✅ **With RAG**: `📚 Used 3 sources from your documents`
- ❌ **Without RAG**: `🤖 General knowledge`

This implementation will immediately show users when their imported books are being used in the chat responses!