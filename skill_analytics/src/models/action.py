from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .action_settings import ActionSettings
from .condition import Condition
from .entity import Entity
from .intent import Intent
from .step import Step
from .variables import ResultVariable, StepVariable


@dataclass
class Action:
    id: str
    title: str
    description: Optional[str]
    
    intent: Intent
    condition: Condition
    settings: Any

    steps: List[Step]
    
    step_variables: Dict[str, StepVariable]
    result_variables: Dict[str, ResultVariable]

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_dict(
        cls,
        action_dict: dict,
        intents: Dict[str, Intent],
        entities: Dict[str, Entity]
    ) -> 'Action':
        """Create an Action instance from a dictionary."""
        id = action_dict["action"]
        
        step_variables: Dict[str, StepVariable] = {}
        result_variables: Dict[str, ResultVariable] = {}
        for variable_dict in action_dict.get("variables", []):
            variable_id = variable_dict["variable"]
            if "_result" in variable_id:
                result_variable = ResultVariable.from_dict(variable_dict, id)
                result_variables[result_variable.id] = result_variable
            else:
                step_variable = StepVariable.from_dict(variable_dict, id)
                step_variables[step_variable.id] = step_variable
        
        condition_dict = action_dict.get("condition", {})
        condition = Condition.from_dict(condition_dict)

        intent_id = Action._get_intent_id(condition_dict)
        intent = Intent()
        if intent_id in intents:
            intent = intents[intent_id]

        steps: List[Step] = []
        for step_dict in action_dict["steps"]:
            step = Step.from_dict(step_dict, entities)
            steps.append(step)

        return cls(
            id=id,
            title=action_dict["title"],
            description=action_dict.get("description"),
            
            intent=intent,
            condition=condition,
            settings=ActionSettings.from_dict(action_dict),

            steps=steps,
            step_variables=step_variables,
            result_variables=result_variables,
        )

    def get_subaction_ids(self) -> List[str]:
        """Get all subaction IDs referenced in this action's steps."""
        return [step.subaction_id for step in self.steps if step.subaction_id]
    
    def get_extensions(self) -> List[Any]:
        """Get all extensions used in this action."""
        # TODO
        return []

    def get_skill_variable_ids(self) -> List[str]:
        """Get all skill variable IDs referenced in this action."""
        skill_variable_ids =  []
        return skill_variable_ids

    @staticmethod
    def _get_intent_id(obj: Any) -> Optional[str]:
        if isinstance(obj, dict):
            if "intent" in obj:
                return obj["intent"]
            for value in obj.values():
                intent_id = Action._get_intent_id(value)
                if intent_id:
                    return intent_id
        
        if isinstance(obj, list):
            for value in obj:
                intent_id = Action._get_intent_id(value)
                if intent_id:
                    return intent_id
        
        return None