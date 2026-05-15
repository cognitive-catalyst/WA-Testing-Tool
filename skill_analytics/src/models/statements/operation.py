from enum import Enum
from typing import Optional, List

class OperationType(Enum):
    ASSIGN = "assign"
    NOT = "not"
    AND = "and"
    OR = "or"
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"

    ADD = "add"
    SUBTRACT = "subtract"

    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    MATCHES = "matches"
    NOT_MATCHES = "not_matches"
    IN = "in"
    NOT_IN = "not_in"

    def get_spel_symbol(self) -> Optional[str]:
        """
        Return SpEL symbol for binary operations that use infix notation.
        Returns None for operations that use method-call or other syntax.
        """
        _SPEL_SYMBOL_MAP = {
            OperationType.ASSIGN: "=",
            OperationType.AND: "&&",
            OperationType.OR: "||",
            OperationType.EQ: "==",
            OperationType.NEQ: "!=",
            OperationType.GT: ">",
            OperationType.LT: "<",
            OperationType.GTE: ">=",
            OperationType.LTE: "<=",
        }
        return _SPEL_SYMBOL_MAP.get(self)
    
    def is_binary_operation(self) -> bool:
        """Check if this operation uses binary infix notation (e.g., a == b, a && b)."""
        return self != OperationType.ASSIGN and self.get_spel_symbol() is not None
    
    def is_method_operation(self) -> bool:
        """Check if this operation uses method-call syntax (e.g., a.contains(b))."""
        return self in {
            OperationType.CONTAINS,
            OperationType.NOT_CONTAINS,
            OperationType.MATCHES,
            OperationType.NOT_MATCHES,
            OperationType.IN,
            OperationType.NOT_IN,
        }
    
    def is_unary_operation(self) -> bool:
        """Check if this operation takes a single argument (e.g., exists, not_exists)."""
        return self in {
            OperationType.EXISTS,
            OperationType.NOT_EXISTS,
        }

    def is_datetime_operation(self) -> bool:
        """Check if this operation takes a a datetime (e.g., add, subtract)."""
        return self in {
            OperationType.ADD,
            OperationType.SUBTRACT,
        }

    @staticmethod
    def get_negated_operation(operation: 'OperationType') -> 'OperationType':
        """Get the negated version of an operation."""
        _NEGATION_MAP = {
            OperationType.EXISTS: OperationType.NOT_EXISTS,
            OperationType.NOT_EXISTS: OperationType.EXISTS,
            OperationType.CONTAINS: OperationType.NOT_CONTAINS,
            OperationType.NOT_CONTAINS: OperationType.CONTAINS,
            OperationType.MATCHES: OperationType.NOT_MATCHES,
            OperationType.NOT_MATCHES: OperationType.MATCHES,
            OperationType.IN: OperationType.NOT_IN,
            OperationType.NOT_IN: OperationType.IN,
        }
        return _NEGATION_MAP.get(operation, operation)
    
    @staticmethod
    def get_base_operation(operation: 'OperationType') -> 'OperationType':
        """Get the base (non-negated) version of an operation."""
        if operation in {OperationType.NOT_EXISTS, OperationType.NOT_CONTAINS,
                        OperationType.NOT_MATCHES, OperationType.NOT_IN}:
            return OperationType.get_negated_operation(operation)
        return operation

    @staticmethod
    def get_binary_operations() -> List['OperationType']:
        return [op for op in OperationType if op.is_binary_operation()]
    
    @staticmethod
    def get_datetime_operations() -> List['OperationType']:
        return [op for op in OperationType if op.is_datetime_operation()]