from typing import Type

from .base import Response, ResponseType
from .text import TextResponse
from .user_defined import UserDefinedResponse
from .option import OptionResponse
from .dynamic_option import DynamicOptionResponse
from .date import DateResponse
from .time import TimeResponse
from .speech_to_text import SpeechToTextResponse
from .text_to_speech import TextToSpeechResponse
from .dtmf import DtmfResponse
from .response_from_data_type import ResponseFromDataTypeResponse
from .end_session import EndSessionResponse

RESPONSE_REGISTRY: dict[ResponseType, Type[Response]] = {
    ResponseType.TEXT: TextResponse,
    ResponseType.USER_DEFINED: UserDefinedResponse,
    ResponseType.OPTION: OptionResponse,
    ResponseType.DYNAMIC_OPTION: DynamicOptionResponse,
    ResponseType.DATE: DateResponse,
    ResponseType.TIME: TimeResponse,
    ResponseType.SPEECH_TO_TEXT: SpeechToTextResponse,
    ResponseType.TEXT_TO_SPEECH: TextToSpeechResponse,
    ResponseType.DTMF: DtmfResponse,
    ResponseType.RESPONSE_FROM_DATA_TYPE: ResponseFromDataTypeResponse,
    ResponseType.END_SESSION: EndSessionResponse,
}

def create_response_from_dict(data: dict) -> Response:
    """Create the appropriate response instance from a dictionary based on its type."""
    try:
        response_type = ResponseType(data["response_type"])
    except:
        raise ValueError(f"Unknown response type: {data['response_type']}")

    response_class = RESPONSE_REGISTRY[response_type]
    return response_class.from_dict(data)
