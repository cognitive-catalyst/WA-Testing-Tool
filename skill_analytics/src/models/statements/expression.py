from dataclasses import dataclass
from typing import List

from ..operands import Operand, ExpressionOperand
from .base import Statement


@dataclass
class ExpressionStatement(Statement):
    """Statement that wraps a single expression operand."""
    expression_operand: ExpressionOperand
    
    def to_dict(self) -> dict:
        return {
            "operation": None,      # an expression does not have an explicit operation
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        return self.expression_operand.spel_expression

    def get_operands(self) -> List[Operand]:
        return [self.expression_operand]
