from typing import Any

from src.models.assistant import Assistant
from src.models.resolvers import CalloutResolver
from src.models.statements.operation import OperationType
from src.models.variables import VariableType
from src.output_handlers import OutputFormat, create_output_handler
from src.utils.parse_wxa_ids import build_long_id


class VariableAnalyzer:
    """Analyzer for extracting and analyzing variable metadata from an Assistant."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def get_variable_metadata(
        self,
        include_skill_variables: bool = True,
        include_step_variables: bool = True,
        include_result_variables: bool = True,
        include_system_variables: bool = True,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        """Get a comprehensive summary of all variables in the assistant."""
        variables_data = []
        
        # Collect skill variables
        if include_skill_variables:
            for var in self.assistant.skill_variables.values():
                variables_data.append(var.to_dict())

        # Collect step variables
        if include_step_variables:
            for var in self.assistant.step_variables.values():
                variables_data.append(var.to_dict())
        
        # Collect result variables
        if include_result_variables:
            for var in self.assistant.result_variables.values():
                variables_data.append(var.to_dict())

        # Collect system variables
        if include_system_variables:
            for var in self.assistant.system_variables.values():
                variables_data.append(var.to_dict())

        handler = create_output_handler(return_as)
        return handler.handle(variables_data)
    
    def get_variables_by_type(
        self,
        variable_type: VariableType,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        """Get all variables of a specific type."""
        if variable_type == VariableType.SKILL:
            variables = list(self.assistant.skill_variables.values())
        elif variable_type == VariableType.STEP:
            variables = list(self.assistant.step_variables.values())
        elif variable_type == VariableType.RESULT:
            variables = list(self.assistant.result_variables.values())
        elif variable_type == VariableType.SYSTEM:
            variables = list(self.assistant.system_variables.values())
        else:
            raise ValueError(f"Unknown variable type: {variable_type}")
        
        results = [var.to_dict() for var in variables]
        handler = create_output_handler(return_as)
        return handler.handle(results)
    def get_variable_usage(
        self,
        *variable_ids: str,
        return_as: OutputFormat | str = OutputFormat.PYTHON,
    ) -> Any:
        results = []
        
        for action in self.assistant.actions.values():

            for statement in action.condition.get_all_statements():
                for variable_id in statement.get_all_variable_ids():
                    variable = self.assistant.get_variable(variable_id, action_id=action.id)
                    if variable is None:
                        print(f"Warning: Variable {variable_id} in action condition of action {action.title} - {action.id}, but is missing from assistant variables.")
                        results.append({
                            "action_id": action.id,
                            "action_title": action.title,
                            "step_id": None,
                            "step_title": None,
                            "step_number": 0,
                            "action_step_id": None,
                            "variable_id": variable_id,
                            "source": "action condition",
                            **statement.to_dict()
                        })
                        continue
                    if len(variable_ids) and variable.id not in variable_ids:
                        continue
                    results.append({
                        "action_id": action.id,
                        "action_title": action.title,
                        "step_id": None,
                        "step_title": None,
                        "step_number": 0,
                        "action_step_id": None,
                        "variable_id": variable.id,
                        "variable_uid": variable.uid,
                        "variable_type": variable.variable_type.value,
                        "source": "action condition",
                        **statement.to_dict()
                    })
            

            for i, step in enumerate(action.steps):
                
                action_and_step_metadata = {
                    "action_id": action.id,
                    "action_title": action.title,
                    "step_id": step.id,
                    "step_title": step.title,
                    "step_number": i+1,
                    "action_step_id": build_long_id(action.id, step.id),
                }

                for statement in step.condition.get_all_statements():
                    for variable_id in statement.get_all_variable_ids():
                        variable = self.assistant.get_variable(variable_id, action_id=action.id)
                        if variable is None:
                            print(f"Warning: Variable {variable_id} in condition of action {action.title} - {action.id}, step {i+1}, but is missing from assistant variables.")
                            results.append({
                                **action_and_step_metadata, 
                                "variable_id": variable_id, 
                                "source": "condition",
                                **statement.to_dict()
                            })
                            continue
                        if len(variable_ids) and variable.id not in variable_ids:
                            continue
                        results.append({
                            **action_and_step_metadata,
                            "variable_id": variable.id,
                            "variable_uid": variable.uid,
                            "variable_type": variable.variable_type.value,
                            "source": "condition",
                            **statement.to_dict()
                        })
                for statement in step.context.get_all_statements():
                    for variable_id in statement.get_all_variable_ids():
                        variable = self.assistant.get_variable(variable_id, action_id=action.id)
                        if variable is None:
                            print(f"Warning: Variable {variable_id} in context of action {action.title} - {action.id}, step {i+1}, but is missing from assistant variables.")
                            results.append({
                                **action_and_step_metadata, 
                                "variable_id": variable_id, 
                                "source": "context",
                                **statement.to_dict()
                            })
                            continue
                        if len(variable_ids) and variable.id not in variable_ids:
                            continue
                        results.append({
                            **action_and_step_metadata,
                            "variable_id": variable.id,
                            "variable_uid": variable.uid,
                            "variable_type": variable.variable_type.value,
                            "source": "context",
                            **statement.to_dict()
                        })
                
                if isinstance(step.resolver, CalloutResolver):
                    params = step.resolver.request_mapping.header + step.resolver.request_mapping.query
                    for param in params:
                        for variable_id in param.get_all_variable_ids():
                            variable = self.assistant.get_variable(variable_id, action_id=action.id)
                            if variable is None:
                                print(f"Warning: Variable {variable_id} in extension of action {action.title} - {action.id}, step {i+1}, but is missing from assistant variables.")
                                results.append({
                                **action_and_step_metadata, 
                                "variable_id": variable_id, 
                                "source": "extension",
                            })
                                continue
                            if len(variable_ids) and variable.id not in variable_ids:
                                continue
                            results.append({
                                **action_and_step_metadata,
                                "variable_id": variable.id,
                                "variable_uid": variable.uid,
                                "variable_type": variable.variable_type.value,
                                "source": "extension",
                                "operation": OperationType.ASSIGN.value,
                                "LHS": param.parameter,
                                "RHS": param.value.value,
                                "spel_expression": param.spel_expression
                        })
                    
                for response in step.responses:
                    for variable_id in response.get_all_variable_ids():
                        variable = self.assistant.get_variable(variable_id, action_id=action.id)
                        if variable is None:
                            print(f"Warning: Variable {variable_id} in response of action {action.title} - {action.id}, step {i+1}, but is missing from assistant variables.")
                            results.append({
                            **action_and_step_metadata, 
                            "variable_id": variable_id, 
                            "source": f"response - {response.response_type.value}",
                        })
                            continue
                        if len(variable_ids) and variable.id not in variable_ids:
                            continue
                        results.append({
                            **action_and_step_metadata,
                            "variable_id": variable.id,
                            "variable_uid": variable.uid,
                            "variable_type": variable.variable_type.value,
                            "source": f"response - {response.response_type.value}",
                            "response": str(response)
                    })
        
        handler = create_output_handler(return_as)
        return handler.handle(results)

                