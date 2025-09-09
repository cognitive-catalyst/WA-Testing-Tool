from src.statement import Statement

class SubAction:

    name = "subaction"

    def __init__(self, resolver_obj):
        self.raw_obj = resolver_obj

        invoke_action_obj = resolver_obj.get("invoke_action", {})
        self.subaction_exists = bool(invoke_action_obj)

        self.ID = invoke_action_obj.get("action")
        self.result_variable =  invoke_action_obj.get("result_variable")

        self.parameter_statements = SubAction._parse_parameter_obj( invoke_action_obj.get("parameters", []) )
        self.variable_ids = list(sorted(set([variable for statement in self.parameter_statements for variable in statement.variable_ids])))
        if self.result_variable:
            self.variable_ids.append(self.result_variable)

    def __repr__(self):
        if self.subaction_exists:
            return self.ID
        return "No Subaction"
    
    def __bool__(self):
        return self.subaction_exists

    def to_json(self):
        return {
            "ID": self.ID,
            "result variable": self.result_variable,
            "statements": self.parameter_statements,
            "variables": self.variable_ids
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_parameter_obj(parameter_obj_list):
        if parameter_obj_list is None:
            parameter_obj_list = []
        
        parameter_statements = []
        for parameter_obj in parameter_obj_list:
            LHS = parameter_obj["parameter"]
            LHS_SpEL_expression = f"${{{LHS}}}"
            RHS, RHS_SpEL_expression = SubAction._parse_value_obj(parameter_obj["value"])
            parameter_statements.append(Statement(
                LHS=LHS, 
                LHS_SpEL_expression=LHS_SpEL_expression,
                RHS=RHS,
                RHS_SpEL_expression=RHS_SpEL_expression,
                operation="assign"
            ))
        
        return parameter_statements
    
    @staticmethod
    def _parse_value_obj(value_obj):
        
        if "time" in value_obj:
            value = value_obj["time"]
            return value, f'"{value}"'
        
        if "scalar" in value_obj:
            value = value_obj["scalar"]
            if isinstance(value, str):
                return value, f'"{value}"'
            if isinstance(value, bool):
                return value, str(value).lower()
            return value, str(value)

        if "expression" in value_obj:
            value = value_obj["expression"]
            return value, value
        
        if "skill_variable" in value_obj:
            value = f"${{{value_obj['skill_variable']}}}"
            return value, value
        
        if "variable" in value_obj:
            value = f"${{{value_obj['variable']}}}"
            if "variable_path" in value_obj:
                value = f"{value}.{value_obj['variable_path']}"
            return value, value

        raise Exception("Unknown", value_obj)
    
    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []

        for statement in self.parameter_statements:
            statement_results = statement.get_all_variable_usage()
            for statement_result in statement_results:
                results.append({
                    "source": "subaction passed values",
                    **statement_result
                })
        
        return results