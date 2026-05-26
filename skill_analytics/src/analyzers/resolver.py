from typing import Any

from src.models.assistant import Assistant
from src.models.resolvers import CalloutResolver, InvokeActionAndEndResolver, InvokeActionResolver
from src.output_handlers import OutputFormat, create_output_handler
from src.utils.parse_wxa_ids import build_long_id


class ResolverAnalyzer:
    """Analyzer for extracting and analyzing resolver usage from an Assistant."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def subaction_usage(
        self,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        """Find all subaction invocations (invoke_action_resolver and invoke_action_and_end_resolver)."""
        results = []
        
        for action in self.assistant.actions.values():
            for i, step in enumerate(action.steps):
                resolver = step.resolver
                
                # Check if resolver is an invoke action type
                if isinstance(resolver, (InvokeActionResolver, InvokeActionAndEndResolver)):
                    # Get subaction details
                    subaction = self.assistant.actions.get(resolver.subaction_id)
                    subaction_title = subaction.title if subaction else None
                    
                    # Determine if action ends
                    ends_action = isinstance(resolver, InvokeActionAndEndResolver)
                    
                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": step.id,
                        "step_title": step.title,
                        "step_number": i + 1,
                        "action_step_id": build_long_id(action.id, step.id),
                        "subaction_id": resolver.subaction_id,
                        "subaction_title": subaction_title,
                        "ends_action": ends_action,
                        "policy": resolver.policy,
                        "result_variable_id": resolver.result_variable_id,
                        "ignore_end_action_steps": resolver.ignore_end_action_steps,
                    })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def extension_usage(
        self,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        """Find all extension usages (callout_resolver)."""
        results = []
        
        for action in self.assistant.actions.values():
            for i, step in enumerate(action.steps):
                resolver = step.resolver

                # Check if resolver is a callout type
                if isinstance(resolver, CalloutResolver):
                    variable = self.assistant.get_variable(resolver.result_variable_id, action_id=action.id)
                    if variable is None:
                        print(f"Warning: Variable {resolver.result_variable_id} from action {action.title} and step number {i+1} is missing from assistant variables.")

                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": step.id,
                        "step_title": step.title,
                        "step_number": i+1,
                        "action_step_id": build_long_id(action.id, step.id),
                        **resolver.to_dict(),
                        "is_protected": variable.is_protected if variable else False
                    })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)
