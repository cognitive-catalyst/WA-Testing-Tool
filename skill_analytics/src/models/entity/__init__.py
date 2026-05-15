"""Entity module for parsing and managing Watson Assistant entities.

This module provides classes for working with entities and their values,
including synonyms and pattern-based entity values.
"""

from .entity import Entity
from .value import (
    EntityValue,
    EntityValueType,
    SynonymsEntityValue,
    PatternsEntityValue,
)
from .factory import (
    create_entity_value_from_dict,
    ENTITY_VALUE_REGISTRY,
)

__all__ = [
    # Main entity class
    "Entity",
    
    # Entity value classes
    "EntityValue",
    "EntityValueType",
    "SynonymsEntityValue",
    "PatternsEntityValue",
    
    # Factory functions and registry
    "create_entity_value_from_dict",
    "ENTITY_VALUE_REGISTRY",
]
