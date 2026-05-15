from dataclasses import dataclass, field
from typing import List

from .base import Resolver, ResolverType


@dataclass
class ReplayResolver(Resolver):
    """Resolver that replays previous steps."""
    steps_to_replay: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.REPLAY
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReplayResolver':
        """Create a ReplayResolver instance from a dictionary."""
        clear_data = data["clear"]
        return cls(
            steps_to_replay=[var_dict["variable"] for var_dict in clear_data]
        )
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id,
            "steps_to_replay": self.steps_to_replay,
        }
    
    def __repr__(self) -> str:
        return f"ReplayResolver(steps_to_replay={self.steps_to_replay})"
