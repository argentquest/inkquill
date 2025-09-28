# /ai_rag_story_app/app/services/sk_constants.py

"""
This module defines constants for Semantic Kernel plugin names used throughout the application.
Centralizing these names helps prevent typos and ensures consistency when registering
and retrieving plugins and their functions.
"""

# Plugin name for functions related to generating and modifying narrative content.
STORYTELLING_PLUGIN_NAME: str = "StorytellingPlugin"

# Plugin name for functions related to analyzing story content, like reviews or metadata extraction.
STORY_ANALYSIS_PLUGIN_NAME: str = "StoryAnalysisPlugin"

# Plugin name for functions dealing with the structural aspects of a story (e.g., scene extraction).
STORY_STRUCTURE_PLUGIN_NAME: str = "StoryStructurePlugin"

# Plugin name for functions that process or generate descriptive text for world-building elements.
WORLD_BUILDING_PLUGIN_NAME: str = "WorldBuildingPlugin"

# Plugin name for functions that generate entire world structures (e.g., from a book title).
WORLD_GENERATION_PLUGIN_NAME: str = "WorldGenerationPlugin"

# Plugin name for the native RAG retrieval plugin.
RETRIEVAL_PLUGIN_NAME: str = "Retrieval"

# You can add more constants here if other plugin types emerge.