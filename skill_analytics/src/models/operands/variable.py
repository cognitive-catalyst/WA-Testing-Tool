from dataclasses import dataclass

from .base import Operand, OperandType


@dataclass
class SkillVariableOperand(Operand):
    skill_variable_id: str

    def __post_init__(self):
        self.operand_type = OperandType.SKILL_VARIABLE

    @classmethod
    def from_dict(cls, data: dict) -> 'SkillVariableOperand':
        """Create a SkillVariableOperand instance from a dictionary."""
        skill_variable_id = data['skill_variable']
        value = f"${{{skill_variable_id}}}"
        return cls(value=value, skill_variable_id=skill_variable_id)

    @property
    def spel_expression(self) -> str:
        """Get the SpEL expression value."""
        return self.value

@dataclass
class SystemVariableOperand(Operand):

    def __post_init__(self):
        self.operand_type = OperandType.SYSTEM_VARIABLE

    @classmethod
    def from_dict(cls, data: dict) -> 'SystemVariableOperand':
        """Create a SystemVariableOperand instance from a dictionary."""
        value = f"${{{data['system_variable']}}}"
        return cls(value=value)

    @property
    def spel_expression(self) -> str:
        """Get the SpEL expression value."""
        return self.value


@dataclass
class VariableOperand(Operand):

    def __post_init__(self):
        self.operand_type = OperandType.VARIABLE

    @classmethod
    def from_dict(cls, data: dict) -> 'VariableOperand':
        value = f"${{{data['variable']}}}"
        if "variable_path" in data:
            value = f"{value}.{data['variable_path']}"
        return cls(value=value)

    @property
    def spel_expression(self) -> str:
        return self.value
