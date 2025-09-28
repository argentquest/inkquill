# /ai_rag_story_app/app/schemas/__init__.py

# This file marks the 'schemas' directory as a Python package.
# It allows you to import modules from this directory using dot notation
# (e.g., from app.schemas.user import UserRead).

# This file can be kept empty.
# Optionally, you could import your Pydantic schema classes here to make them
# available directly from the app.schemas namespace, for example:
#
# from .user import UserCreate, UserRead, UserUpdate
# from .token import Token, TokenPayload
# from .story import StoryCreate, StoryRead, StoryUpdate
# from .act import ActCreate, ActRead, ActUpdate
# from .document import DocumentRead, DocumentUploadResponse
# from .billing import UserAccountResponse, UserTransactionResponse, CreditPackageResponse
#
# This would allow imports like:
# from app.schemas import UserRead
# instead of:
# from app.schemas.user import UserRead
#
# For now, keeping it empty is standard and allows for clear, explicit imports.