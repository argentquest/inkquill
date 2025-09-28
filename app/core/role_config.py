# /app/core/role_config.py
"""
Role configuration for story element associations.
Defines predefined roles for different element types.
"""

from typing import Dict, List, Set

# Predefined roles for different element types
PREDEFINED_ROLES: Dict[str, Dict[str, List[str]]] = {
    "character": {
        "story": [
            "protagonist",
            "antagonist",
            "deuteragonist",
            "mentor",
            "love interest",
            "sidekick",
            "comic relief",
            "narrator",
            "rival",
            "ally",
            "villain",
            "anti-hero",
            "supporting character",
            "minor character"
        ],
        "act": [
            "lead",
            "featured",
            "introduced",
            "developed",
            "transformed",
            "confronted",
            "resolved",
            "absent",
            "mentioned",
            "flashback",
            "cameo"
        ],
        "scene": [
            "present",
            "active",
            "speaking",
            "observing",
            "reacting",
            "entering",
            "exiting",
            "central focus",
            "background",
            "mentioned",
            "offscreen",
            "flashback",
            "viewpoint character"
        ]
    },
    "location": {
        "story": [
            "primary setting",
            "secondary setting",
            "backdrop",
            "origin",
            "destination",
            "recurring location",
            "symbolic location",
            "flashback setting",
            "dream location",
            "parallel world"
        ],
        "act": [
            "setting",
            "battlefield",
            "meeting place",
            "hideout",
            "passage",
            "discovery site",
            "confrontation site",
            "sanctuary",
            "prison",
            "threshold"
        ],
        "scene": [
            "primary location",
            "secondary location", 
            "entrance point",
            "exit point",
            "interaction space",
            "observation point",
            "hiding place",
            "meeting spot",
            "conflict zone",
            "safe haven",
            "transition area",
            "atmosphere setter"
        ]
    },
    "lore_item": {
        "story": [
            "macguffin",
            "key artifact",
            "weapon",
            "tool",
            "symbol",
            "heirloom",
            "quest item",
            "power source",
            "document",
            "curse object",
            "blessing object"
        ],
        "act": [
            "featured item",
            "discovered",
            "used",
            "lost",
            "found",
            "destroyed",
            "created",
            "transformed",
            "hidden",
            "revealed"
        ],
        "scene": [
            "featured",
            "used",
            "mentioned",
            "displayed",
            "interacted with",
            "discovered",
            "hidden",
            "revealed",
            "activated",
            "deactivated",
            "examined",
            "ignored",
            "prop"
        ]
    }
}

# Maximum number of custom roles allowed per association
MAX_CUSTOM_ROLES = 5

# Role validation rules
ROLE_RULES = {
    "max_length": 50,
    "min_length": 2,
    "allowed_characters": "alphanumeric, spaces, hyphens, apostrophes",
    "max_roles_per_association": 10
}

def get_predefined_roles(element_type: str, container_type: str) -> List[str]:
    """
    Get predefined roles for a specific element and container type.
    
    Args:
        element_type: Type of element (character, location, lore_item)
        container_type: Type of container (story, act, scene)
    
    Returns:
        List of predefined role strings
    """
    return PREDEFINED_ROLES.get(element_type, {}).get(container_type, [])

def validate_role(role: str) -> bool:
    """
    Validate a role string according to the rules.
    
    Args:
        role: Role string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not role or not isinstance(role, str):
        return False
    
    role = role.strip()
    
    # Check length
    if len(role) < ROLE_RULES["min_length"] or len(role) > ROLE_RULES["max_length"]:
        return False
    
    # Check characters (alphanumeric, spaces, hyphens, apostrophes)
    import re
    if not re.match(r"^[a-zA-Z0-9\s\-']+$", role):
        return False
    
    return True

def normalize_role(role: str) -> str:
    """
    Normalize a role string for consistency.
    
    Args:
        role: Role string to normalize
    
    Returns:
        Normalized role string
    """
    return role.strip().lower()

def is_predefined_role(role: str, element_type: str, container_type: str) -> bool:
    """
    Check if a role is predefined for the given context.
    
    Args:
        role: Role to check
        element_type: Type of element
        container_type: Type of container
    
    Returns:
        True if predefined, False if custom
    """
    normalized_role = normalize_role(role)
    predefined = get_predefined_roles(element_type, container_type)
    return normalized_role in [normalize_role(r) for r in predefined]