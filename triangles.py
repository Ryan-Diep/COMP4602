import numpy as np
import networkx as nx

def count_triangles(adjacency_matrix):
    # Create a graph from the adjacency matrix
    G = nx.from_numpy_array(adjacency_matrix)
    
    # Count triangles using NetworkX
    triangles = nx.triangles(G)
    
    # Sum up the triangle counts and divide by 3 (each triangle is counted 3 times)
    total_triangles = sum(triangles.values()) // 3
    
    return total_triangles

if __name__ == "__main__":
    # Example usage
    # Replace this with your own adjacency matrix
    adj_matrix = np.load("balanced-ge2.npy")
    
    num_triangles = count_triangles(adj_matrix)
    print(f"Number of triangles in the graph: {num_triangles}")