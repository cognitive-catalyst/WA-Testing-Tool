from dataclasses import dataclass, field

from .base import Response, ResponseType, SelectionPolicyType

@dataclass
class UserDefinedResponse(Response):
    custom_dict: dict
    selection_policy: SelectionPolicyType = field(default=Response._DEFAULT_SELECTION_POLICY)
    repeat_on_reprompt: bool = field(default=Response._DEFAULT_REPEAT_ON_REPROMPT)
    
    def __post_init__(self):
        self.response_type = ResponseType.USER_DEFINED
    
    def __str__(self) -> str:
        return str(self.custom_dict)

    @classmethod
    def from_dict(cls, data: dict) -> 'UserDefinedResponse':
        return cls(
            custom_dict=data["user_defined"],
            selection_policy=cls._get_selection_policy(data),
            repeat_on_reprompt=cls._get_repeat_on_reprompt(data)
        )

    def to_dict(self) -> dict:
        return {
            "response_type": self.response_type.value,
            "custom_dict": self.custom_dict,
            "selection_policy": self.selection_policy.value,
            "repeat_on_reprompt": self.repeat_on_reprompt,
        }