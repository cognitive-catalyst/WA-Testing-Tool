from dataclasses import dataclass
from typing import List

from ..operands import Operand
from .operation import OperationType
from .base import Statement


@dataclass
class ExistsStatement(Statement):
    """Statement for EXISTS operation."""
    operand: Operand
    
    def to_dict(self) -> dict:
        return {
            "operation": OperationType.EXISTS.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        return f"{self.operand.spel_expression} != null"

    def get_operands(self) -> List[Operand]:
        return [self.operand]


@dataclass
class NotExistsStatement(Statement):
    """Statement for NOT_EXISTS operation."""
    operand: Operand
    
    def to_dict(self) -> dict:
        return {
            "operation": OperationType.NOT_EXISTS.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        return f"{self.operand.spel_expression} == null"

    def get_operands(self) -> List[Operand]:
        return [self.operand]

