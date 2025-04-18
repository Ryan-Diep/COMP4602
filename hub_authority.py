import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

adj_matrix = np.load("balanced-ge2.npy")
G = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)  # HITS needs a directed graph

hubs, authorities = nx.hits(G)

avg_hub = sum(hubs.values()) / len(hubs)
avg_auth = sum(authorities.values()) / len(authorities)

sorted_hubs = sorted(hubs.values(), reverse=True)
sorted_auths = sorted(authorities.values(), reverse=True)

plt.figure(figsize=(12, 6))
plt.bar(range(len(sorted_hubs)), sorted_hubs, color='orange', edgecolor='black')
plt.axhline(y=avg_hub, color='red', linestyle='--', label=f'Avg Hub = {avg_hub:.5f}')
plt.title("Hub Score Distribution")
plt.xlabel("Nodes (sorted by Hub Score)")
plt.ylabel("Hub Score")
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
plt.bar(range(len(sorted_auths)), sorted_auths, color='purple', edgecolor='black')
plt.axhline(y=avg_auth, color='red', linestyle='--', label=f'Avg Authority = {avg_auth:.5f}')
plt.title("Authority Score Distribution")
plt.xlabel("Nodes (sorted by Authority Score)")
plt.ylabel("Authority Score")
plt.legend()
plt.tight_layout()
plt.show()

print("Average Hub Score:", avg_hub)
print("Average Authority Score:", avg_auth)
