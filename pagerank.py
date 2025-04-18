import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

adj_matrix = np.load("balanced-ge1.npy")
G = nx.from_numpy_array(adj_matrix)

pagerank_scores = nx.pagerank(G)

#Average PageRank (should be 1/N in total)
avg_pagerank = sum(pagerank_scores.values()) / len(pagerank_scores)

# get top 10 nodes by PageRank
top_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:10]

# print("Average PageRank:", avg_pagerank)
# print("\nTop 10 Nodes by PageRank:")
# for node, score in top_pagerank:
#     print(f"Node {node}: {score:.5f}")

# sorted_scores = sorted(pagerank_scores.values(), reverse=True)

# plt.figure(figsize=(12, 6))
# plt.bar(range(len(sorted_scores)), sorted_scores, color='skyblue', edgecolor='black')
# plt.axhline(y=avg_pagerank, color='red', linestyle='--', label=f'Average = {avg_pagerank:.5f}')
# plt.title("PageRank Distribution Across Nodes")
# plt.xlabel("Nodes (sorted by PageRank)")
# plt.ylabel("PageRank Score")
# plt.legend()
# plt.tight_layout()
# plt.show()


# Get the top 20 nodes by PageRank
top_20_pagerank = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:20]

# Separate the nodes and their scores for plotting
top_20_nodes, top_20_scores = zip(*top_20_pagerank)

# Plot the top 20 nodes
plt.figure(figsize=(12, 6))
plt.bar(range(len(top_20_scores)), top_20_scores, color='skyblue', edgecolor='black')
plt.xticks(range(len(top_20_nodes)), top_20_nodes, rotation=45)
plt.title("Top 20 Nodes by PageRank")
plt.xlabel("Nodes")
plt.ylabel("PageRank Score")
plt.tight_layout()
plt.show()