from src.statement import Statement

class Context:

    name = "context"

    def __init__(self, context_obj):
        self.raw_obj = context_obj
        
        self.context_statements = Context._parse_context(context_obj)
        self.variable_ids = list(sorted(set([variable for statement in self.context_statements for variable in statement.variable_ids])))
    
    def __repr__(self):
        return "\n".join([context_statement["SpEL expression"] for context_statement in self.context_statements])

    def __iter__(self):
        return self.context_statements.__iter__()

    def to_json(self):
        return {
            "statements": [statement.to_json() for statement in self.context_statements],
            "variables": self.variable_ids,
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_context(context_obj):
        context = []
        for context_variable_obj in context_obj.get("variables", []):
            context.append( Context._parse_context_variable(context_variable_obj) )
        
        return context

    @staticmethod
    def _parse_context_variable(variable_obj):

        LHS = LHS_SpEL_expression = None
        RHS = RHS_SpEL_expression = None

        if "skill_variable" in variable_obj:
            LHS = variable_obj["skill_variable"]
            LHS_SpEL_expression = f"${{{LHS}}}"
        
        RHS, RHS_SpEL_expression = Context._parse_value_obj(variable_obj["value"])

        return Statement(
            LHS=LHS, 
            LHS_SpEL_expression=LHS_SpEL_expression,
            RHS=RHS,
            RHS_SpEL_expression=RHS_SpEL_expression,
            operation="assign" if LHS else None
        )

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

        for statement in self.context_statements:
            statement_results = statement.get_all_variable_usage()
            for statement_result in statement_results:
                results.append({
                    "source": "context",
                    **statement_result
                })
        
        return results
    
    def get_all_entity_usage(self):
        results = []

        for statement in self.context_statements:
            statement_results = statement.get_all_entity_usage()
            for statement_result in statement_results:
                results.append({
                    "source": "context",
                    **statement_result
                })
        
        return results