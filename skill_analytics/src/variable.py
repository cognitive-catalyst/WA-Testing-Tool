
class Variable:

    def __init__(self, variable_obj):
        self.raw_obj = variable_obj

        self.ID = variable_obj.get("variable")
        self.title = variable_obj.get("title")
        self.description = variable_obj.get("description")
        self.data_type = variable_obj.get("data_type", "any")
        self.initial_value = Variable._parse_initial_value( variable_obj.get("initial_value") )
        
        self.is_protected = variable_obj.get("privacy", {}).get("enabled", False)

    def __repr__(self):
        return self.ID
    
    def to_json(self):
        return {
            "ID": self.ID,
            "title": self.title,
            "description": self.description,
            "data_type": self.data_type,
            "initial_value": self.initial_value,
            "is_protected": self.is_protected
        }

    def __bool__(self):
        return self.ID is not None

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_initial_value(value_obj):
        if value_obj is None:
            return None
        
        if "scalar" in value_obj:
            value = value_obj["scalar"]
            return value

        if "expression" in value_obj:
            value = value_obj["expression"]
            return value

        raise Exception("Unknown", value_obj)
    
    # ================================================================================
    # Searching
    # ================================================================================

    def summary(self):
        return {
            "variable_id": self.ID,
            "variable_title": self.title,
            "description": self.description,
            "data_type": self.data_type,
            "initial_value": self.initial_value,
            "is_protected": self.is_protected
        }