import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import time
from model import RumorSpreadModel, MisinformationModel
import pandas as pd

if __name__ == "__main__":
    # Load your network
    adj_matrix = np.load("med.npy")
    G = nx.from_numpy_array(adj_matrix)
    mapping = {old_label: int(i) for i, old_label in enumerate(G.nodes())}
    G = nx.relabel_nodes(G, mapping)
    
    print(f"Loaded network with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    # Create model directly (choose either RumorSpreadModel or MisinformationModel)
    # You can adjust parameters as needed
    model = RumorSpreadModel(
        custom_network=G,
        initial_outbreak_size=5,
        prob_infect=0.05,
        prob_make_denier=0.02,
        prob_accept_deny=0.05
    )
    
    # Record start time
    start_time = time.time()
    
    # Run for 100 steps
    for i in range(100):
        if i % 10 == 0:
            print(f"Step {i}...")
        model.step()
    
    # Record end time and print duration
    end_time = time.time()
    print(f"Simulation completed in {end_time - start_time:.2f} seconds")
    
    # Get results from data collector
    results_df = model.datacollector.get_model_vars_dataframe()
    
    # Save results to CSV
    results_df.to_csv("simulation_results.csv")
    print(f"Results saved to simulation_results.csv")
    
    # Create a visualization of the final state
    plt.figure(figsize=(10, 8))
    
    # Plot the network with final states
    pos = nx.spring_layout(G, seed=42)  # Position nodes using spring layout
    
    # Define node colors based on states
    node_colors = []
    for node in G.nodes():
        agent = model.agents[node]
        if agent.state == "INFECTED" or agent.state == "Infected":
            node_colors.append('red')
        elif agent.state == "Exposed":
            node_colors.append('orange')
        elif agent.state == "VACCINATED" or agent.state == "Resistant":
            node_colors.append('blue')
        else:  # "NEUTRAL" or "Susceptible"
            node_colors.append('gray')
    
    # Draw the network
    nx.draw(G, pos, node_color=node_colors, node_size=30, alpha=0.7, with_labels=False)
    
    # Add a legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Infected'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Neutral/Susceptible'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Vaccinated/Resistant'),
    ]
    if isinstance(model, MisinformationModel):
        legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Exposed'))
    
    plt.legend(handles=legend_elements, loc='upper right')
    plt.title(f"Network State after 100 steps ({G.number_of_nodes()} nodes)")
    
    # Save the plot
    plt.savefig("network_final_state.png", dpi=300)
    print("Network visualization saved to network_final_state.png")
    
    # Also create a chart showing state changes over time
    plt.figure(figsize=(10, 6))
    results_df.plot(figsize=(10, 6))
    plt.title("State Changes Over Time")
    plt.xlabel("Step")
    plt.ylabel("Number of Agents")
    plt.grid(True, alpha=0.3)
    plt.savefig("state_changes.png", dpi=300)
    print("State change chart saved to state_changes.png")