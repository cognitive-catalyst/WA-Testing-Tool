from dataclasses import dataclass

from .base import Operand, OperandType


@dataclass
class TimeOperand(Operand):

    def __post_init__(self):
        self.operand_type = OperandType.TIME

    @classmethod
    def from_dict(cls, data: dict) -> 'TimeOperand':
        """Create a TimeOperand instance from a dictionary."""
        return cls(value=data["time"]["value"])

    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this time value."""
        return f'"{self.value}"'
