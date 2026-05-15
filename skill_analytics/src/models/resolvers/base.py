from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ResolverType(Enum):
    """Enum representing different resolver types in Watson Assistant."""
    CONTINUE = ("continue", "Continue to next step")
    REPLAY = ("replay", "Re-ask")
    INVOKE_ANOTHER_ACTION = ("invoke_another_action", "Go to a subaction")
    INVOKE_ANOTHER_ACTION_AND_END = ("invoke_another_action_and_end", "Go to a subaction and end the current action")
    CALLOUT = ("callout", "Use an extension")
    END_ACTION = ("end_action", "End the action")
    CONNECT_TO_AGENT = ("connect_to_agent", "Connect to agent")
    FALLBACK = ("fallback", "Fallback")
    PROMPT_AGAIN = ("prompt_again", "Prompt Again")
    
    def __init__(self, type_id: str, title: str):
        self._id = type_id
        self._title = title
    
    @property
    def id(self) -> str:
        """Get the unique identifier for this resolver type."""
        return self._id
    
    @property
    def title(self) -> str:
        """Get a human-readable display name for this resolver type."""
        return self._title
    
    @classmethod
    def from_id(cls, type_id: str) -> 'ResolverType':
        """Get a ResolverType by its ID string."""
        for member in cls:
            if member.id == type_id:
                return member
        raise ValueError(f"'{type_id}' is not a valid ResolverType")


@dataclass
class Resolver(ABC):
    """Abstract base class for all resolver types."""
    resolver_type: ResolverType = field(init=False)
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'Resolver':
        """Create a resolver instance from a dictionary."""
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.resolver_type.id})"