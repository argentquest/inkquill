# /ai_rag_story_app/app/core/context.py
from contextvars import ContextVar, Token as ContextVarToken # Import Token for type hints
from typing import Optional, Any # <<< ADDED Any HERE

# Context variable for a unique request ID (good for tracing)
# Default is None, middleware will set it.
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

# Context variable for the current user's identifier (username or ID string)
# Default to a placeholder indicating no user context is set.
user_identifier_var: ContextVar[str] = ContextVar("user_identifier", default="[no_user_context]")

# Optional: If you also want to log user's actual integer ID when available
# user_db_id_var: ContextVar[Optional[int]] = ContextVar("user_db_id", default=None)

def get_request_id() -> Optional[str]:
    return request_id_var.get()

def set_request_id(req_id: str) -> ContextVarToken: # Return the specific Token type
    return request_id_var.set(req_id)

def reset_request_id(token: ContextVarToken): # Expect the specific Token type
    request_id_var.reset(token)

def get_user_identifier() -> str:
    return user_identifier_var.get()

def set_user_identifier(identifier: str) -> ContextVarToken: # Return the specific Token type
    return user_identifier_var.set(identifier)

def reset_user_identifier(token: ContextVarToken): # Expect the specific Token type
    user_identifier_var.reset(token)