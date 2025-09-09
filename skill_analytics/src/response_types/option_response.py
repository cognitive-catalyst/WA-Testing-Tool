from src.response_types.response import Response
from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

class OptionResponse(Response):
    
    name = "option response"
    response_type = "option"

    def __init__(self, output_obj, questions_obj):
        super().__init__()

        self.raw_obj = {
            "output": output_obj,
            "questions": questions_obj,
        }

        self.buttons = OptionResponse._parse_output_for_option_response(output_obj)
        self.response_collection_behavior = questions_obj.get("response_collection_behavior", "optionally_ask")

        self.variable_ids = []
        for button_obj in self.buttons:
            self.variable_ids.extend(parse_variables_from_spel_expression(button_obj["label"]))
            self.variable_ids.extend(parse_variables_from_spel_expression(button_obj["value"]))
        self.variable_ids = list(sorted(set(self.variable_ids)))

    def __bool__(self):
        return self.buttons.__bool__()

    def to_json(self):
        return {
            "buttons": self.buttons,
            "response_type": self.response_type,
            "response_collection_behavior": self.response_collection_behavior,
            "variables": self.variable_ids
        }

    def get_labels(self):
        return [button_obj["label"] for button_obj in self.buttons]

    def get_values(self):
        return [button_obj["value"] for button_obj in self.buttons]

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_output_for_option_response(output_obj):
        
        option_responses = []

        for response_obj in output_obj.get("generic", []):
            response_type = response_obj["response_type"]

            if response_type != "option":
                continue
            
            option_responses.extend(OptionResponse._parse_option_response_obj(response_obj))

        return option_responses

    @staticmethod
    def _parse_option_response_obj(options_response_obj):
        
        options_responses = []
        for option_obj in options_response_obj["options"]:
            label = option_obj["label"]
            value = option_obj["value"]["input"]["text"]

            options_responses.append({
                "label": label,
                "value": value
            })
        
        return options_responses

    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []
        for button_obj in self.buttons:
            variable_ids = list(sorted(set(parse_variables_from_spel_expression(button_obj["label"]) + parse_variables_from_spel_expression(button_obj["value"]))))
            for variable_id in variable_ids:
                results.append({
                    "variable": variable_id,
                    "label": button_obj["label"],
                    "value": button_obj["value"],
                    "source": self.name
                })
        return results
    
    def get_all_responses(self):
        results = []
        if self.buttons:
            for label in self.get_labels():
                results.append({
                    "source": self.name,
                    "response_type": self.response_type + " - labels",
                    "response_text": label,
                })
            for value in self.get_values():
                results.append({
                    "source": self.name,
                    "response_type": self.response_type + " - values",
                    "response_text": value,
                })
        return results