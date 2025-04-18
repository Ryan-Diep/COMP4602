import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def calculate_clustering_coefficients_with_networkx(adj_matrix):
    # Create a directed graph from the adjacency matrix
    G = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)
    
    # Calculate clustering coefficients for all nodes
    clustering_coeffs = nx.clustering(G, nodes=G.nodes(), weight=None)
    
    # Convert the result to a numpy array
    clustering_coeffs_array = np.array([clustering_coeffs[node] for node in G.nodes()])
    
    return clustering_coeffs_array

def calculate_average_clustering_coefficient(adj_matrix):
    # Create a directed graph from the adjacency matrix
    G = nx.from_numpy_array(adj_matrix, create_using=nx.DiGraph)
    
    # Calculate the average clustering coefficient
    avg_clustering_coeff = nx.average_clustering(G, weight=None)
    
    return avg_clustering_coeff


# Example usage:
if __name__ == "__main__":
    # Load an example adjacency matrix
    # path = "high-truth-ge1.npy"  # Replace with your file path
    path = "balanced-ge2.npy"  # Replace with your file path
    adj_matrix = np.load(path)

    clustering_coeffs = calculate_clustering_coefficients_with_networkx(adj_matrix)
    avg_clustering_coeff = calculate_average_clustering_coefficient(adj_matrix)
    print(clustering_coeffs.sum())
    print("Clustering Coefficients:")
    print(clustering_coeffs)
    print("average Clustering Coefficients:")
    print(avg_clustering_coeff)

    # Optional: Save the result
    np.save("clustering_coefficients.npy", clustering_coeffs)
