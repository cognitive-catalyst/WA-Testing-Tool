from dataclasses import dataclass

from .base import Resolver, ResolverType


@dataclass
class EndActionResolver(Resolver):
    """Resolver that ends the current action."""
    
    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.END_ACTION
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EndActionResolver':
        """Create an EndActionResolver instance from a dictionary."""
        return cls()
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id
        }
    
    def __repr__(self) -> str:
        return "EndActionResolver()"
