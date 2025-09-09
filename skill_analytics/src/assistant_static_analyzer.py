import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

from src.action import Action
from src.entity import Entity
from src.variable import Variable

from src.utils.graph import Graph

class AssistantStaticAnalyzer:

    def __init__(self, assistant_obj):
        self.raw_obj = assistant_obj
        
        self.name = assistant_obj["name"]
        self.description = assistant_obj["description"]
        self.skill_id = assistant_obj["skill_id"]
        self.assistant_id = assistant_obj["assistant_id"]
        self.workspace_id = assistant_obj["workspace_id"]

        self.entities = AssistantStaticAnalyzer._parse_assistant_obj_for_entities(assistant_obj)

        self.actions = AssistantStaticAnalyzer._parse_assistant_obj_for_actions(assistant_obj)

        self.system_variables = AssistantStaticAnalyzer._parse_assistant_obj_for_system_variables(assistant_obj)
        self.action_variables = [action_variable for action in self.actions for action_variable in action.action_variables]

        self.variable_ids = list(sorted(set([variable for action in self.actions for variable in action.variable_ids])))

    def __repr__(self):
        return f"{self.name} - Static Analyzer ({self.assistant_id})"

    # ================================================================================
    # Getters
    # ================================================================================

    @staticmethod
    def _get_by_id_or_title(obj, title_or_id):
        for subobj in obj:
            if subobj.ID == title_or_id or subobj.title.lower() == title_or_id.lower():
                return subobj
        return None

    def get_action(self, action_title_or_id, warning=True):
        action = AssistantStaticAnalyzer._get_by_id_or_title(self.actions, action_title_or_id)
        if warning and action is None:
            print(f"Warning: could not find action with ID or title '{action_title_or_id}'")
        return action
    
    def get_variable(self, variable_title_or_id, warning=True):
        variable = AssistantStaticAnalyzer._get_by_id_or_title(self.variables, variable_title_or_id)
        if warning and variable is None:
            print(f"Warning: could not find variable with ID or title '{variable_title_or_id}'")
        return variable

    def get_entity(self, entity_id, warning=True):
        for entity in self.entities:
            if entity.ID == entity_id:
                return entity
        if warning:
            print(f"Warning: could not find variable with ID or title '{entity_id}'")
        return entity

    # ================================================================================
    # Parsing
    # ================================================================================

    @staticmethod
    def _parse_assistant_obj_for_entities(assistant_obj):

        for entity_obj in assistant_obj["workspace"]["entities"]:
            pass
            # print(entity_obj)

    @staticmethod
    def _parse_assistant_obj_for_actions(assistant_obj):
        actions = []
        for i, action_obj in enumerate(assistant_obj["workspace"]["actions"]):
            actions.append( Action(action_obj, i) )
        
        return actions
    
    @staticmethod
    def _parse_assistant_obj_for_system_variables(assistant_obj):
        system_variables = []

        for variable_obj in assistant_obj["workspace"]["variables"]:
            system_variables.append( Variable(variable_obj) )
        
        # These are extra system variables that the assistant creates by default
        default_system_variables = [
            "current_date",
            "current_time",
            "digressed_from",
            "fallback_reason", 
            "no_action_matches_count", 
            "session_history",
            "system_current_date",
            "system_current_time",
            "system_integrations", 
            "system_session_history", 
            "system_timezone",
        ]
        for system_variable_id in default_system_variables:
            system_variables.append(Variable({"variable": system_variable_id, "title": system_variable_id, "privacy": {"enabled": True}}))

        return system_variables
    
    # ================================================================================
    # Searching - Helpers
    # ================================================================================

    @staticmethod
    def _return_as(obj, return_as):

        if return_as is None:
            return obj

        if not isinstance(return_as, str):
            raise TypeError("`return_as` should be type `str`, instead got", type(return_as))

        if return_as.lower() in ["dict", "dictionary"]:
            return obj

        if return_as.lower() in ["csv", "dataframe", "df"]:
            return pd.DataFrame(obj)

        if return_as.lower() in ["json"]:
            return json.dumps(obj)

        raise ValueError(f"Unknown value for `return_as`, got '{return_as}'")

    def _get_action_id_list(self, action_title_or_id_list):
        action_ids = []
        for action_id_or_title in action_title_or_id_list:
            action = self.get_action(action_id_or_title)
            if action is not None:
                action_ids.append(action.ID)
        
        return action_ids

    def is_variable_protected(self, variable_id, source):
        
        for variable in self.system_variables:
            if variable_id == variable.ID:
                return variable.is_protected
        
        for variable in self.action_variables:
            if variable_id == variable.ID:
                return variable.is_protected
        
        if source in ["extension"]:
            return None

        print(f"Warning: Could not find `{variable_id}` in either the system or action variables")
        return False

    # ================================================================================
    # Searching - Variables
    # ================================================================================

    def get_all_variable_usage(self, return_as=None):
        results = []
        for action in self.actions:
            action_results = action.get_all_variable_usage()
            for action_result in action_results:
                variable_id = action_result["variable"]
                results.append({
                    **action_result,
                    "is_protected": self.is_variable_protected(variable_id, action_result["source"])
                })
        
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    def search_for_variables(self, *variable_ids, return_as=None):
        results = self.get_all_variable_usage(return_as="dict")
        results = [result for result in results if result["variable"] in list(variable_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)
    
    def get_all_variables_used_in_action(self, *action_title_or_id_list, return_as=None):
        action_ids = self._get_action_id_list(action_title_or_id_list)
        results = self.get_all_variable_usage(return_as="dict")
        if action_ids:
            results = [result for result in results if result["action_id"] in list(action_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    def variable_summary(self, return_as=None):
        results = []

        for action in self.actions:
            action_variable_results = action.action_variable_summary()
            for action_variable_result in action_variable_results:
                results.append({
                    **action_variable_result,
                    "source": "action_variables"
                })

        for variable in self.system_variables:
            results.append({
                **variable.summary(),
                "source": "system_variable"
            })
        
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # ================================================================================
    # Searching - Entities
    # ================================================================================

    def get_all_entity_usage(self, return_as=None):
        results = []
        for action in self.actions:
            action_results = action.get_all_entity_usage()
            for action_result in action_results:
                entity_id = action_result["entity"]
                # TODO
                # entity = self.get_entity(entity_id)
                results.append({
                    **action_result,
                    # TODO
                })
        
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    def search_for_entities(self, *entity_ids, return_as=None):
        results = self.get_all_entity_usage(return_as="dict")
        if entity_ids:
            results = [result for result in results if result["entity"] in list(entity_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)
    
    def get_all_entities_used_in_action(self, *action_title_or_id_list, return_as=None):
        action_ids = self._get_action_id_list(action_title_or_id_list)
        results = self.get_all_entity_usage(return_as="dict")
        if action_ids:
            results = [result for result in results if result["action_id"] in list(action_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # ================================================================================
    # Searching - Subactions
    # ================================================================================

    def get_all_subaction_usage(self, return_as=None):
        results = []
        for action in self.actions:
            action_results = action.get_all_subaction_usage()
            for action_result in action_results:
                results.append({
                    **action_result,
                    "subaction_title": self.get_action(action_result["subaction_id"]).title
                })
        
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    def search_for_subactions(self, *subaction_title_or_id_list, return_as=None):
        subaction_ids = self._get_action_id_list(subaction_title_or_id_list)
        results = self.get_all_subaction_usage(return_as="dict")
        if subaction_ids:
            results = [result for result in results if result["subaction_id"] in list(subaction_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)
    
    def get_all_subactions_used_in_action(self, *action_title_or_id_list, return_as=None):
        action_ids = self._get_action_id_list(action_title_or_id_list)
        results = self.get_all_subaction_usage(return_as="dict")
        if action_ids:
            results = [result for result in results if result["action_id"] in list(action_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # ================================================================================
    # Searching - Extensions
    # ================================================================================

    def get_all_extension_usage(self, return_as=None):
        results = []
        for action in self.actions:
            action_results = action.get_all_extension_usage()
            for action_result in action_results:
                results.append(action_result)
        
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # TODO: There's not a good way to identify extensions
    def search_for_extensions(self, *action_title_or_id_list, return_as=None):
        raise NotImplementedError("There is currently no good way to uniquely identify extensions. This functionality is still under development.")
    
    def get_all_extensions_used_in_action(self, *action_title_or_id_list, return_as=None):
        action_ids = self._get_action_id_list(action_title_or_id_list)
        results = self.get_all_extension_usage(return_as="dict")
        if action_ids:
            results = [result for result in results if result["action_id"] in list(action_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # ================================================================================
    # Searching - Responses
    # ================================================================================

    def get_all_responses(self, return_as=None):
        results = []
        for action in self.actions:
            action_results = action.get_all_responses()
            for action_result in action_results:
                results.append(action_result)
        
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)
    
    def get_all_responses_in_action(self, *action_title_or_id_list, return_as=None):
        action_ids = self._get_action_id_list(action_title_or_id_list)
        results = self.get_all_responses(return_as="dict")
        if action_ids:
            results = [result for result in results if result["action_id"] in list(action_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # ================================================================================
    # Searching - Get Settings
    # ================================================================================
    def get_all_action_settings(self, return_as=None):
        results = [action.get_settings() for action in self.actions]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    def search_for_action_settings(self, *action_title_or_id_list, return_as=None):
        action_ids = self._get_action_id_list(action_title_or_id_list)
        results = self.get_all_action_settings(return_as="dict")
        if action_ids:
            results = [result for result in results if result["action_id"] in list(action_ids)]
        return AssistantStaticAnalyzer._return_as(results, return_as=return_as)

    # ================================================================================
    # Graph
    # ================================================================================
    def _create_subaction_graph(self):
        G = Graph()
        for action in self.actions:
            G.add_node(action.ID)
        
        for action in self.actions:
            for step in action.steps:
                if step.subaction.subaction_exists:
                    G.add_edge(action.ID, step.subaction.ID)
        
        return G

    @staticmethod
    def _draw_network(node_list, edge_list):
        nxG = nx.DiGraph()
        nxG.add_nodes_from( node_list )
        nxG.add_edges_from( edge_list )
        pos = graphviz_layout(nxG, prog='dot')  # 'dot' gives top-down layout
        nx.draw(nxG, pos, with_labels=True, arrows=True, node_size=1000, node_color='lightblue', font_size=5)
        plt.show()

    def visualize_action_flow(self, action_title_or_id, terminal_actions=[], ignore_actions=[]):
        action = self.get_action(action_title_or_id)
        if action is None:
            return

        terminal_actions_by_ID = []
        for terminal_action_title_or_id in terminal_actions:
            terminal_action = self.get_action(terminal_action_title_or_id)
            if terminal_action is None:
                print(f"Warning: Did not find action with ID or title '{terminal_action_title_or_id}'")
            else:
                terminal_actions_by_ID.append(terminal_action.ID)
        
        ignore_actions_by_ID = []
        for ignore_action_title_or_id in ignore_actions:
            ignore_action = self.get_action(ignore_action_title_or_id)
            if ignore_action is None:
                print(f"Warning: Did not find action with ID or title '{ignore_action_title_or_id}'")
            else:
                ignore_actions_by_ID.append(ignore_action.ID)

        G = self._create_subaction_graph()
        subG = G.get_connected_subgraph(action.ID, terminal_actions_by_ID, ignore_actions_by_ID)

        node_list = [self.get_action(action_id).title for action_id in subG.nodes]
        edge_list = [(self.get_action(action_id), self.get_action(subaction_id)) for action_id, neighbors in subG.Adj.items() for subaction_id in neighbors]

        # print( json.dumps(node_list, indent=4) )
        # print( json.dumps(edge_list, indent=4) )
        AssistantStaticAnalyzer._draw_network(node_list, edge_list)