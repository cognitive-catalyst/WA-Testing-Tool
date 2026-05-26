from dataclasses import dataclass

from .base import Resolver, ResolverType


@dataclass
class ConnectToAgentResolver(Resolver):
    """Resolver that connects to a live agent."""
    
    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.CONNECT_TO_AGENT
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConnectToAgentResolver':
        """Create a ConnectToAgentResolver instance from a dictionary."""
        return cls()
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id
        }
    
    def __repr__(self) -> str:
        return "ConnectToAgentResolver()"
