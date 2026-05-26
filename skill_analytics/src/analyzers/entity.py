from typing import Any

from src.models.assistant import Assistant
from src.models.operands import EntityOperand
from src.output_handlers import OutputFormat, create_output_handler
from src.utils.parse_wxa_ids import build_long_id


class EntityAnalyzer:
    """Analyzer for extracting and analyzing entities metadata from an Assistant."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def entity_metadata(
        self,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        
        results = []
        for entity in self.assistant.entities.values():
            for value in entity.values:
                results.append({
                    "entity_id": entity.id,
                    "fuzzy_match": entity.fuzzy_match,
                    **value.to_dict()
                })
    
        handler = create_output_handler(return_as)
        return handler.handle(results)

    def entity_usage(
        self,
        *entity_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        """Get usage of entities across all actions and steps."""
        results = []
        
        for action in self.assistant.actions.values():
            # Check action condition
            for statement in action.condition.get_all_statements():
                for operand in statement.get_operands():
                    if isinstance(operand, EntityOperand):
                        if len(entity_ids) and operand.entity_id not in entity_ids:
                            continue
                        results.append({
                            "action_id": action.id,
                            "action_title": action.title,
                            "step_id": None,
                            "step_title": None,
                            "step_number": 0,
                            "action_step_id": None,
                            "entity_id": operand.entity_id,
                            "entity_value": operand.value,
                            "source": "action condition",
                            **statement.to_dict()
                        })
            
            # Check each step
            for i, step in enumerate(action.steps):
                # Check step condition
                for statement in step.condition.get_all_statements():
                    for operand in statement.get_operands():
                        if isinstance(operand, EntityOperand):
                            if len(entity_ids) and operand.entity_id not in entity_ids:
                                continue
                            results.append({
                                "action_id": action.id,
                                "action_title": action.title,
                                "step_id": step.id,
                                "step_title": step.title,
                                "step_number": i+1,
                                "action_step_id": build_long_id(action.id, step.id),
                                "entity_id": operand.entity_id,
                                "entity_value": operand.value,
                                "source": "condition",
                                **statement.to_dict()
                            })
                
                # Check step context
                for statement in step.context.get_all_statements():
                    for operand in statement.get_operands():
                        if isinstance(operand, EntityOperand):
                            if len(entity_ids) and operand.entity_id not in entity_ids:
                                continue
                            results.append({
                                "action_id": action.id,
                                "action_title": action.title,
                                "step_id": step.id,
                                "step_title": step.title,
                                "step_number": i+1,
                                "action_step_id": build_long_id(action.id, step.id),
                                "entity_id": operand.entity_id,
                                "entity_value": operand.value,
                                "source": "context",
                                **statement.to_dict()
                            })
            
                if step.entity:
                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": step.id,
                        "step_title": step.title,
                        "step_number": i+1,
                        "action_step_id": build_long_id(action.id, step.id),
                        "entity_id": step.entity.id,
                        "source": "response",
                    })

            # TODO: When I finish implementing buttons, I'll need to add that here as well

        handler = create_output_handler(return_as)
        return handler.handle(results)