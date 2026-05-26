from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .base import Response, ResponseType, SelectionPolicyType

class PreferenceType(Enum):
    BUTTON = "button"

@dataclass
class Option:
    label: str
    value: str

    def __repr__(self) -> str:
        return f"Option(label='{self.label}', value='{self.value}')"

    def __str__(self) -> str:
        return str(self.label)

    @classmethod
    def from_dict(cls, data: dict) -> 'Option':
        """Create an Option instance from a dictionary."""
        return cls(
            label=data["label"],
            value=data["value"]["input"]["text"]
        )

    def to_dict(self) -> dict:
        """Convert the option to a dictionary representation."""
        return {
            "label": self.label,
            "value": self.value
        }

@dataclass
class OptionResponse(Response):
    options: List[Option]
    preference: PreferenceType
    selection_policy: SelectionPolicyType = field(default=Response._DEFAULT_SELECTION_POLICY)
    repeat_on_reprompt: bool = field(default=Response._DEFAULT_REPEAT_ON_REPROMPT)
    
    def __post_init__(self):
        self.response_type = ResponseType.OPTION
    
    def __str__(self) -> str:
        button_str = '", "'.join([str(option) for option in self.options])
        return f"<Buttons>: [\"{button_str}\"]"

    @classmethod
    def from_dict(cls, data: dict) -> 'OptionResponse':
        """Create an OptionResponse instance from a dictionary."""
        return cls(
            options=[Option.from_dict(option_dict) for option_dict in data["options"]],
            preference=PreferenceType(data.get("preference", "button")),
            selection_policy=cls._get_selection_policy(data),
            repeat_on_reprompt=cls._get_repeat_on_reprompt(data)
        )

    def to_dict(self) -> dict:
        return {
            "response_type": self.response_type.value,
            "preference": self.preference.value,
            "options": [option.to_dict() for option in self.options],
            "selection_policy": self.selection_policy.value,
            "repeat_on_reprompt": self.repeat_on_reprompt,
        }