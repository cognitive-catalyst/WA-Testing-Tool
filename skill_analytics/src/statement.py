from src.utils.parse_variables_from_spel_expression import parse_variables_from_spel_expression

class Statement:

    name = "statement"

    EXISTS = ["exists", "defined", "is defined"]
    NOT_EXISTS = ["not_exists", "not exists", "not_defined", "not defined", "is not defined"]

    CONTAINS = ["contains"]
    NOT_CONTAINS = ["not_contains", "not contains", "does not contain"]

    MATCHES = ["matches"]
    NOT_MATCHES = ["not_matches", "not matches", "does not match"]

    IN = ["in", "is any of"]
    NOT_IN = ["not_in", "not in", "is none of"]

    operation_to_SpEL_map = {
        "assign": "=",
        "and": "&&",
        "or": "||",
        "eq": "==",
        "equal": "==",
        "is": "==",
        "neq": "!=",
        "not equal": "!=",
        "is not": "!=",
        "gt": ">",
        "greater than": ">",
        "lt": "<", 
        "less than": "<", 
        "gte": ">=",
        "greater than or equal": ">=",
        "lte": "<=",
        "less than or equal": "<="
    }

    def __init__(self, LHS=None, operation=None, RHS=None, LHS_SpEL_expression=None, RHS_SpEL_expression=None, entity_id=None):
        self.LHS = LHS
        self.operation = operation
        self.RHS = RHS
        self.entity_id = entity_id

        self.LHS_SpEL_expression = Statement._infer_SpEL_expression(LHS) if LHS_SpEL_expression is None else LHS_SpEL_expression
        self.RHS_SpEL_expression = Statement._infer_SpEL_expression(RHS) if RHS_SpEL_expression is None else RHS_SpEL_expression

        self.SpEL_expression = Statement._create_equivalent_spel_expression(self.LHS, self.LHS_SpEL_expression, self.operation, self.RHS, self.RHS_SpEL_expression)
        
        self.LHS_variables = list(sorted(set(parse_variables_from_spel_expression(self.LHS_SpEL_expression))))
        self.RHS_variables = list(sorted(set(parse_variables_from_spel_expression(self.RHS_SpEL_expression))))
        self.variable_ids = list(sorted(set(parse_variables_from_spel_expression(self.SpEL_expression))))

    def __repr__(self):
        return self.SpEL_expression

    def to_json(self):
        return {
            "LHS": self.LHS,
            "LHS SpEL expression": self.LHS_SpEL_expression,
            "LHS variables": self.LHS_variables,
            "RHS": self.RHS,
            "RHS SpEL expression": self.RHS_SpEL_expression,
            "RHS variables": self.RHS_variables,
            "operation": self.operation,
            "SpEL expression": self.SpEL_expression,
            "entity_id": self.entity_id,
            "variables": self.variable_ids
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _validate_arguments(LHS, operation, RHS):
        if LHS is None and operation is None and RHS is None:
            raise ValueError("At least one of 'LHS', 'operation', and 'RHS' must not be None.")
        
        if LHS is None and RHS is None:
            boolean_operations = Statement.MATCHES + Statement.NOT_MATCHES + Statement.CONTAINS + Statement.NOT_CONTAINS + list(Statement.operation_to_SpEL_map)
            if operation in boolean_operations:
                raise ValueError(f"For an operation of value '{operation}', both 'LHS' and 'RHS' must not be None.")    

        if operation in (Statement.EXISTS + Statement.NOT_EXISTS) and RHS is not None:
            raise ValueError(f"For an operation of value '{operation}', 'RHS' must be None")


    @staticmethod
    def _infer_SpEL_expression(value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, str):
            if parse_variables_from_spel_expression(value):  # this means it's in the format of a variable
                return value
            return f'"{value}"'
        return str(value)

    @staticmethod
    def _create_equivalent_spel_expression(LHS, LHS_SpEL_expression, operation, RHS, RHS_SpEL_expression):
        
        if operation in Statement.EXISTS:
            return Statement._create_equivalent_spel_expression(LHS, LHS_SpEL_expression, "neq", RHS, RHS_SpEL_expression)    # RHS_SpEL_expression == null 
        if operation in Statement.NOT_EXISTS:
            return Statement._create_equivalent_spel_expression(LHS, LHS_SpEL_expression, "eq", RHS, RHS_SpEL_expression)     # RHS_SpEL_expression == null

        if operation in Statement.MATCHES:
            return f"{LHS_SpEL_expression}.matches({RHS_SpEL_expression})"
        if operation in Statement.NOT_MATCHES:
            return f"!({Statement._create_equivalent_spel_expression(LHS, LHS_SpEL_expression, 'matches', RHS, RHS_SpEL_expression)})"
        
        if operation in Statement.CONTAINS:
            return f"{LHS_SpEL_expression}.contains({RHS_SpEL_expression})"
        if operation in Statement.NOT_CONTAINS:
            return f"!({Statement._create_equivalent_spel_expression(LHS, LHS_SpEL_expression, 'contains', RHS, RHS_SpEL_expression)})"

        if operation in Statement.IN:
            return f'{RHS_SpEL_expression}.contains("{LHS_SpEL_expression}")'
        if operation in Statement.NOT_IN:
            return f"!({Statement._create_equivalent_spel_expression(LHS, LHS_SpEL_expression, 'in', RHS, RHS_SpEL_expression)})"

        if operation in Statement.operation_to_SpEL_map:
            return f"{LHS_SpEL_expression} {Statement.operation_to_SpEL_map[operation]} {RHS_SpEL_expression}"

        # This means it's just a SpEL expression
        if LHS is None and operation is None:
            return RHS_SpEL_expression
        if operation is None and RHS is None:
            return LHS_SpEL_expression

        raise ValueError(f"Unknown operation '{operation}'. Expected one of {list(Statement.operation_to_SpEL_map.keys())}")
    
    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []
        for variable_id in self.variable_ids:
            results.append({
                "variable": variable_id,
                "LHS": self.LHS,
                "RHS": self.RHS,
                "operation": self.operation,
                "SpEL expression": self.SpEL_expression,
                "entity_id": self.entity_id,
            })
        return results

    def get_all_entity_usage(self):
        if self.entity_id:
            return [{
                "entity": self.entity_id,
                "LHS": self.LHS,
                "RHS": self.RHS,
                "operation": self.operation,
                "SpEL expression": self.SpEL_expression
            }]
        return []