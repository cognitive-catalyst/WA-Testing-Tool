from typing import Any

from src.models.assistant import Assistant
from src.output_handlers import OutputFormat, create_output_handler


class AssistantAnalyzer:
    """Analyzer for extracting and analyzing assistant metadata."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def assistant_metadata(
        self,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        """Extract comprehensive metadata about the assistant including IDs, settings, and aggregated stats."""
        
        # Count various elements
        num_actions = len(self.assistant.actions)
        num_intents = len(self.assistant.intents)
        num_entities = len(self.assistant.entities)
        num_skill_variables = len(self.assistant.skill_variables)
        num_step_variables = len(self.assistant.step_variables)
        num_result_variables = len(self.assistant.result_variables)
        num_system_variables = len(self.assistant.system_variables)
        num_custom_data_types = len(self.assistant.data_type_registry.get_all_custom_types())
        
        # Count total steps across all actions
        total_steps = sum(len(action.steps) for action in self.assistant.actions.values())
        
        # Build the metadata dictionary
        result = {
            # ID Information
            "name": self.assistant.name,
            "description": self.assistant.description,
            "skill_id": self.assistant.skill_id,
            "assistant_id": self.assistant.assistant_id,
            "workspace_id": self.assistant.workspace_id,
            
            # System Settings
            **self.assistant.settings.to_dict(),
            
            # Aggregated Statistics
            "num_actions": num_actions,
            "num_intents": num_intents,
            "num_entities": num_entities,
            "num_skill_variables": num_skill_variables,
            "num_step_variables": num_step_variables,
            "num_result_variables": num_result_variables,
            "num_system_variables": num_system_variables,
            "num_custom_data_types": num_custom_data_types,
            "total_steps": total_steps,
        }
        
        handler = create_output_handler(return_as)
        return handler.handle([result])
