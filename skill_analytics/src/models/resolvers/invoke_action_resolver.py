from dataclasses import dataclass
from typing import Any, Optional

from .base import Resolver, ResolverType


@dataclass
class InvokeActionResolver(Resolver):
    """Resolver that invokes another action (subaction) and continues."""
    subaction_id: str
    policy: str
    parameters: Optional[Any]
    result_variable_id: str
    ignore_end_action_steps: bool
    
    def __post_init__(self):
        """Set the resolver type after dataclass initialization."""
        self.resolver_type = ResolverType.INVOKE_ANOTHER_ACTION
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InvokeActionResolver':
        """Create an InvokeActionResolver instance from a dictionary."""
        invoke_action_data = data["invoke_action"]
        return cls(
            subaction_id=invoke_action_data["action"],
            policy=invoke_action_data["policy"],
            parameters=invoke_action_data.get("parameters"),
            result_variable_id=invoke_action_data["result_variable"],
            ignore_end_action_steps=invoke_action_data.get("ignore_end_action_steps", False)
        )
    
    def to_dict(self) -> dict:
        """Convert the resolver to a dictionary representation."""
        return {
            "type": self.resolver_type.id,
            "subaction_id": self.subaction_id,
            "policy": self.policy,
            "parameters": self.parameters,
            "result_variable_id": self.result_variable_id,
            "ignore_end_action_steps": self.ignore_end_action_steps
        }
    
    def __repr__(self) -> str:
        return f"InvokeActionResolver(subaction_id={self.subaction_id})"
