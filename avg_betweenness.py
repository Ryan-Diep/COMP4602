import numpy as np
import networkx as nx

adj_matrix = np.load("adjacency_matrix.npy")
G = nx.from_numpy_array(adj_matrix)

betweenness = nx.betweenness_centrality(G)

average_betweenness = sum(betweenness.values()) / len(betweenness)

print("Average Betweenness Centrality:", average_betweenness)
