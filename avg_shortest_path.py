import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

adj_matrix = np.load("balanced-ge2.npy")

G = nx.from_numpy_array(adj_matrix)
if not nx.is_connected(G):
    #focuses on the largest connected component
    largest_cc = max(nx.connected_components(G), key=len)
    G = G.subgraph(largest_cc).copy()

path_lengths = dict(nx.all_pairs_shortest_path_length(G))
all_lengths = [dist for d in path_lengths.values() for dist in d.values() if dist > 0]

avg_length = sum(all_lengths) / len(all_lengths)
print("Average Shortest Path Length:", avg_length)

plt.figure(figsize=(10, 6))
plt.hist(all_lengths, bins=range(1, max(all_lengths)+2), color='skyblue', edgecolor='black')
plt.axvline(avg_length, color='red', linestyle='--', label=f'Avg = {avg_length:.2f}')
plt.title("Distribution of Shortest Path Lengths")
plt.xlabel("Shortest Path Length")
plt.ylabel("Number of Node Pairs")
plt.legend()
plt.tight_layout()
plt.show()
