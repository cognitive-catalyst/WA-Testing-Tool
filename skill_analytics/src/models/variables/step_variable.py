from dataclasses import dataclass, field

from src.utils.parse_wxa_ids import build_long_id

from .base import Variable, VariableType


@dataclass
class StepVariable(Variable):
    action_id: str = field(kw_only=True)

    def __post_init__(self):
        self.variable_type = VariableType.STEP

    @classmethod
    def from_dict(cls, data: dict, action_id: str) -> 'StepVariable':
        """Create a StepVariable instance from a dictionary."""
        return cls(
            id=data["variable"],
            action_id=action_id,
            title=data.get("title"),
            description=data.get("description"),
            is_protected=data.get("privacy", {}).get("enabled", False),
        )

    def to_dict(self) -> dict:
        """Convert the step variable to a dictionary representation."""
        return {
            "uid": self.uid,
            "id": self.id,
            "action_id": self.action_id,
            "step_id": self.step_id,
            "title": self.title,
            "description": self.description,
            "type": self.variable_type.value,
            "is_protected": self.is_protected,
        }

    @property
    def uid(self) -> str:
        """Get the unique identifier combining action ID and variable ID."""
        return build_long_id(self.action_id, self.id)

    @property
    def step_id(self) -> str:
        """Get the step ID (same as variable ID for step variables)."""
        return self.id

