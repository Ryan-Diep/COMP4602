import numpy as np
import networkx as nx
from server import server, ModelWrapper

if __name__ == "__main__":
    # adj_matrix = np.load("adjacency_matrix-no-filter-twitter15.npy")
    # adj_matrix = np.load("adjacency_matrix-no-filter.npy")
    adj_matrix = np.load("adjacency_matrix.npy")

    G = nx.from_numpy_array(adj_matrix)
    mapping = {old_label: int(i) for i, old_label in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)
    
    print(f"Loaded network with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    custom_network = G
    server.model_cls = lambda **kwargs: ModelWrapper(
        kwargs.pop("model_type"), 
        custom_network=custom_network, 
        **kwargs
    )

    server.launch()
