from typing import Any, Optional
from io import BytesIO

from src.models.assistant import Assistant
from src.models.resolvers import InvokeActionAndEndResolver, InvokeActionResolver
from src.utils.graph import Graph

# TODO: Needs testing

class SubactionAnalyzer:
    """Analyzer for generating subaction flow graphs."""
    
    def __init__(self, assistant: Assistant):
        self.assistant = assistant

    def generate_subaction_flow_graph(
        self,
        start_action_id: Optional[str] = None,
        include_action_titles: bool = True
    ) -> BytesIO:
        """
        Generate a flow graph of subactions and return as PNG bytes.
        
        Args:
            start_action_id: Optional action ID to start from. If None, generates full graph.
            include_action_titles: Whether to include action titles in node labels.
            
        Returns:
            BytesIO object containing the PNG image data that can be saved by the caller.
        """
        try:
            import graphviz
        except ImportError:
            raise ImportError(
                "graphviz package is required for generating flow graphs. "
                "Install it with: pip install graphviz"
            )
        
        # Build the graph
        graph = self._build_subaction_graph()
        
        # Create graphviz Digraph
        dot = graphviz.Digraph(comment='Subaction Flow Graph')
        dot.attr(rankdir='TB')  # Top to bottom layout
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        
        # Determine which nodes to include
        if start_action_id:
            if start_action_id not in graph.nodes:
                raise ValueError(f"Action ID '{start_action_id}' not found in assistant")
            
            # Get connected subgraph starting from the specified action
            terminal_actions = set()
            ignore_actions = set()
            subgraph = graph.get_connected_subgraph(start_action_id, terminal_actions, ignore_actions)
            nodes_to_include = subgraph.get_node_ID_list()
            edges_to_include = subgraph.get_edge_list_node_IDs()
        else:
            # Include all nodes and edges
            nodes_to_include = graph.get_node_ID_list()
            edges_to_include = graph.get_edge_list_node_IDs()
        
        # Add nodes
        for node_id in nodes_to_include:
            node_data = graph.get_node_data(node_id)
            action = self.assistant.actions.get(node_id)
            
            if action:
                if include_action_titles:
                    label = f"{action.title}\n({node_id})"
                else:
                    label = node_id
                
                # Color code based on whether action has subactions
                has_subactions = node_data.get('has_subactions', False)
                fillcolor = 'lightgreen' if has_subactions else 'lightblue'
                
                dot.node(node_id, label=label, fillcolor=fillcolor)
            else:
                # Action not found (shouldn't happen, but handle gracefully)
                dot.node(node_id, label=f"{node_id}\n(not found)", fillcolor='lightcoral')
        
        # Add edges
        for u, v in edges_to_include:
            edge_data = graph.get_edge_data(u, v)
            
            # Customize edge appearance based on resolver type
            if edge_data.get('ends_action', False):
                # InvokeActionAndEndResolver - dashed line
                dot.edge(u, v, label='invoke & end', style='dashed', color='red')
            else:
                # InvokeActionResolver - solid line
                dot.edge(u, v, label='invoke', color='blue')
        
        # Render to PNG bytes
        png_bytes = dot.pipe(format='png')
        png_buffer = BytesIO(png_bytes)
        
        # Reset buffer position to beginning
        png_buffer.seek(0)
        
        return png_buffer

    def _build_subaction_graph(self) -> Graph:
        """
        Build a directed graph of subaction relationships.
        
        Returns:
            Graph object with actions as nodes and subaction invocations as edges.
        """
        graph = Graph()
        
        # First pass: Add all actions as nodes
        for action_id, action in self.assistant.actions.items():
            has_subactions = False
            
            # Check if this action invokes any subactions
            for step in action.steps:
                resolver = step.resolver
                if isinstance(resolver, (InvokeActionResolver, InvokeActionAndEndResolver)):
                    has_subactions = True
                    break
            
            graph.add_node(action_id, node_data={
                'title': action.title,
                'has_subactions': has_subactions
            })
        
        # Second pass: Add edges for subaction invocations
        for action_id, action in self.assistant.actions.items():
            for i, step in enumerate(action.steps):
                resolver = step.resolver
                
                # Check if resolver is an invoke action type
                if isinstance(resolver, (InvokeActionResolver, InvokeActionAndEndResolver)):
                    subaction_id = resolver.subaction_id
                    
                    # Only add edge if subaction exists
                    if subaction_id in self.assistant.actions:
                        ends_action = isinstance(resolver, InvokeActionAndEndResolver)
                        
                        edge_data = {
                            'step_id': step.id,
                            'step_title': step.title,
                            'step_number': i + 1,
                            'ends_action': ends_action,
                            'policy': resolver.policy,
                            'result_variable_id': resolver.result_variable_id
                        }
                        
                        graph.add_edge(action_id, subaction_id, edge_data=edge_data)
        
        return graph

    def get_subaction_statistics(self) -> dict[str, Any]:
        """
        Get statistics about subaction usage in the assistant.
        
        Returns:
            Dictionary containing various statistics about subactions.
        """
        graph = self._build_subaction_graph()
        
        total_actions = len(self.assistant.actions)
        actions_with_subactions = sum(
            1 for node_id in graph.get_node_ID_list()
            if graph.get_node_data(node_id).get('has_subactions', False)
        )
        
        total_subaction_calls = len(graph.get_edge_list_node_IDs())
        
        # Find actions that are never invoked as subactions
        invoked_actions = set(v for u, v in graph.get_edge_list_node_IDs())
        root_actions = set(graph.get_node_ID_list()) - invoked_actions
        
        # Find actions that invoke themselves (recursive)
        recursive_actions = [
            action_id for action_id in graph.get_node_ID_list()
            if graph.is_edge_exists(action_id, action_id)
        ]
        
        return {
            'total_actions': total_actions,
            'actions_with_subactions': actions_with_subactions,
            'total_subaction_calls': total_subaction_calls,
            'root_actions_count': len(root_actions),
            'root_actions': list(root_actions),
            'recursive_actions_count': len(recursive_actions),
            'recursive_actions': recursive_actions
        }

"""
analyzer = SubactionAnalyzer(assistant)
png_buffer = analyzer.generate_subaction_flow_graph()

# Caller can save the PNG if needed
with open("subaction_flow.png", "wb") as f:
    f.write(png_buffer.getvalue())
"""