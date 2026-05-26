from dataclasses import dataclass
from typing import List

from ..operands import Operand
from .operation import OperationType
from .base import Statement


@dataclass
class MatchesStatement(Statement):
    """Statement for MATCHES operation."""
    lhs_operand: Operand
    rhs_operand: Operand
    
    def to_dict(self) -> dict:
        return {
            "operation": OperationType.MATCHES.value,
            "LHS": self.lhs_operand.value,
            "RHS": self.rhs_operand.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        return f"{self.lhs_operand.spel_expression}.matches({self.rhs_operand.spel_expression})"

    def get_operands(self) -> List[Operand]:
        return [self.lhs_operand, self.rhs_operand]


@dataclass
class NotMatchesStatement(Statement):
    """Statement for NOT_MATCHES operation."""
    lhs_operand: Operand
    rhs_operand: Operand
    
    def to_dict(self) -> dict:
        return {
            "operation": OperationType.NOT_MATCHES.value,
            "LHS": self.lhs_operand.value,
            "RHS": self.rhs_operand.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        matches_expr = f"{self.lhs_operand.spel_expression}.matches({self.rhs_operand.spel_expression})"
        return f"!({matches_expr})"

    def get_operands(self) -> List[Operand]:
        return [self.lhs_operand, self.rhs_operand]
