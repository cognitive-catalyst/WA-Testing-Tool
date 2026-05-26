from dataclasses import dataclass, field

from .base import Response, ResponseType, SelectionPolicyType

@dataclass
class SpeechToTextResponse(Response):
    selection_policy: SelectionPolicyType = field(default=Response._DEFAULT_SELECTION_POLICY)
    repeat_on_reprompt: bool = field(default=Response._DEFAULT_REPEAT_ON_REPROMPT)
    
    def __post_init__(self):
        self.response_type = ResponseType.SPEECH_TO_TEXT
    
    def __str__(self) -> str:
        return "<Speech to Text>"

    @classmethod
    def from_dict(cls, data: dict) -> 'SpeechToTextResponse':
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