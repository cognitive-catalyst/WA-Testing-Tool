from dataclasses import dataclass
from typing import List

from ..operands import Operand, SkillVariableOperand
from .operation import OperationType
from .base import Statement


@dataclass
class AssignStatement(Statement):
    """Statement for ASSIGN operation."""
    lhs_operand: SkillVariableOperand
    rhs_operand: Operand
    
    def to_dict(self) -> dict:
        """Convert the assign statement to a dictionary representation."""
        return {
            "operation": OperationType.ASSIGN.value,
            "LHS": self.lhs_operand.value,
            "RHS": self.rhs_operand.value,
            "spel_expression": self.spel_expression
        }
    
    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this assignment."""
        spel_operation = OperationType.ASSIGN.get_spel_symbol()
        return f"{self.lhs_operand.spel_expression} {spel_operation} {self.rhs_operand.spel_expression}"

    def get_operands(self) -> List[Operand]:
        """Get the left-hand and right-hand operands of this assignment."""
        return [self.lhs_operand, self.rhs_operand]

