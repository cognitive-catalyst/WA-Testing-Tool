from src.response_types.response import Response
from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

class TextResponse(Response):

    name = "text response"
    response_type = "text"

    def __init__(self, output_obj):
        super().__init__()

        self.raw_obj = output_obj

        self.message = TextResponse._parse_output_for_text_response(output_obj)
        self.variable_ids = list(sorted(set(parse_variables_from_spel_expression(self.message))))

    def __bool__(self):
        return self.message.__bool__()
    
    def to_json(self):
        return {
            "message": self.message,
            "response_type": self.response_type,
            "variables": self.variable_ids
        }
    
    # ================================================================================
    # Parsing
    # ================================================================================
    
    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []
        for variable_id in self.variable_ids:
            results.append({
                "variable": variable_id,
                "text": self.message,
                "source": self.name
            })
        return results
    
    def get_all_responses(self):
        results = []
        if self.message:
            results.append({
                "source": self.name,
                "response_type": self.response_type,
                "response_text": self.message,
            })
        return results