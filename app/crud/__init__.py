# /ai_rag_story_app/app/crud/__init__.py

# This file marks the 'crud' directory as a Python package.
# It allows you to import modules from this directory using dot notation
# (e.g., from app.crud.user import create_user).

# This file can be kept empty.
# Optionally, you could import your CRUD functions here to make them
# available directly from the app.crud namespace, for example:
#
# from .user import get_user, get_user_by_username, create_user, update_user
# from .story import create_story, get_story, get_stories_by_user, update_story, delete_story
# from .act import create_act, get_act, get_acts_by_story, update_act, delete_act
# from .document import create_document_record, get_document, update_document_status
#
# This would allow imports like:
# from app.crud import create_user
# instead of:
# from app.crud.user import create_user
#
# For now, keeping it empty is standard and allows for clear, explicit imports.