"""
Story brainstorm plugin metadata for the storytelling runtime.

This plugin handles generating story concepts and three-act structures based on
user preferences from the story brainstorm interview.
"""

import json
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def kernel_function(*, description: str, name: str):
    """Decorate functions with lightweight metadata for compatibility."""
    def decorator(func):
        func._kernel_function = {"description": description, "name": name}
        return func
    return decorator


class StoryBrainstormPlugin:
    """Plugin for generating story concepts and structures"""

    @kernel_function(
        description="Generate 15 unique story concepts based on user preferences",
        name="generate_story_concepts"
    )
    def generate_story_concepts(
        self,
        genres: str,
        tone: str,
        elements: str,
        char1_role: str,
        char1_name: str,
        char1_background: str,
        char2_role: str,
        char2_name: str,
        char2_background: str
    ) -> str:
        """
        Generate 15 story concepts based on interview responses.
        This function uses the story_concepts_generation.txt prompt template.
        
        Args:
            genres: Comma-separated list of preferred genres
            tone: Comma-separated list of preferred tones
            elements: Comma-separated list of story elements
            char1_role: Character 1 role
            char1_name: Character 1 name
            char1_background: Character 1 background
            char2_role: Character 2 role
            char2_name: Character 2 name
            char2_background: Character 2 background
            
        Returns:
            JSON string containing 15 story concepts with titles and synopses
        """
        # This function will be invoked with the prompt template
        # Prompt rendering is handled by the active storytelling runtime.
        return "Story concepts generation initiated"
    
    @kernel_function(
        description="Generate a three-act story structure from a selected concept and user preferences",
        name="generate_three_act_structure"
    )
    def generate_three_act_structure(
        self,
        title: str,
        synopsis: str,
        genres: str,
        tone: str,
        elements: str,
        char1_role: str,
        char1_name: str,
        char1_background: str,
        char2_role: str,
        char2_name: str,
        char2_background: str
    ) -> str:
        """
        Generate a detailed three-act structure based on selected concept and user preferences.
        This function uses the three_act_structure_generation.txt prompt template.
        
        Args:
            title: Story concept title
            synopsis: Story concept synopsis
            genres: Comma-separated list of preferred genres
            tone: Comma-separated list of preferred tones
            elements: Comma-separated list of story elements
            char1_role: Character 1 role
            char1_name: Character 1 name
            char1_background: Character 1 background
            char2_role: Character 2 role
            char2_name: Character 2 name
            char2_background: Character 2 background
            
        Returns:
            JSON string containing three acts with detailed outlines
        """
        # This function will be invoked with the prompt template
        # Prompt rendering is handled by the active storytelling runtime.
        return "Three-act structure generation initiated"
