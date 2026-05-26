from dataclasses import dataclass

from .base import Operand, OperandType


@dataclass
class ExpressionOperand(Operand):

    def __post_init__(self):
        self.operand_type = OperandType.EXPRESSION

    @classmethod
    def from_dict(cls, data: dict) -> 'ExpressionOperand':
        """Create an ExpressionOperand instance from a dictionary."""
        return cls(value=data["expression"])

    @property
    def spel_expression(self) -> str:
        """Get the SpEL expression value."""
        return self.value

