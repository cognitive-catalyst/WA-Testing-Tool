import copy
from collections import deque

class Graph:

    def __init__(self):
        self.nodes = {}
        self.Adj = {}
    
    def add_node(self, node_ID, node_data={}):
        if node_ID in self.nodes:
            # TODO: maybe I'll merge the node_data somehow (define a custom function maybe)
            return
        self.nodes[node_ID] = copy.deepcopy(node_data)
    
    def add_edge(self, u, v, edge_data={}, edge_merge_func=None):
        if edge_merge_func is None:
            # e = edge that already exists
            # f = new duplicate edge
            edge_merge_func = lambda e, f: e if e else f
        
        # u, v are node IDs
        if u not in self.nodes:
            raise ValueError(f"Origin node {u} is not found in the node list")
        if v not in self.nodes:
            raise ValueError(f"Destination node {v} is not found in the node list")

        if u not in self.Adj:
            self.Adj[u] = {}
        
        # the edge already exists
        if v in self.Adj[u]:
            self.Adj[u][v] = edge_merge_func(self.Adj[u][v], copy.deepcopy(edge_data))
        # the edge does not exist
        else:
            self.Adj[u][v] = copy.deepcopy(edge_data)

    def is_edge_exists(self, u, v):
        if u not in self.Adj:
            return False
        if v not in self.Adj[u]:
            return False
        return True

    def get_node_data(self, node_ID):
        return self.nodes[node_ID]

    def get_edge_data(self, u, v):
        return self.Adj[u][v]
    
    def get_neighbors(self, node_ID):
        return self.Adj.get(node_ID, {})
    
    def get_node_ID_list(self):
        return list(self.nodes.keys())
    
    def get_edge_list_node_IDs(self):
        return [(u, v) for u, neighbors in self.Adj.items() for v, edge_data in neighbors.items()]

    def get_node_data_list(self):
        return list(self.nodes.values())
    
    def get_edge_list_node_data(self):
        return [(self.nodes[u], self.nodes[v]) for u, neighbors in self.Adj.items() for v, edge_data in neighbors.items()]

    def get_edge_dictionary(self):
        return {(u, v): edge_data for u, neighbors in self.Adj.items() for v, edge_data in neighbors.items()}
    
    # Modified BFS
    # I calculate depth because why not, but it's not strictly necessary
    def get_connected_subgraph(self, start_ID, terminal_actions, ignore_actions):
        subG = Graph()
        subG.add_node(start_ID)

        visited = set()
        queue = deque([(start_ID, 0)])
        
        while queue:
            node_ID, depth = queue.popleft()
            if node_ID not in visited:
                visited.add(node_ID)
                
                if node_ID != start_ID and node_ID in ignore_actions:
                    continue
                
                subG.add_node(node_ID)

                if node_ID != start_ID and node_ID in terminal_actions:
                    continue

                # Add all unvisited neighbors to the queue with incremented depth
                for neighbor_ID in self.get_neighbors(node_ID):
                    
                    if neighbor_ID not in ignore_actions:
                        subG.add_node(neighbor_ID)
                        subG.add_edge(node_ID, neighbor_ID)
                    
                    queue.append((neighbor_ID, depth + 1))
        
        return subG