from dataclasses import dataclass
from typing import List

from ..operands import Operand
from .operation import OperationType
from .base import Statement


@dataclass
class ContainsStatement(Statement):
    """Statement for CONTAINS operation."""
    lhs_operand: Operand
    rhs_operand: Operand

    def to_dict(self) -> dict:
        return {
            "operation": OperationType.CONTAINS.value,
            "LHS": self.lhs_operand.value,
            "RHS": self.rhs_operand.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        return f"{self.lhs_operand.spel_expression}.contains({self.rhs_operand.spel_expression})"

    def get_operands(self) -> List[Operand]:
        return [self.lhs_operand, self.rhs_operand]


@dataclass
class NotContainsStatement(Statement):
    """Statement for NOT_CONTAINS operation."""
    lhs_operand: Operand
    rhs_operand: Operand
    
    def to_dict(self) -> dict:
        return {
            "operation": OperationType.NOT_CONTAINS.value,
            "LHS": self.lhs_operand.value,
            "RHS": self.rhs_operand.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        contains_expr = f"{self.lhs_operand.spel_expression}.contains({self.rhs_operand.spel_expression})"
        return f"!({contains_expr})"

    def get_operands(self) -> List[Operand]:
        return [self.lhs_operand, self.rhs_operand]
