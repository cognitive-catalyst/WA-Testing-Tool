from typing import Any

from src.models.assistant import Assistant
from src.output_handlers import OutputFormat, create_output_handler


class IntentAnalyzer:
    """Analyzer for extracting and analyzing intent metadata from an Assistant."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def intent_usage(
        self,
        *action_ids,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        
        results = []
        for action in self.assistant.actions.values():
            if len(action_ids) and action.id not in action_ids:
                continue

            intent = action.intent
            for example in intent.examples:
                results.append({
                    "action_id": action.id,
                    "action_title": action.title,
                    "intent_id": intent.id,
                    "utterance": example
                })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)