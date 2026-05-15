from dataclasses import dataclass


@dataclass
class ActionSettings:
    ask_clarifying_question: bool
    change_coversation_topic: bool
    never_return: bool

    @classmethod
    def from_dict(cls, data: dict) -> 'ActionSettings':
        """Create an ActionSettings instance from a dictionary."""
        disambiguation_opt_out = data.get("disambiguation_opt_out", True)
        allowed_from = data.get("topic_switch", {}).get("allowed_from", True)
        allowed_into = data.get("topic_switch", {}).get("allowed_into", True)
        never_return = data.get("topic_switch", {}).get("never_return", False)
        
        if allowed_from != allowed_into:
            raise ValueError(f"The values `allowed_from` and `allowed_into` are different, and they shouldn't be.")

        return cls(
            ask_clarifying_question=(not disambiguation_opt_out),
            change_coversation_topic=allowed_into,
            never_return=never_return
        )

    def to_dict(self) -> dict:
        """Convert the action settings to a dictionary representation."""
        return {
            "ask_clarifying_question": self.ask_clarifying_question,
            "change_coversation_topic": self.change_coversation_topic,
            "never_return": self.never_return,
        }
