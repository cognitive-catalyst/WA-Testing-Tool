from dataclasses import dataclass, field
from typing import List, Set

from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

from .statements import OperationType, Statement, create_statement_from_dict

@dataclass
class Condition:
    operation_type: OperationType = OperationType.AND
    condition_group: List['Condition'] = field(default_factory=list)
    statements: List[Statement] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(len(self.condition_group + self.statements))

    @classmethod
    def from_dict(cls, data: dict) -> 'Condition':
        """Create a Condition instance from a dictionary."""
        if ("and" not in data) and ("or" not in data):
            statements = [create_statement_from_dict(data)]
            return cls(statements=[statement for statement in statements if statement])
        
        operation_str, condition_group_list = list(data.items())[0]
        operation_type = OperationType(operation_str)
        
        # Recursively go down condition group
        return cls(
            operation_type=operation_type,
            condition_group=[Condition.from_dict(condition_dict) for condition_dict in condition_group_list]
        )

    def to_dict(self) -> dict:
        """Convert the condition to a dictionary representation."""
        return {
            "operation_type": self.operation_type.value,
            "condition_group": [condition.to_dict() for condition in self.condition_group],
            "statements": [statement.to_dict() for statement in self.statements],
            "spel_expression": self.spel_expression
        }

    def get_all_statements(self) -> List[Statement]:
        """Recursively get all statements from this condition and nested condition groups."""
        statements = list(self.statements)
        for condition in self.condition_group:
            statements.extend(condition.get_all_statements())
        return statements

    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this condition."""
        obj_list = self.statements + self.condition_group
        
        spel_clauses = [statement.spel_expression for statement in obj_list]
        spel_clauses = [exp for exp in spel_clauses if exp != ""]

        if len(spel_clauses) == 0:
            return ""
        if len(spel_clauses) == 1:
            return spel_clauses[0]
        
        op_symbol = self.operation_type.get_spel_symbol()
        return f" {op_symbol} ".join([
            f"({clause})" for clause in spel_clauses
        ])

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in this condition's SpEL expression."""
        spel_expression = self.spel_expression
        return parse_variables_from_spel_expression(spel_expression)
