from dataclasses import dataclass

from .base import Resolver, ResolverType


@dataclass
class PromptAgainResolver(Resolver):
    """Resolver that prompts the user again."""
    
    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.PROMPT_AGAIN
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PromptAgainResolver':
        """Create a PromptAgainResolver instance from a dictionary."""
        return cls()
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id
        }
    
    def __repr__(self) -> str:
        return "PromptAgainResolver()"
