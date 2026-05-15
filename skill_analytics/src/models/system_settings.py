from enum import Enum
from dataclasses import dataclass


class NoMatchThresholdType(Enum):
    RARELY = "rarely"
    SOMETIMES = "sometimes"
    MORE_OFTEN = "more_often"

@dataclass
class SystemSettings:
    disambiguations_enabled: bool
    disambiguation_message: str
    no_match_threshold: NoMatchThresholdType
    digressions_enabled: bool
    digression_confirmation_enabled: bool
    spelling_auto_correct_enabled: bool


    @classmethod
    def from_dict(cls, data: dict) -> 'SystemSettings':
        """Create an SystemSettings instance from a dictionary."""
        return cls(
            disambiguations_enabled=data["disambiguation"]["enabled"],
            disambiguation_message=data["disambiguation"]["prompt"],
            no_match_threshold=NoMatchThresholdType(data["launch_mode"].get("no_action_matches", "rarely")),
            digressions_enabled=data["topic_switch"]["enabled"],
            digression_confirmation_enabled=data["topic_switch"]["messages"]["enable_confirmation"],
            spelling_auto_correct_enabled=data["spelling_auto_correct"],
        )

    def to_dict(self) -> dict:
        """Convert the action settings to a dictionary representation."""
        return {
            "disambiguations_enabled": self.disambiguations_enabled,
            "disambiguation_message": self.disambiguation_message,
            "no_match_threshold": self.no_match_threshold.value,
            "digressions_enabled": self.digressions_enabled,
            "digression_confirmation_enabled": self.digression_confirmation_enabled,
            "spelling_auto_correct_enabled": self.spelling_auto_correct_enabled,
        }



