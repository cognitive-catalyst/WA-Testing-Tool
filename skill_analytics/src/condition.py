from src.statement import Statement

class Condition:

    name = "condition"

    def __init__(self, condition_obj):
        self.raw_obj = condition_obj

        self.condition_statements, self.SpEL_expression = Condition._parse_condition(condition_obj)
        self.SpEL_expression = "null" if self.SpEL_expression is None else str(self.SpEL_expression)

        self.variable_ids = list(sorted(set([variable for statement in self.condition_statements for variable in statement.variable_ids])))
    
    def __repr__(self):
        return self.SpEL_expression

    def __iter__(self):
        return self.condition_statements.__iter__()

    def to_json(self):
        return {
            "statements": [statement.to_json() for statement in self.condition_statements],
            "SpEL expression": self.SpEL_expression,
            "variables": self.variable_ids,
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_condition(condition_obj):
        if condition_obj == {}:
            return [], None

        if ("and" not in condition_obj) and ("or" not in condition_obj):
            statement = Condition._parse_condition_statement(condition_obj)
            if statement is None:
                return [], None
            return [statement], statement.SpEL_expression

        condition_statements = []
        SpEL_expression = ""
        for boolean_operator, sub_condition_list in condition_obj.items():
            sub_SpEL_expressions = []
            for sub_condition_obj in sub_condition_list:
                sub_condition_statements, sub_SpEL_expression = Condition._parse_condition(sub_condition_obj)
                condition_statements.extend(sub_condition_statements)
                if sub_SpEL_expression is not None:
                    sub_SpEL_expressions.append(sub_SpEL_expression)
            
            SpEL_expression = f") {Statement.operation_to_SpEL_map[boolean_operator]} (".join(sub_SpEL_expressions)
            if len(sub_condition_list) > 1:
                SpEL_expression = f"({SpEL_expression})"

        return condition_statements, SpEL_expression

    @staticmethod
    def _parse_condition_statement(condition_statement_obj):
        statement = None

        boolean_operations = list(Statement.operation_to_SpEL_map.keys()) + ["matches", "not_matches", "contains", "not_contains", "in", "not_in"]

        for field in condition_statement_obj:

            if field == "not":
                LHS, LHS_SpEL_expression, _ = Condition._parse_condition_operand(condition_statement_obj["not"]["exists"])
                statement = Statement(
                    LHS=LHS, 
                    LHS_SpEL_expression=LHS_SpEL_expression,
                    operation="not exists"
                )
            
            elif field == "exists":
                LHS, LHS_SpEL_expression, _ = Condition._parse_condition_operand(condition_statement_obj["exists"])
                statement = Statement(
                    LHS=LHS, 
                    LHS_SpEL_expression=LHS_SpEL_expression,
                    operation="exists"
                )
            
            elif field in boolean_operations:
                # I don't think an entity would ever be on the LHS of a condition
                LHS, LHS_SpEL_expression, _ = Condition._parse_condition_operand(condition_statement_obj[field][0])
                RHS, RHS_SpEL_expression, RHS_entity_id = Condition._parse_condition_operand(condition_statement_obj[field][1])
                statement = Statement(
                    LHS=LHS, 
                    LHS_SpEL_expression=LHS_SpEL_expression,
                    operation=field,
                    RHS=RHS,
                    RHS_SpEL_expression=RHS_SpEL_expression,
                    entity_id=RHS_entity_id
                )

            elif field == "expression":
                statement = Statement(
                    RHS=condition_statement_obj["expression"],
                    RHS_SpEL_expression=condition_statement_obj["expression"]
                )

            elif field in ["entity", "intent"]:
                pass

            else:
                raise ValueError("Unknown condition field:", field)

        return statement

    @staticmethod
    def _parse_condition_operand(condition_operand_obj):

        if "add" in condition_operand_obj:
            return Condition._parse_add_or_subtract_date_obj(condition_operand_obj["add"], "add")

        if "subtract" in condition_operand_obj:
            return Condition._parse_add_or_subtract_date_obj(condition_operand_obj["subtract"], "subtract")

        if "time" in condition_operand_obj:
            return Condition._parse_condition_operand(condition_operand_obj["time"])

        if "value" in condition_operand_obj:
            value = condition_operand_obj["value"]
            SpEL_expression = f'"{value}"'
            entity_id = condition_operand_obj.get("from_entity")
            return value, SpEL_expression, entity_id
        
        if "scalar" in condition_operand_obj:
            value = condition_operand_obj["scalar"]
            SpEL_expression = str(value)
            if isinstance(value, bool):
                SpEL_expression = str(value).lower()
            if isinstance(value, str):
                SpEL_expression = f'"{value}"'

            ignore_case = condition_operand_obj.get("options", {}).get("ignore_case", False)
            if ignore_case:
                SpEL_expression = f"(?i){SpEL_expression}"
            return value, SpEL_expression, None
        
        if "expression" in condition_operand_obj:
            value = condition_operand_obj["expression"]
            SpEL_expression = value
            return value, SpEL_expression, None
        
        if "collection" in condition_operand_obj:
            value = [obj["value"] for obj in condition_operand_obj["collection"]]
            SpEL_expression = str(value)
            return value, SpEL_expression, None

        variable_types = ["variable", "skill_variable", "system_variable"]
        for field in variable_types:
            if field in condition_operand_obj:
                value = condition_operand_obj[field]
                SpEL_expression = f"${{{value}}}"
                if "variable_path" in condition_operand_obj:
                    value = f"{SpEL_expression}.{condition_operand_obj['variable_path']}"
                    SpEL_expression = value

                return value, SpEL_expression, None
        
        raise ValueError("Unknown condition operand:", condition_operand_obj)
    
    @staticmethod
    def _parse_add_or_subtract_date_obj(add_or_subtract_date_obj, add_or_subtract_field):
        if add_or_subtract_field != "add" and add_or_subtract_field != "subtract":
            raise ValueError(f"The argument `add_or_subtract_date_obj` must be one of 'add' or 'subtract', instead got '{add_or_subtract_field}'")

        plus_or_minus = "plus" if add_or_subtract_field == "addition" else "minus"

        LHS = add_or_subtract_date_obj[0]["system_variable"]        # This should always be ${current_date} or ${current_time} I believe
        LHS_SpEL_expression = f"${{{LHS}}}"

        duration_obj = add_or_subtract_date_obj[1]["duration"]
        RHS_SpEL_expression = ""

        if "seconds" in duration_obj:
            RHS_SpEL_expression = f".{plus_or_minus}Seconds({duration_obj['seconds']})"
        elif "minutes" in duration_obj:
            RHS_SpEL_expression = f".{plus_or_minus}Minutes({duration_obj['minutes']})"
        elif "hours" in duration_obj:
            RHS_SpEL_expression = f".{plus_or_minus}Hours({duration_obj['hours']})"
        elif "days" in duration_obj:
            RHS_SpEL_expression = f".{plus_or_minus}Days({duration_obj['days']})"
        elif "months" in duration_obj:
            RHS_SpEL_expression = f".{plus_or_minus}Months({duration_obj['months']})"
        elif "years" in duration_obj:
            RHS_SpEL_expression = f".{plus_or_minus}Years({duration_obj['years']})"
        else:
            raise ValueError("Unknown duration object:", duration_obj)

        return LHS, f"{LHS_SpEL_expression}{RHS_SpEL_expression}", None
        

    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []

        for statement in self.condition_statements:
            statement_results = statement.get_all_variable_usage()
            for statement_result in statement_results:
                results.append({
                    "source": "condition",
                    **statement_result
                })
        
        return results
    
    def get_all_entity_usage(self):
        results = []

        for statement in self.condition_statements:
            statement_results = statement.get_all_entity_usage()
            for statement_result in statement_results:
                results.append({
                    "source": "condition",
                    **statement_result
                })
        
        return results