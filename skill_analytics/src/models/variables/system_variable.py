from dataclasses import dataclass

from .base import Variable, VariableType

SYSTEM_VARIABLE_IDS = [
    "fallback_reason", 
    "digressed_from", 
    "no_action_matches_count",
    "system_session_history",
    "system_current_date",
    "system_current_time",
    "system_integrations",
    "system_now",
    "current_time",
    "system_timezone"
]

@dataclass
class SystemVariable(Variable):

    def __post_init__(self):
        self.variable_type = VariableType.SYSTEM

    @classmethod
    def from_dict(cls, data: dict) -> 'SystemVariable':
        """Create a SystemVariable instance from a dictionary."""
        return cls(
            id=data['variable'],
            title=data.get("title"),
            description=data.get("description"),
            is_protected=data.get("privacy", {}).get("enabled", False),
        )

    def to_dict(self) -> dict:
        """Convert the system variable to a dictionary representation."""
        return {
            "uid": self.uid,
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.variable_type.value,
            "is_protected": self.is_protected,
        }
