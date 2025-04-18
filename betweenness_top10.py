import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

adj_matrix = np.load("adjacency_matrix.npy")
G = nx.from_numpy_array(adj_matrix)

betweenness = nx.betweenness_centrality(G)

top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
top_nodes = [node for node, _ in top_betweenness]

pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(12, 8))

nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=50)

nx.draw_networkx_nodes(G, pos, nodelist=top_nodes, node_color='red', node_size=100)

nx.draw_networkx_edges(G, pos, alpha=0.3)

labels = {node: str(node) for node in top_nodes}
nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black')

plt.title("Top 10 Nodes by Betweenness Centrality (Highlighted in Red)")
plt.axis('off')
plt.tight_layout()
plt.savefig("betweenness_top10.png", dpi=300)  # Save the image
plt.show()
