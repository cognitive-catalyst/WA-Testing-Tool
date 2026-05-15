from dataclasses import dataclass
from typing import Dict, Optional

from src.utils.parse_wxa_ids import build_long_id

from .action import Action
from .intent import Intent
from .data_types import DataTypeRegistry
from .entity import Entity
from .system_settings import SystemSettings
from .variables import (
    ResultVariable,
    SkillVariable,
    StepVariable,
    SystemVariable,
    Variable,
    SYSTEM_VARIABLE_IDS,
)


@dataclass
class Assistant:
    name: str
    description: str
    skill_id: str
    assistant_id: str
    workspace_id: Optional[str]

    settings: SystemSettings
    
    intents: Dict[str, Intent]
    entities: Dict[str, Entity]
    actions: Dict[str, Action]

    data_type_registry: DataTypeRegistry
    skill_variables: Dict[str, SkillVariable]

    def __post_init__(self):
        # cached variables
        self._system_variables = None
        self._step_variables = None
        self._result_variables = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Assistant':
        """Create an Assistant instance from a dictionary."""
        workspace = data["workspace"]

        intents: Dict[str, Intent] = {}
        for intent_dict in workspace["intents"]:
            intent = Intent.from_dict(intent_dict)
            assert intent.id is not None
            intents[intent.id] = intent

        entities: Dict[str, Entity] = {}
        for entity_dict in workspace["entities"]:
            entity = Entity.from_dict(entity_dict)
            entities[entity.id] = entity

        actions: Dict[str, Action] = {}
        for action_dict in workspace["actions"]:
            action = Action.from_dict(action_dict, intents, entities)
            actions[action.id] = action

        data_type_registry = DataTypeRegistry()
        data_type_registry.register_many(workspace.get("data_types", []))

        skill_variables: Dict[str, SkillVariable] = {}
        for variable_dict in workspace["variables"]:
            skill_variable = SkillVariable.from_dict(variable_dict, data_type_registry)
            skill_variables[skill_variable.id] = skill_variable

        return cls(
            name=data["name"],
            description=data["description"],
            skill_id=data["skill_id"],
            assistant_id=data["assistant_id"],
            workspace_id=data.get("workspace_id"),
            
            settings=SystemSettings.from_dict(workspace["system_settings"]),

            entities=entities,
            intents=intents,
            actions=actions,

            data_type_registry=data_type_registry,
            skill_variables=skill_variables,
        )

    def get_action(self, id_or_title: str) -> Optional[Action]:
        """Retrieve an action by its ID or title."""
        for action in self.actions.values():
            if id_or_title == action.id or id_or_title == action.title:
                return action

    def get_variable(self, variable_id: str, action_id: Optional[str] = None) -> Optional[Variable]:
        """Retrieve a variable by ID, searching across skill, step, result, and system variables."""
        long_id = variable_id
        if action_id is not None:
            long_id = build_long_id(action_id, variable_id)
        
        if variable_id in self.skill_variables:
            return self.skill_variables[variable_id]
        
        if long_id in self.step_variables:
            return self.step_variables[long_id]
        
        if long_id in self.result_variables:
            return self.result_variables[long_id]
        
        if variable_id in self.system_variables:
            return self.system_variables[variable_id]

    @property
    def system_variables(self) -> Dict[str, SystemVariable]:
        """Get all system variables, cached after first access."""
        if self._system_variables:
            return self._system_variables
        
        system_variables: Dict[str, SystemVariable] = {}
        for system_variable_id in SYSTEM_VARIABLE_IDS:
            system_variable = SystemVariable.from_dict({"variable": system_variable_id})
            system_variables[system_variable.uid] = system_variable

        self._system_variables = system_variables
        return self._system_variables

    @property
    def step_variables(self) -> Dict[str, StepVariable]:
        """Get all step variables from all actions, cached after first access."""
        if self._step_variables:
            return self._step_variables
        
        step_variables: Dict[str, StepVariable] = {}
        for action in self.actions.values():
            for step_variable in action.step_variables.values():
                step_variables[step_variable.uid] = step_variable
        
        self._step_variables = step_variables
        return self._step_variables

    @property
    def result_variables(self) -> Dict[str, ResultVariable]:
        """Get all result variables from all actions, cached after first access."""
        if self._result_variables:
            return self._result_variables
        
        result_variables: Dict[str, ResultVariable] = {}
        for action in self.actions.values():
            for result_variable in action.result_variables.values():
                result_variables[result_variable.uid] = result_variable
        
        self._result_variables = result_variables
        return self._result_variables