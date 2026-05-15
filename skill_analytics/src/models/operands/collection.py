from dataclasses import dataclass

from .base import Operand, OperandType
from .entity import EntityOperand


@dataclass
class CollectionOperand(Operand):
    
    def __post_init__(self):
        self.operand_type = OperandType.COLLECTION

    @classmethod
    def from_dict(cls, data: dict) -> 'CollectionOperand':
        """Create a CollectionOperand instance from a dictionary."""
        return cls(value=[
            EntityOperand.from_dict(entity_dict) for entity_dict in data['collection']
        ])

    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this collection."""
        list_str = ', '.join(operand.spel_expression for operand in self.value)
        return f"[{list_str}]"

