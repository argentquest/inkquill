# /story_app/app/services/sk_plugins/__init__.py

"""
This package contains modules for setting up various Semantic Kernel plugins.
Each module is responsible for loading its specific prompts and registering
its functions with the main kernel instance.
"""

# Import each plugin setup module to make them accessible when the 'sk_plugins' package is imported.
# This allows sk_kernel_instance.py to do: from .sk_plugins import story_analysis_plugin_setup

from . import story_analysis_plugin_setup
from . import storytelling_plugin_setup
from . import story_structure_plugin_setup
from . import world_generation_plugin_setup

# Optional: Define __all__ if you want to control what 'from .sk_plugins import *' imports.
# For specific imports like 'from .sk_plugins import story_analysis_plugin_setup', __all__ is not strictly necessary.
__all__ = [
    "story_analysis_plugin_setup",
    "storytelling_plugin_setup",
    "story_structure_plugin_setup",
    "world_generation_plugin_setup",
]

