from dataclasses import dataclass

from .base import Operand, OperandType


@dataclass
class IntentOperand(Operand):

    def __post_init__(self):
        self.operand_type = OperandType.INTENT

    @classmethod
    def from_dict(cls, data: dict) -> 'IntentOperand':
        """Create an IntentOperand instance from a dictionary."""
        return cls(value=data['intent'])

    @property
    def spel_expression(self) -> str:
        """Get the SpEL expression value."""
        return self.value
