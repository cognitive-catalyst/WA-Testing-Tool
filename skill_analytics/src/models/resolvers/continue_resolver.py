from dataclasses import dataclass

from .base import Resolver, ResolverType


@dataclass
class ContinueResolver(Resolver):
    """Resolver that continues to the next step."""
    
    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.CONTINUE
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContinueResolver':
        """Create a ContinueResolver instance from a dictionary."""
        return cls()
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id
        }
    
    def __repr__(self) -> str:
        return "ContinueResolver()"
