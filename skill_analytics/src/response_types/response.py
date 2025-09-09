
class Response:

    def __init__(self):
        pass

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_output_for_text_response(output_obj):
        
        text_responses = []

        for generic_obj in output_obj.get("generic", []):
            response_type = generic_obj["response_type"]

            if response_type != "text":
                continue
            
            text_responses.extend(Response._parse_generic_obj(generic_obj))

        return "".join(text_responses)

    @staticmethod
    def _parse_generic_obj(generic_obj):
        
        text_responses = []
        for value_obj in generic_obj["values"]:
            if "text_expression" in value_obj:
                for concat_obj in value_obj["text_expression"]["concat"]:
                    if "scalar" in concat_obj:
                        text = concat_obj["scalar"]
                        if text:
                            text_responses.append(text)
                    
                    elif "variable" in concat_obj:
                        text = f"${{{concat_obj['variable']}}}"
                        if "variable_path" in concat_obj:
                            text = f"{text}.{concat_obj['variable_path']}"
                        text_responses.append(text)
                    
                    elif "skill_variable" in concat_obj:
                        text = f"${{{concat_obj['skill_variable']}}}"
                        if "variable_path" in concat_obj:
                            text = f"{text}.{concat_obj['variable_path']}"
                        text_responses.append(text)
                    
                    elif "system_variable" in concat_obj:
                        text = f"${{{concat_obj['system_variable']}}}"
                        if "variable_path" in concat_obj:
                            text = f"{text}.{concat_obj['variable_path']}"
                        text_responses.append(text)
                    
                    else:
                        raise ValueError(f"Unexpected field: {concat_obj}")
            elif "text" in value_obj:
                text_responses.append(value_obj["text"])
            else:
                raise ValueError(f"Unexpected field: {value_obj}")
        
        return text_responses