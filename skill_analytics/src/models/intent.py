
from dataclasses import dataclass, field
from typing import List, Optional

from src.utils.parse_wxa_ids import parse_long_id

@dataclass
class Intent:
    id: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.id is None:
            self.action_id = None
            self.short_id = None
        elif self.id == "fallback_connect_to_agent":
            self.action_id = "fallback"
            self.short_id = "fallback_connect_to_agent"
        else:
            self.action_id, self.short_id = parse_long_id(self.id)

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return str(self.examples)

    @classmethod
    def from_dict(cls, data: dict) -> 'Intent':
        """Create an Intent instance from a dictionary."""
        return cls(
            id=data["intent"],
            examples=[example_dict["text"] for example_dict in data["examples"]]
        )

    def to_dict(self) -> dict:
        """Convert the intent to a dictionary representation."""
        return {
            "id": self.id,
            "examples": self.examples
        }