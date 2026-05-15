from enum import Enum
from dataclasses import dataclass
from typing import Union

class BuiltInDataType(Enum):
    """Built-in data types supported by Watson Assistant.
    
    Each enum value is a tuple of (id, display_name).
    """
    ANY = ("any", "Any")
    STRING = ("string", "String")
    NUMBER = ("number", "Number")
    BOOLEAN = ("boolean", "Boolean")
    CURRENCY = ("currency", "Currency")
    DATE = ("date", "Date")
    TIME = ("time", "Time")
    PERCENTAGE = ("percentage", "Percentage")
    FREE_TEXT = ("free_text", "Free Text")
    CONFIRMATION = ("yes_no", "Confirmation")
    
    def __init__(self, type_id: str, title: str):
        self._id = type_id
        self._title = title
    
    @property
    def id(self) -> str:
        """Get the unique identifier for this data type."""
        return self._id
    
    @property
    def title(self) -> str:
        """Get a human-readable display name for this data type."""
        return self._title
    
    def is_custom(self) -> bool:
        """Check if this is a custom data type."""
        return False
    
    @classmethod
    def from_id(cls, type_id: str) -> 'BuiltInDataType':
        """Get a BuiltInDataType by its ID string."""
        for member in cls:
            if member.id == type_id:
                return member
        raise ValueError(f"'{type_id}' is not a valid BuiltInDataType")

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.value,
            "title": self.title,
        }


@dataclass
class CustomDataType:
    """Represents a custom data type defined in the assistant configuration."""
    _id: str
    title: str
    entity_id: str
    
    @property
    def id(self) -> str:
        """Get the unique identifier for this data type."""
        return self._id
    
    def is_custom(self) -> bool:
        """Check if this is a custom data type."""
        return True
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CustomDataType':
        """Create a CustomDataType instance from a dictionary."""
        return cls(
            _id=data["data_type"],
            title=data["title"],
            entity_id=data["entity"]
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self._id,
            "title": self.title,
            "entity_id": self.entity_id
        }
    
    def __str__(self) -> str:
        return self.title
    
    def __repr__(self) -> str:
        return f"CustomDataType(id='{self._id}', title='{self.title}', entity_id='{self.entity_id}')"


# Type alias for any data type
DataType = Union[BuiltInDataType, CustomDataType]
