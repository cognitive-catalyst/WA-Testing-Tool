from dataclasses import dataclass, field

from .base import Operand, OperandType


@dataclass
class EntityOperand(Operand):
    entity_id: str = field(kw_only=True)

    def __post_init__(self):
        self.operand_type = OperandType.ENTITY

    @classmethod
    def from_dict(cls, data: dict) -> 'EntityOperand':
        """Create an EntityOperand instance from a dictionary."""
        return cls(value=data['value'], entity_id=data["from_entity"])

    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this entity operand."""
        return f"{self.entity_id}(\"{self.value}\")"

