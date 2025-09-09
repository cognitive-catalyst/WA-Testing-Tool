from src.condition import Condition
from src.context import Context
from src.response_types import TextResponse, OptionResponse, DynamicOptionResponse, ValidationResponse
from src.extension import Extension
from src.subaction import SubAction
from src.variable import Variable


class Step:

    name = "step"

    def __init__(self, step_obj, index):
        self.raw_obj = step_obj
        self.index = index
        self.step_number = index+1
        
        self.ID = step_obj.get("step")
        self.title = step_obj.get("title")
        self.next_step_id = step_obj.get("next_step")
        
        condition_obj = step_obj.get("condition", {})
        context_obj = step_obj.get("context", {})
        output_obj = step_obj.get("output", {})
        handlers_obj = step_obj.get("handlers", [])
        questions_obj = step_obj.get("question", {})
        resolver_obj = step_obj.get("resolver", {})

        self.condition = Condition(condition_obj)
        self.context = Context(context_obj)

        self.text = TextResponse(output_obj)
        self.static_buttons = OptionResponse(output_obj, questions_obj)
        # self.dynamic_buttons = OptionResponse(output_obj, handlers_obj, questions_obj)
        self.validation = ValidationResponse(handlers_obj)
        
        self.extension = Extension(resolver_obj)
        self.subaction = SubAction(resolver_obj)

        self.entity_id = questions_obj.get("entity", None)
        self.resolver_type = resolver_obj.get("type", "continue")
        self.is_end_action = Step._parse_resolver_type(self.resolver_type)

        self.attributes_to_search = [
            self.condition,
            self.context,
            self.text,
            self.static_buttons,
            self.validation,
            self.subaction,
            self.extension
        ]

        self.variable_ids = list(sorted(set([variable for attribute in self.attributes_to_search for variable in attribute.variable_ids if variable is not None])))

    def __repr__(self):
        if self.title:
            return f"Step {self.index+1} - {self.title}"
        return f"Step {self.index+1}"

    def __bool__(self):
        return self.ID is not None

    def to_json(self):
        return {
            "ID": self.ID,
            "title": self.title,
            "index": self.index,
            "step_number": self.index+1,
            "step_protected": self.is_protected,
            **{attribute.name: attribute.to_json() for attribute in self.attributes_to_search},
            "variables": self.variable_ids
        }

    # ================================================================================
    # Parsing
    # ================================================================================
    
    @staticmethod
    def _parse_resolver_type(resolver_type):
        return resolver_type in ["end_action", "invoke_another_action_and_end"]

    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []
        for attribute in self.attributes_to_search:
            attribute_results = attribute.get_all_variable_usage()
            for attribute_result in attribute_results:
                results.append({
                    "step_id": self.ID,
                    "step_title": self.title,
                    "step_number": self.step_number,
                    **attribute_result
                })
        return results
    
    def get_all_entity_usage(self):
        results = []
        if self.entity_id:
            results.append({
                "step_id": self.ID,
                "step_title": self.title,
                "step_number": self.step_number,
                "entity": self.entity_id,
                "source": "customer_response"
            })

        for attribute in self.attributes_to_search:
            # TODO: do this properly later
            if hasattr(attribute, 'get_all_entity_usage') and callable(getattr(attribute, 'get_all_entity_usage')):
                attribute_results = attribute.get_all_entity_usage()
                for attribute_result in attribute_results:
                    results.append({
                        "step_id": self.ID,
                        "step_title": self.title,
                        "step_number": self.step_number,
                        **attribute_result
                    })
        
        return results

    def get_all_subaction_usage(self):
        results = []
        if self.subaction:
            results.append({
                "step_id": self.ID,
                "step_title": self.title,
                "step_number": self.step_number,
                "subaction_id": self.subaction.ID
            })
        return results
    
    def get_all_extension_usage(self):
        results = []
        if self.extension:
            results.append({
                "step_id": self.ID,
                "step_title": self.title,
                "step_number": self.step_number,
                "extension_method": self.extension.method,
                "extension_path": self.extension.path
            })
        return results
    
    def get_all_responses(self):
        results = []
        results.extend(self.text.get_all_responses())
        results.extend(self.static_buttons.get_all_responses())
        results.extend(self.validation.get_all_responses())

        return [{
            "step_id": self.ID,
            "step_title": self.title,
            "step_number": self.step_number,
            **result
        } for result in results]