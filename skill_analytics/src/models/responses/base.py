
from abc import ABC, abstractmethod
from enum import Enum
from typing import Set

class ResponseType(Enum):
    TEXT = "text"
    USER_DEFINED = "user_defined"
    OPTION = "option"
    DYNAMIC_OPTION = "response_from_variable"
    DATE = "date"
    TIME = "time"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
    DTMF = "dtmf"
    RESPONSE_FROM_DATA_TYPE = "response_from_data_type"
    END_SESSION = "end_session"

class SelectionPolicyType(Enum):
    SEQUENTIAL = "sequential"
    INCREMENTAL = "incremental"

class Response(ABC):
    response_type: ResponseType
    selection_policy: SelectionPolicyType
    repeat_on_reprompt: bool
    
    _DEFAULT_SELECTION_POLICY: SelectionPolicyType = SelectionPolicyType.SEQUENTIAL
    _DEFAULT_REPEAT_ON_REPROMPT: bool = False

    @classmethod
    def _get_selection_policy(cls, data: dict) -> SelectionPolicyType:
        """Get selection_policy from data dict with default fallback."""
        policy_str = data.get("selection_policy")
        if policy_str is None:
            return cls._DEFAULT_SELECTION_POLICY
        return SelectionPolicyType(policy_str)
    
    @classmethod
    def _get_repeat_on_reprompt(cls, data: dict) -> bool:
        """Get repeat_on_reprompt from data dict with default fallback."""
        return data.get("repeat_on_reprompt", cls._DEFAULT_REPEAT_ON_REPROMPT)

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'Response':
        """Create a Response instance from a dictionary."""
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the response to a dictionary representation."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Get string representation of the response."""
        pass

    def get_all_variable_ids(self) -> Set[str]:
        """Extract all variable IDs referenced in this response."""
        return set([])