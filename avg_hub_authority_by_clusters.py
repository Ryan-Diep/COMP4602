import numpy as np
import networkx as nx
import community as community_louvain  # pip install python-louvain

# Load graph
adj_matrix = np.load("adjacency_matrix.npy")
G = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)

# 1. Detect communities using Louvain method (on undirected version)
undirected_G = G.to_undirected()
partition = community_louvain.best_partition(undirected_G)

# Reverse map: cluster_id -> list of nodes
from collections import defaultdict
clusters = defaultdict(list)
for node, comm in partition.items():
    clusters[comm].append(node)

# 2. Compute HITS (hub & authority)
hub_scores, auth_scores = nx.hits(G)

# 3. Calculate average scores per cluster
cluster_results = []
for cid, nodes in clusters.items():
    avg_hub = sum(hub_scores[n] for n in nodes) / len(nodes)
    avg_auth = sum(auth_scores[n] for n in nodes) / len(nodes)
    cluster_results.append((cid, len(nodes), avg_hub, avg_auth))

# Sort by authority score
cluster_results.sort(key=lambda x: x[3], reverse=True)

# Display results
print("Cluster ID | Size | Avg Hub Score | Avg Authority Score")
for cid, size, avg_hub, avg_auth in cluster_results:
    print(f"{cid:10d} | {size:4d} | {avg_hub:.5f}     | {avg_auth:.5f}")
