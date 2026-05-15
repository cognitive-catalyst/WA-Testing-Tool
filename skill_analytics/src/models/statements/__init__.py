"""Statement module for handling operations and operands."""

from .operation import OperationType
from .base import Statement
from .expression import ExpressionStatement
from .binary import BinaryStatement
from .exists import ExistsStatement, NotExistsStatement
from .matches import MatchesStatement, NotMatchesStatement
from .contains import ContainsStatement, NotContainsStatement
from .assign import AssignStatement
from .factory import create_statement_from_dict

__all__ = [
    # Statement types
    "Statement",
    "ExpressionStatement",
    "BinaryStatement",
    "ExistsStatement",
    "NotExistsStatement",
    "MatchesStatement",
    "NotMatchesStatement",
    "ContainsStatement",
    "NotContainsStatement",
    "AssignStatement",
    
    # Operation Type
    "OperationType",

    # Factory functions
    "create_statement_from_dict",
]
