from typing import Dict, Type
from .base import Resolver, ResolverType
from .continue_resolver import ContinueResolver
from .replay_resolver import ReplayResolver
from .invoke_action_resolver import InvokeActionResolver
from .invoke_action_and_end_resolver import InvokeActionAndEndResolver
from .callout_resolver import CalloutResolver
from .end_action_resolver import EndActionResolver
from .connect_to_agent_resolver import ConnectToAgentResolver
from .fallback_resolver import FallbackResolver
from .prompt_again import PromptAgainResolver


# Mapping of resolver type IDs to their corresponding classes
RESOLVER_REGISTRY: Dict[ResolverType, Type[Resolver]] = {
    ResolverType.CONTINUE: ContinueResolver,
    ResolverType.REPLAY: ReplayResolver,
    ResolverType.INVOKE_ANOTHER_ACTION: InvokeActionResolver,
    ResolverType.INVOKE_ANOTHER_ACTION_AND_END: InvokeActionAndEndResolver,
    ResolverType.CALLOUT: CalloutResolver,
    ResolverType.END_ACTION: EndActionResolver,
    ResolverType.CONNECT_TO_AGENT: ConnectToAgentResolver,
    ResolverType.FALLBACK: FallbackResolver,
    ResolverType.PROMPT_AGAIN: PromptAgainResolver,
}


def create_resolver_from_dict(data: dict) -> Resolver:
    """Create the appropriate resolver instance from a dictionary based on its type."""
    resolver_type_id = data.get("type", "").lower()
    try:
        resolver_type = ResolverType.from_id(resolver_type_id)
    except:
        raise ValueError(f"Unknown resolver type: {resolver_type_id}")
    
    resolver_class = RESOLVER_REGISTRY.get(resolver_type)
    if resolver_class is None:
        raise ValueError(f"Unknown resolver type: {resolver_type}")
    
    return resolver_class.from_dict(data)


__all__ = [
    "create_resolver_from_dict",
    "RESOLVER_REGISTRY",
]
