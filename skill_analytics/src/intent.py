import re

class Intent:

    def __init__(self, intent_obj, index):
        self.raw_obj = intent_obj
        self.index = index

        self.ID = intent_obj.get("intent")
        self.action_id = Intent._parse_intent_id(self.ID)
        self.examples = Intent._parse_examples(intent_obj.get("examples", []))
    
    def __repr__(self):
        return self.ID

    def to_json(self):
        return {
            "ID": self.ID,
            "action_id": self.action_id,
            "examples": self.examples
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_examples(examples):
        return [text_obj.get("text") for text_obj in examples if text_obj.get("text")]
    
    @staticmethod
    def _parse_intent_id(full_intent_id):
        if full_intent_id is None:
            return None
        if full_intent_id == "fallback_connect_to_agent":
            return "fallback"
        
        pattern = r"(action\_\d*)_(intent\_.*)"
        match = re.search(pattern, full_intent_id)
        if match:
            return match.group(1)

        print(f"Warning: Did not parse intent id {full_intent_id}")