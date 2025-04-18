import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

adj_matrix = np.load("adjacency_matrix-no-filter-COAID.npy")
G = nx.from_numpy_array(adj_matrix)

edge_betweenness = nx.edge_betweenness_centrality(G)

top_edges = sorted(edge_betweenness.items(), key=lambda x: x[1], reverse=True)[:10]
top_edge_list = [edge for edge, _ in top_edges]

pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(12, 8))
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=50)

nx.draw_networkx_edges(G, pos, edgelist=[e for e in G.edges() if e not in top_edge_list], alpha=0.3, edge_color='gray')

nx.draw_networkx_edges(G, pos, edgelist=top_edge_list, edge_color='red', width=2)

#Label nodes (only useful if desired)
nx.draw_networkx_labels(G, pos, font_size=7)

plt.title("Top 10 Edges by Betweenness Centrality (Bridges Highlighted in Red)")
plt.axis('off')
plt.tight_layout()
plt.savefig("edge_betweenness_top10.png", dpi=300)  # Save the image
plt.show()
