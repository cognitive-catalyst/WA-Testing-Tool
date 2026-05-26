from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from .entity import Entity
from .resolvers import (
    Resolver,
    InvokeActionResolver,
    InvokeActionAndEndResolver,
    create_resolver_from_dict,
)
from .responses import (
    Response,
    TextResponse,
    OptionResponse,
    DynamicOptionResponse,
    create_response_from_dict,
)
from .condition import Condition
from .context import Context
from .handler import Handler
from .question import Question

@dataclass
class Step:
    id: str
    condition: Condition
    context: Context
    responses: List[Response]
    question: Optional[Question]
    handlers: List[Handler]
    resolver: Resolver

    title: Optional[str] = None
    next_step_id: Optional[str] = None
    entity: Optional[Entity] = None

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_dict(cls, data: dict, entities: Dict[str, Entity]) -> 'Step':
        """Create a Step instance from a dictionary."""

        responses: List[Response] = []
        for response_dict in data.get("output", {}).get("generic", []):
            response = create_response_from_dict(response_dict)
            responses.append(response)

        question = None
        entity = None
        if "question" in data:
            question = Question.from_dict(data["question"])
            entity = entities.get(question.entity_id) if question.entity_id else None

        handlers: List[Handler] = []
        for handler_dict in data.get("handlers", []):
            handler = Handler.from_dict(handler_dict)
            handlers.append(handler)

        return cls(
            id=data["step"],
            title=data.get("title"),
            next_step_id=data.get("next_step"),

            condition=Condition.from_dict(data.get("condition", {})),
            context=Context.from_dict(data.get("context", {})),
            responses=responses,
            question=question,
            handlers=handlers,
            resolver=create_resolver_from_dict(data["resolver"]),
            entity=entity,
        )
    
    @property
    def subaction_id(self) -> Optional[str]:
        """Get the subaction ID if this step invokes another action."""
        if not isinstance(self.resolver, (InvokeActionResolver, InvokeActionAndEndResolver)):
            return None
        return self.resolver.subaction_id
    
    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in this step's condition and context."""
        variable_ids = set([])
        variable_ids.update(self.condition.get_all_variable_ids())
        variable_ids.update(self.context.get_all_variable_ids())
        return variable_ids

    def get_display_options_toggle(self) -> Optional[bool]:
        """Check if this step has display options enabled."""
        if self.entity is None:
            return None
        return any(
            isinstance(response, (OptionResponse, DynamicOptionResponse)) 
            for response in self.responses
        )

    def get_repeat_on_reprompt_toggle(self) -> Optional[bool]:
        """Check if any text response in this step has repeat on reprompt enabled."""
        return any(
            isinstance(response, TextResponse) and response.repeat_on_reprompt 
            for response in self.responses
        )