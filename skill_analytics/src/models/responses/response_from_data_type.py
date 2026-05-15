from dataclasses import dataclass, field

from .base import Response, ResponseType, SelectionPolicyType

@dataclass
class ResponseFromDataTypeResponse(Response):
    selection_policy: SelectionPolicyType = field(default=Response._DEFAULT_SELECTION_POLICY)
    repeat_on_reprompt: bool = field(default=Response._DEFAULT_REPEAT_ON_REPROMPT)
    
    def __post_init__(self):
        self.response_type = ResponseType.RESPONSE_FROM_DATA_TYPE
    
    def __str__(self) -> str:
        return "<Response from Data Type>"

    @classmethod
    def from_dict(cls, data: dict) -> 'ResponseFromDataTypeResponse':
        return cls(
            selection_policy=cls._get_selection_policy(data),
            repeat_on_reprompt=cls._get_repeat_on_reprompt(data)
        )

    def to_dict(self) -> dict:
        return {
            "response_type": self.response_type.value,
            "selection_policy": self.selection_policy.value,
            "repeat_on_reprompt": self.repeat_on_reprompt,
        }