from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ResponseCollectionBehaviorType(Enum):
    ALWAYS_ASK = "always_ask"
    NEVER_ASK = "never_ask"
    OPTIONALLY_ASK = "optionally_ask"

@dataclass
class Question:
    """
    This part of the assistant JSON is a mix of a bunch of things. It's not 1-to-1 with the UI
    """

    entity_id: Optional[str]
    # data_type: Optional[DataType]
    max_tries: int
    response_collection_behavior: ResponseCollectionBehaviorType
    allow_topic_switch: bool
    collect_verbatim_response: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """Create a Question instance from a dictionary."""
        return cls(
            entity_id=data.get("entity"),
            # data_type=DataType data.get("data_type"),     # This would take a lot of work to validate properly, and I'm not sure if anyone even cares
            max_tries=data.get("max_tries", 3),
            response_collection_behavior=ResponseCollectionBehaviorType(data.get("response_collection_behavior", "optionally_ask")),
            allow_topic_switch=data.get("allow_topic_switch", False),
            collect_verbatim_response=data.get("collect_verbatim_response", False)
        )

    def to_dict(self) -> dict:
        """Convert the question to a dictionary representation."""
        return {
            "entity_id": self.entity_id,
            "max_tries": self.max_tries,
            "response_collection_behavior": self.response_collection_behavior.value,
            "allow_topic_switch": self.allow_topic_switch,
            "collect_verbatim_response": self.collect_verbatim_response,
        }