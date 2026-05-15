from dataclasses import dataclass
from typing import List

from ..operands import Operand
from .operation import OperationType
from .base import Statement


@dataclass
class BinaryStatement(Statement):
    """Statement for binary operations (AND, OR, EQ, NEQ, GT, LT, GTE, LTE)."""
    operation_type: OperationType
    lhs_operand: Operand
    rhs_operand: Operand
    
    def __post_init__(self):
        if not self.operation_type.is_binary_operation():
            raise ValueError(f"Invalid operation type for BinaryStatement: {self.operation_type}")
    
    def to_dict(self) -> dict:
        return {
            "operation": self.operation_type.value,
            "LHS": self.lhs_operand.value,
            "RHS": self.rhs_operand.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        spel_operation = self.operation_type.get_spel_symbol()
        return f"{self.lhs_operand.spel_expression} {spel_operation} {self.rhs_operand.spel_expression}"

    def get_operands(self) -> List[Operand]:
        return [self.lhs_operand, self.rhs_operand]

