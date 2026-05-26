from typing import Optional, Type

from ..operands import ExpressionOperand, create_operand_from_dict
from .base import Statement
from .operation import OperationType
from .expression import ExpressionStatement
from .binary import BinaryStatement
from .exists import ExistsStatement, NotExistsStatement
from .matches import MatchesStatement, NotMatchesStatement
from .contains import ContainsStatement, NotContainsStatement
from .assign import AssignStatement

# Map operation types to their statement classes
STATEMENT_REGISTRY: dict[OperationType, Type[Statement]] = {
    OperationType.EXISTS: ExistsStatement,
    OperationType.NOT_EXISTS: NotExistsStatement,
    OperationType.CONTAINS: ContainsStatement,
    OperationType.NOT_CONTAINS: NotContainsStatement,
    OperationType.MATCHES: MatchesStatement,
    OperationType.NOT_MATCHES: NotMatchesStatement,
    OperationType.IN: ContainsStatement,  # "in" maps to ContainsStatement
    OperationType.NOT_IN: NotContainsStatement,  # "not_in" maps to NotContainsStatement
}


def create_statement_from_dict(data: dict) -> Optional[Statement]:
    """Create the appropriate statement instance from a dictionary based on its operation type."""
    if not data:
        return None
    
    # FIXME: this is for these built-in conditions like trigger words
    # I don't really know how to parse it correctly, and I don't think there's much value
    # so I don't want to deal with this case right now
    if "entity" in data:
        return None

    # This occurs on an action condition, so we can just skip this
    if "intent" in data:
        return None

    # Handle binary operations (eq, neq, gt, lt, gte, lte)
    for operation in OperationType.get_binary_operations():
        field = operation.value
        if field in data:
            lhs_dict, rhs_dict = data[field]
            return BinaryStatement(
                operation_type=OperationType(field),
                lhs_operand=create_operand_from_dict(lhs_dict),
                rhs_operand=create_operand_from_dict(rhs_dict)
            )

    # Handle expression statements
    if "expression" in data:
        return ExpressionStatement(
            expression_operand=ExpressionOperand.from_dict(data)
        )

    def parse_match_exist_contain(sub_data: dict, negated: bool = False) -> Statement:
        """Parse match, exist, and contain operations."""
        for operation_type, statement_class in STATEMENT_REGISTRY.items():
            key = operation_type.value
            if key in sub_data:
                # Handle unary operations (exists, not_exists)
                if operation_type.is_unary_operation():
                    operand_dict = sub_data[key]
                    operand = create_operand_from_dict(operand_dict)
                    return statement_class(operand)
                
                # Handle binary operations (contains, matches, in, etc.)
                else:
                    lhs_dict, rhs_dict = sub_data[key]
                    lhs_operand = create_operand_from_dict(lhs_dict)
                    rhs_operand = create_operand_from_dict(rhs_dict)
                    return statement_class(lhs_operand, rhs_operand)
        
        raise ValueError(f"Unknown statement type. Data keys: {list(sub_data.keys())}")

    # Handle negated operations
    if "not" in data:
        return parse_match_exist_contain(data["not"], negated=True)
    
    return parse_match_exist_contain(data, negated=False)
