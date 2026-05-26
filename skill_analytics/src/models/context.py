from dataclasses import dataclass
from typing import List, Set

from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

from .operands import ExpressionOperand, SkillVariableOperand, create_operand_from_dict
from .statements import AssignStatement, ExpressionStatement, Statement

@dataclass
class Context:
    statements: List[Statement]

    def __bool__(self) -> bool:
        return bool(len(self.statements))

    @classmethod
    def from_dict(cls, data: dict) -> 'Context':
        """Create a Context instance from a dictionary."""

        statements: List[Statement] = []
        for statement_dict in data.get("variables", []):
            
            if "skill_variable" in statement_dict:
                statement = AssignStatement(
                    SkillVariableOperand.from_dict(statement_dict),
                    create_operand_from_dict(statement_dict["value"])
                )
            else:
                statement = ExpressionStatement(
                    ExpressionOperand.from_dict(statement_dict["value"])
                )
            
            statements.append(statement)

        return cls(statements=statements)

    def to_dict(self) -> dict:
        """Convert the context to a dictionary representation."""
        return {
            "statements": [statement.to_dict() for statement in self.statements],
            "spel_expression": self.spel_expression
        }

    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this context."""
        if len(self.statements) == 0:
            return ""
        if len(self.statements) == 1:
            statement = self.statements[0]
            return statement.spel_expression
        
        return " && ".join([f"({statement.spel_expression})" for statement in self.statements])

    def get_all_statements(self) -> List[Statement]:
        """Get all statements in this context."""
        return self.statements

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in this context's SpEL expression."""
        spel_expression = self.spel_expression
        return parse_variables_from_spel_expression(spel_expression)
    