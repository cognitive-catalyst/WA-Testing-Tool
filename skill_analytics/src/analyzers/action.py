from typing import Any

from src.models.assistant import Assistant
from src.models.handler import HandlerType
from src.output_handlers import OutputFormat, create_output_handler
from src.utils.parse_wxa_ids import build_long_id

class ActionAnalyzer:
    """Analyzer for extracting and analyzing action metadata from an Assistant."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def action_metadata(
        self,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        
        results = []
        for action in self.assistant.actions.values():
            results.append({
                "action_id": action.id,
                "action_title": action.title,
                "intent_id": action.intent.id,
                "num_steps": len(action.steps),
                "condition_spel_expression": action.condition.spel_expression,
                **action.settings.to_dict()
            })
    
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def customer_response_settings(
        self,
        *action_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON
    ) -> Any:

        results = []
        for action in self.assistant.actions.values():
            if len(action_ids) and action.id not in action_ids:
                continue
            for i, step in enumerate(action.steps):
                if step.question:
                    variable = self.assistant.get_variable(step.id, action_id=action.id)
                    if variable is None:
                        print(f"Warning: Variable {step.id} from action {action.title} and step number {i+1} is missing from assistant variables.")
                    
                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": step.id,
                        "step_title": step.title,
                        "step_number": i+1,
                        "action_step_id": build_long_id(action.id, step.id),
                        "customer_response_collection_behavior": step.question.response_collection_behavior.value,
                        "display_options_toggle": step.get_display_options_toggle(),
                        "is_protected": variable.is_protected if variable else False
                    })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def validation_settings(
        self,
        *action_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON
    ) -> Any:

        results = []
        for action in self.assistant.actions.values():
            if len(action_ids) and action.id not in action_ids:
                continue
            for i, step in enumerate(action.steps):
                for handler in step.handlers:
                    if handler.handler_type == HandlerType.NOT_FOUND:
                        results.append({
                            "action_id": action.id,
                            "action_title": action.title,
                            "step_id": step.id,
                            "step_title": step.title,
                            "step_number": i+1,
                            "action_step_id": build_long_id(action.id, step.id),
                            "validation_responses": str([str(response) for response in handler.responses]),
                            "max_tries": step.question.max_tries if step.question else None,
                            "repeat_on_reprompt": step.get_repeat_on_reprompt_toggle()
                        })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def condition_usage(
        self,
        *action_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON
    ) -> Any:
        """Report all conditions used in the assistant."""
        results = []
        
        for action in self.assistant.actions.values():
            if len(action_ids) and action.id not in action_ids:
                continue
            
            # Action-level conditions
            for statement in action.condition.get_all_statements():
                results.append({
                    "action_id": action.id,
                    "action_title": action.title,
                    "step_id": None,
                    "step_title": None,
                    "step_number": 0,
                    "action_step_id": None,
                    "source": "action condition",
                    **statement.to_dict()
                })
            
            # Step-level conditions
            for i, step in enumerate(action.steps):
                for statement in step.condition.get_all_statements():
                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": step.id,
                        "step_title": step.title,
                        "step_number": i+1,
                        "action_step_id": build_long_id(action.id, step.id),
                        "source": "step condition",
                        **statement.to_dict()
                    })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def context_usage(
        self,
        *action_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON
    ) -> Any:
        """Report all context statements used in the assistant."""
        results = []
        
        for action in self.assistant.actions.values():
            if len(action_ids) and action.id not in action_ids:
                continue
            
            # Step-level context (context is only at step level, not action level)
            for i, step in enumerate(action.steps):
                for statement in step.context.get_all_statements():
                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": step.id,
                        "step_title": step.title,
                        "step_number": i+1,
                        "action_step_id": build_long_id(action.id, step.id),
                        "source": "step context",
                        **statement.to_dict()
                    })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def response_usage(
        self,
        *action_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON
    ) -> Any:
        """Report all responses used in the assistant steps."""
        results = []
        
        for action in self.assistant.actions.values():
            if len(action_ids) and action.id not in action_ids:
                continue
            
            # Step-level responses
            for i, step in enumerate(action.steps):
                # TODO: Maybe I should iterate over responses? Idk
                results.append({
                    "action_id": action.id,
                    "action_title": action.title,
                    "step_id": step.id,
                    "step_title": step.title,
                    "step_number": i+1,
                    "action_step_id": build_long_id(action.id, step.id),
                    "response_types": [response.response_type.value for response in step.responses],
                    "assistant_response": "\n".join([str(response) for response in step.responses])
                })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)