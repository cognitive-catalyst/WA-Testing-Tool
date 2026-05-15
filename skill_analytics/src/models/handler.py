from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .resolvers import Resolver, create_resolver_from_dict
from .responses import Response, create_response_from_dict

class HandlerType(Enum):
    NOT_FOUND = "not_found"
    NOT_FOUND_MAX_RETRIES = "not_found_max_tries"
    MAX_HITS = "max_hits"

@dataclass
class Handler:
    id: str
    title: Optional[str]
    handler_type: HandlerType
    responses: List[Response]
    resolver: Resolver
    next_handler_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Handler':
        """Create a Handler instance from a dictionary."""
        return cls(
            id=data["handler"],
            title=data.get("title"),
            handler_type=HandlerType(data["type"]),
            responses=[create_response_from_dict(response_dict) for response_dict in data.get("output", {}).get("generic", [])],
            resolver=create_resolver_from_dict(data["resolver"]),
            next_handler_id=data.get("next_handler")
        )

    def to_dict(self) -> dict:
        """Convert the handler to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "handler_type": self.handler_type.value,
            "responses": [response.to_dict() for response in self.responses],
            "resolver": self.resolver.to_dict(),
            "next_handler_id": self.next_handler_id,
        }