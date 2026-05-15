from typing import Type
from .value import PatternsEntityValue, SynonymsEntityValue, EntityValueType, EntityValue

ENTITY_VALUE_REGISTRY: dict[EntityValueType, Type[EntityValue]] = {
    EntityValueType.SYNONYMS: SynonymsEntityValue,
    EntityValueType.PATTERNS: PatternsEntityValue,
}

def create_entity_value_from_dict(data: dict) -> EntityValue:
    """Create an EntityValue instance from a dictionary based on the value type."""
    for entity_value_type, entity_value_class in ENTITY_VALUE_REGISTRY.items():
        key = entity_value_type.value
        if key in data:
            return entity_value_class.from_dict(data)
    
    # If no matching key found, raise an error
    raise ValueError(f"Unknown entity value type. Data keys: {list(data.keys())}")