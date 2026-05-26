
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class EntityValueType(Enum):
    SYNONYMS = "synonyms"
    PATTERNS = "patterns"

@dataclass
class EntityValue(ABC):
    value_type: EntityValueType = field(init=False)
    value: str

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'EntityValue':
        """Create an EntityValue instance from a dictionary."""
        pass

    def to_dict(self) -> dict:
        """Convert the entity value to a dictionary representation."""
        return {
            "value_type": self.value_type.value,
            "value": self.value
        }


@dataclass
class SynonymsEntityValue(EntityValue):
    synonyms: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.value_type = EntityValueType.SYNONYMS

    @classmethod
    def from_dict(cls, data: dict) -> 'SynonymsEntityValue':
        """Create a SynonymsEntityValue instance from a dictionary."""
        return cls(
            value=data["value"],
            synonyms=data["synonyms"]
        )

    def to_dict(self) -> dict:
        """Convert the synonyms entity value to a dictionary representation."""
        return {
            "value_type": self.value_type.value,
            "value": self.value,
            "synonyms": self.synonyms,
        }


@dataclass
class PatternsEntityValue(EntityValue):
    patterns: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.value_type = EntityValueType.PATTERNS

    @classmethod
    def from_dict(cls, data: dict) -> 'PatternsEntityValue':
        """Create a PatternsEntityValue instance from a dictionary."""
        return cls(
            value=data["value"],
            patterns=data["patterns"]
        )

    def to_dict(self) -> dict:
        """Convert the patterns entity value to a dictionary representation."""
        return {
            "value_type": self.value_type.value,
            "value": self.value,
            "patterns": self.patterns,
        }