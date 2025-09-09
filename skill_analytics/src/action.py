from src.step import Step
from src.condition import Condition
from src.variable import Variable

class Action:

    def __init__(self, action_obj, index):
        self.raw_obj = action_obj
        self.index = index
        
        self.ID = action_obj["action"]
        self.title = action_obj.get("title")
        self.description = action_obj.get("description")

        self.conditions = Condition(action_obj.get("condition", {}))

        self.action_variables = [Variable(variable_obj) for variable_obj in action_obj.get("variables", {})]
        
        self.steps = [Step(step_obj, j) for j, step_obj in enumerate(action_obj["steps"])]
        
        self.ask_clarifying_question = (not action_obj.get("disambiguation_opt_out", True))
        self.allowed_from = action_obj.get("topic_switch", {}).get("allowed_from", True)
        self.allowed_into = action_obj.get("topic_switch", {}).get("allowed_into", True)
        if self.allowed_from != self.allowed_into:
            raise ValueError(f"In action {self.title} the values `allowed_from` and `allowed_into` are different, and they shouldn't be.")
        self.change_coversation_topic = self.allowed_into
        self.never_return = action_obj.get("topic_switch", {}).get("never_return", False)

        # for step in self.steps:
        #     for action_variable in self.action_variables:
        #         if action_variable.ID == step.ID:
        #             step.attach_action_variable(action_variable)

        # self.extensions = [step.extension for step in self.steps if step.extension.extension_exists]
        # self.subactions = [step.subaction for step in self.steps if step.subaction.subaction_exists]

        self.variable_ids = list(sorted(set([variable for step in self.steps for variable in step.variable_ids] + self.conditions.variable_ids)))

    def __repr__(self):
        return self.title

    def to_json(self):
        return {
            "ID": self.ID,
            "title": self.title,
            "description": self.description,
            "index": self.index,
            "steps": self.steps.to_json(),
            "variables": self.variable_ids
        }

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_action_variables(action_variables_obj, action_id):
        action_variables = []

        for variable_obj in action_variables_obj:
            action_variables.append( Variable(variable_obj, action_id=action_id) )
        
        return action_variables

    # ================================================================================
    # Searching
    # ================================================================================

    def get_all_variable_usage(self):
        results = []
        
        condition_results = self.conditions.get_all_variable_usage()
        for condition_result in condition_results:
            results.append({
                "action_id": self.ID,
                "action_title": self.title,
                "step_id": None,
                "step_title": None,
                "step_number": 0,
                **condition_result
            })
        
        for step in self.steps:
            step_results = step.get_all_variable_usage()
            for step_result in step_results:
                results.append({
                    "action_id": self.ID,
                    "action_title": self.title,
                    **step_result
                })

        return results
    
    def get_all_entity_usage(self):
        results = []
        
        condition_results = self.conditions.get_all_entity_usage()
        for condition_result in condition_results:
            results.append({
                "action_id": self.ID,
                "action_title": self.title,
                "step_id": None,
                "step_title": None,
                "step_number": 0,
                **condition_result
            })
        
        for step in self.steps:
            step_results = step.get_all_entity_usage()
            for step_result in step_results:
                results.append({
                    "action_id": self.ID,
                    "action_title": self.title,
                    **step_result
                })

        return results
    
    def get_all_subaction_usage(self):
        results = []

        for step in self.steps:
            step_results = step.get_all_subaction_usage()
            for step_result in step_results:
                results.append({
                    "action_id": self.ID,
                    "action_title": self.title,
                    **step_result
                })

        return results
    
    def get_all_extension_usage(self):
        results = []

        for step in self.steps:
            step_results = step.get_all_extension_usage()
            for step_result in step_results:
                results.append({
                    "action_id": self.ID,
                    "action_title": self.title,
                    **step_result
                })

        return results
    
    def action_variable_summary(self):
        results = []

        for action_variable in self.action_variables:
            step = None
            for step in self.steps:
                if action_variable.ID == step.ID:
                    break

            results.append({
                "action_id": self.ID,
                "action_title": self.title,
                "step_id": step.ID if step else None,
                "step_title": step.title if step else None,
                "step_number": step.step_number if step else None,
                **action_variable.summary(),
            })
        
        return results

    def get_all_responses(self):
        results = []
        for step in self.steps:
            step_results = step.get_all_responses()
            for step_result in step_results:
                results.append({
                    "action_id": self.ID,
                    "action_title": self.title,
                    **step_result
                })

        return results
    
    def get_settings(self):
        return {
            "action_id": self.ID,
            "action_title": self.title,
            "ask_clarifying_question": self.ask_clarifying_question,
            "change_coversation_topic": self.change_coversation_topic,
            "never_return" : self.never_return,
        }