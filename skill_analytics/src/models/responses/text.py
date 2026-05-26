from dataclasses import dataclass, field
from typing import Set

from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

from ..operands import create_operand_from_dict
from .base import Response, ResponseType, SelectionPolicyType

@dataclass
class TextResponse(Response):
    text: str
    selection_policy: SelectionPolicyType = field(default=Response._DEFAULT_SELECTION_POLICY)
    repeat_on_reprompt: bool = field(default=Response._DEFAULT_REPEAT_ON_REPROMPT)
    
    def __post_init__(self):
        self.response_type = ResponseType.TEXT
    
    def __str__(self) -> str:
        return self.text

    @classmethod
    def from_dict(cls, data: dict) -> 'TextResponse':
        """Create a TextResponse instance from a dictionary."""
        text = "\n".join([TextResponse._parse_value_dict(value_dict) for value_dict in data["values"]])
        return cls(
            text=text,
            selection_policy=cls._get_selection_policy(data),
            repeat_on_reprompt=cls._get_repeat_on_reprompt(data)
        )

    def to_dict(self) -> dict:
        """Convert the text response to a dictionary representation."""
        return {
            "response_type": self.response_type.value,
            "text": self.text,
            "selection_policy": self.selection_policy.value,
            "repeat_on_reprompt": self.repeat_on_reprompt,
        }

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in the response text."""
        variable_ids = parse_variables_from_spel_expression(self.text)
        return variable_ids

    @staticmethod
    def _parse_value_dict(data: dict) -> str:
        """Parse a value dictionary to extract text content."""
        if "text" in data:
            return data["text"]
        
        if "text_expression" in data:
            concat_list = data["text_expression"]["concat"]
            concat_operands = [create_operand_from_dict(operand_dict) for operand_dict in concat_list]
            return "".join([operand.value for operand in concat_operands])
        
        raise ValueError(f"Unable to parse: {data}")