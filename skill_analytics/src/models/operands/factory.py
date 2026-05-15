from typing import Type

from .base import Operand, OperandType
from .scalar import ScalarOperand
from .time import TimeOperand
from .expression import ExpressionOperand
from .variable import SkillVariableOperand, SystemVariableOperand, VariableOperand
from .intent import IntentOperand
from .entity import EntityOperand
from .collection import CollectionOperand


# Map OperandType enum values to their corresponding operand classes
OPERAND_REGISTRY: dict[OperandType, Type[Operand]] = {
    OperandType.SCALAR: ScalarOperand,
    OperandType.TIME: TimeOperand,
    OperandType.EXPRESSION: ExpressionOperand,
    OperandType.SKILL_VARIABLE: SkillVariableOperand,
    OperandType.SYSTEM_VARIABLE: SystemVariableOperand,
    OperandType.VARIABLE: VariableOperand,
    OperandType.INTENT: IntentOperand,
    OperandType.ENTITY: EntityOperand,
    OperandType.COLLECTION: CollectionOperand,
}


def create_operand_from_dict(data: dict) -> Operand:
    """Create the appropriate operand instance from a dictionary based on its type."""
    for operand_type, operand_class in OPERAND_REGISTRY.items():
        key = operand_type.value
        if key in data:
            return operand_class.from_dict(data)
    
    # If no matching key found, raise an error
    raise ValueError(f"Unknown operand type. Data keys: {list(data.keys())}")
