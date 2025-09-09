from src.response_types.response import Response
from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

class ValidationResponse(Response):
    
    name = "validation response"
    response_type = "validation"

    def __init__(self, handlers_obj):
        super().__init__()

        self.raw_obj = handlers_obj

        self.validation_responses = ValidationResponse._parse_handlers_obj(handlers_obj)
        self.variable_ids = []
        for validation_response_obj in self.validation_responses:
            self.variable_ids.extend(parse_variables_from_spel_expression(validation_response_obj["message"]))
        self.variable_ids = list(sorted(set(self.variable_ids)))

    def __bool__(self):
        return self.validation_responses.__bool__()

    def to_json(self):
        return {
            "validation_response": self.validation_responses,
            "response_type": self.response_type,
            "variables": self.variable_ids
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_handlers_obj(handlers_obj):
        validation_responses = []
        for handler_obj in handlers_obj:
            validation_response = ValidationResponse._parse_output_for_text_response(handler_obj.get("output", {}))
            validation_responses.append({
                "message": validation_response,
                "handler_type": handler_obj.get("handler"),
                "resolver_type": handler_obj.get("resolver", {}).get("type")
            })
        
        return validation_responses
    
    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []
        for validation_response_obj in self.validation_responses:
            variable_ids = list(sorted(set(parse_variables_from_spel_expression(validation_response_obj["message"]))))
            for variable_id in variable_ids:
                results.append({
                    "variable": variable_id,
                    "text": validation_response_obj["message"],
                    "source": self.name
                })
        return results

    def get_all_responses(self):
        results = []
        for validation_response_obj in self.validation_responses:
            results.append({
                "source": self.name,
                "response_type": self.response_type,
                "response_text": validation_response_obj["message"],
                "handler_type": validation_response_obj["handler_type"],
                "resolver_type": validation_response_obj["resolver_type"],
            })
        return results