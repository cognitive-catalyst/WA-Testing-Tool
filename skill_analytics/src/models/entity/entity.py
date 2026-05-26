from dataclasses import dataclass
from typing import List

from .value import EntityValue
from .factory import create_entity_value_from_dict

@dataclass
class Entity:
    id: str
    values: List[EntityValue]
    fuzzy_match: bool = False

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_dict(cls, data: dict) -> 'Entity':
        """Create an Entity instance from a dictionary."""
        entity_id = data.get('entity', '')
        fuzzy_match = data.get('fuzzy_match', False)
        
        # Parse all entity values
        values = []
        for value_data in data.get('values', []):
            values.append(
                create_entity_value_from_dict(value_data)
            )
        
        return cls(
            id=entity_id,
            values=values,
            fuzzy_match=fuzzy_match
        )
    
    def to_dict(self) -> dict:
        """Convert the entity to a dictionary representation."""
        return {
            "id": self.id,
            "fuzzy_match": self.fuzzy_match,
            "values": [value.to_dict() for value in self.values]
        }