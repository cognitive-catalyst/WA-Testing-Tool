from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Set

from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

from ..operands import Operand


@dataclass
class Statement(ABC):
    """Base class for all statement types."""
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the statement to a dictionary representation."""
        pass
    
    @property
    @abstractmethod
    def spel_expression(self) -> str:
        """Get the SpEL expression for this statement."""
        pass

    @abstractmethod
    def get_operands(self) -> List[Operand]:
        """Get all operands used in this statement."""
        pass

    def __str__(self) -> str:
        return self.spel_expression

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in this statement's SpEL expression."""
        spel_expression = self.spel_expression
        return parse_variables_from_spel_expression(spel_expression)