from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Set

from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

class OperandType(Enum):
    SCALAR = "scalar"
    TIME = "time"
    EXPRESSION = "expression"
    SKILL_VARIABLE = "skill_variable"
    SYSTEM_VARIABLE = "system_variable"
    VARIABLE = "variable"
    INTENT = "intent"
    COLLECTION = "collection"
    ENTITY = "from_entity"


@dataclass
class Operand(ABC):
    operand_type: OperandType = field(init=False)
    value: Any

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'Operand':
        """Create an operand instance from a dictionary."""
        pass

    def to_dict(self) -> dict:
        """Convert the operand to a dictionary representation."""
        return {
            "operand_type": self.operand_type.value,
            "value": self.value,
            "SpEL_expression": self.spel_expression
        }

    @property
    @abstractmethod
    def spel_expression(self) -> str:
        """Get the SpEL expression representation of this operand."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.operand_type.value})"

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in this operand's SpEL expression."""
        spel_expression = self.spel_expression
        return parse_variables_from_spel_expression(spel_expression)

