from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum

from ..data_types import DataType, BuiltInDataType

class VariableType(Enum):
    SKILL = "skill_variable"
    STEP = "step_variable"
    RESULT = "result_variable"
    SYSTEM = "system_variable"


@dataclass
class Variable(ABC):
    """Abstract base class representing a Watson Assistant variable."""
    id: str
    title: Optional[str]
    description: Optional[str]
    is_protected: bool
    variable_type: VariableType = field(init=False)
    data_type: DataType = BuiltInDataType.ANY
    initial_value: Optional[Any] = None
    
    @property
    def uid(self) -> str:
        """Get the unique identifier for this variable."""
        return self.id
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict, *args, **kwargs) -> 'Variable':
        """Create a Variable instance from a dictionary."""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the variable to a dictionary representation."""
        pass
