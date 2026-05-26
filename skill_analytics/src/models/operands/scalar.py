from dataclasses import dataclass

from .base import Operand, OperandType


@dataclass
class ScalarOperand(Operand):
    _ignore_case: bool = False

    def __post_init__(self):
        self.operand_type = OperandType.SCALAR

    @classmethod
    def from_dict(cls, data: dict) -> 'ScalarOperand':
        """Create a ScalarOperand instance from a dictionary."""
        return cls(
            value=data["scalar"],
            _ignore_case=data.get("options", {}).get("ignore_case", False)
        )

    @property
    def spel_expression(self) -> str:
        """Generate the SpEL expression for this scalar value."""
        spel_expression = str(self.value)
        if isinstance(self.value, str):
            spel_expression = f'"{self.value}"'
        if isinstance(self.value, bool):
            spel_expression = str(self.value).lower()
        
        # if self._ignore_case:
        #     spel_expression = f"(?i){spel_expression}"
        return spel_expression
