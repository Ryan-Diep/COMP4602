import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

adj_matrix = np.load("adjacency_matrix.npy")

G = nx.from_numpy_array(adj_matrix)

#network stats
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())
print("Network density:", nx.density(G))
print("Connected components:", nx.number_connected_components(G))
print("Largest connected component size:", len(max(nx.connected_components(G), key=len)))
print("Average clustering coefficient:", nx.average_clustering(G))
if nx.is_connected(G):
    print("Average path length:", nx.average_shortest_path_length(G))
else:
    print("Graph is not fully connected.")

degrees = [deg for _, deg in G.degree()]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=30, color='skyblue', edgecolor='black')
plt.title("Degree Distribution of the Network")
plt.xlabel("Degree")
plt.ylabel("Number of Nodes")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.savefig("degree_distribution_histogram.png")
