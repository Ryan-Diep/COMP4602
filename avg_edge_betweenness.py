import numpy as np
import networkx as nx

adj_matrix = np.load("balanced-ge2.npy")
G = nx.from_numpy_array(adj_matrix)

edge_betweenness = nx.edge_betweenness_centrality(G)

average_edge_betweenness = sum(edge_betweenness.values()) / len(edge_betweenness)

print("Average Edge Betweenness Centrality:", average_edge_betweenness)
