"""
Resolvers package for Watson Assistant skill analytics.

This package provides classes for parsing and managing different resolver types
in Watson Assistant actions, including continue, replay, invoke action, callout, and end action.
"""

from .base import (
    Resolver,
    ResolverType,
)

from .continue_resolver import (
    ContinueResolver,
)

from .replay_resolver import (
    ReplayResolver,
)

from .invoke_action_resolver import (
    InvokeActionResolver,
)

from .invoke_action_and_end_resolver import (
    InvokeActionAndEndResolver,
)

from .callout_resolver import (
    CalloutResolver,
    RequestMapping,
    ParameterMapping,
)

from .end_action_resolver import (
    EndActionResolver,
)

from .connect_to_agent_resolver import (
    ConnectToAgentResolver,
)

from .fallback_resolver import (
    FallbackResolver,
)

from .factory import (
    create_resolver_from_dict,
    RESOLVER_REGISTRY,
)

__all__ = [
    # Base
    "Resolver",
    "ResolverType",
    # Continue
    "ContinueResolver",
    # Replay (Re-ask)
    "ReplayResolver",
    # Invoke Action (Subaction)
    "InvokeActionResolver",
    # Invoke Action and End
    "InvokeActionAndEndResolver",
    # Callout (Extension)
    "CalloutResolver",
    "RequestMapping",
    "ParameterMapping",
    # End Action
    "EndActionResolver",
    # Connect to Agent
    "ConnectToAgentResolver",
    # Fallback
    "FallbackResolver",
    # Factory
    "create_resolver_from_dict",
    "RESOLVER_REGISTRY",
]
