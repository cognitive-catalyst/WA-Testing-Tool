from dataclasses import dataclass
from typing import Any, Optional

from .base import Variable, VariableType
from ..data_types import DataTypeRegistry, CustomDataType, DataType


@dataclass
class SkillVariable(Variable):

    def __post_init__(self):
        self.variable_type = VariableType.SKILL

    @classmethod
    def from_dict(cls, data: dict, registry: DataTypeRegistry) -> 'SkillVariable':
        """Create a SkillVariable instance from a dictionary."""
        data_type_id = data.get("data_type", "any")
        
        # Use registry to resolve and validate the data type
        data_type = registry.resolve(data_type_id)
        
        return cls(
            id=data["variable"],
            title=data.get("title"),
            description=data.get("description"),
            data_type=data_type,
            initial_value=SkillVariable._parse_initial_value(
                data.get("initial_value", {})
            ),
            is_protected=data.get("privacy", {}).get("enabled", False),
        )

    def to_dict(self) -> dict:
        """Convert the skill variable to a dictionary representation."""
        return {
            "uid": self.uid,
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.variable_type.value,
            "is_protected": self.is_protected,
            "data_type": self.data_type.id,
            "is_custom_data_type": self.data_type.is_custom(),
            "initial_value": self.initial_value,
        }
    
    def get_data_type_title(self) -> str:
        """Get a human-readable title for the data type."""
        return self.data_type.title
    
    def is_custom_data_type(self) -> bool:
        """Check if this variable uses a custom data type."""
        return self.data_type.is_custom()
    
    def get_custom_data_type(self) -> Optional[CustomDataType]:
        """Get the CustomDataType object if this is a custom type."""
        if isinstance(self.data_type, CustomDataType):
            return self.data_type
        return None

    @staticmethod
    def _parse_initial_value(value_obj: dict) -> Optional[Any]:
        """Parse the initial value from the variable object."""
        
        if "scalar" in value_obj:
            value = value_obj["scalar"]
            return value

        if "expression" in value_obj:
            value = value_obj["expression"]
            return value

        return None

