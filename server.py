from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice, Slider
from model import RumorSpreadModel, MisinformationModel

def network_portrayal(G):
    nodes = []
    edges = []

    for node_id, node_data in G.nodes(data=True):
        agent = node_data.get("agent", None)
        if agent is None:
            continue

        portrayal = {
            "id": node_id,
            "color": "gray",
            "size": 6,
            "label": str(agent.unique_id),
            "tooltip": f"ID: {agent.unique_id}, State: {agent.state}",
            "shape": "circle"
        }

        # Handle both model's states
        if "INFECTED" in agent.state:
            portrayal["color"] = "red"
        elif "Exposed" in agent.state:
            portrayal["color"] = "orange"
        elif "Resistant" in agent.state or "VACCINATED" in agent.state:
            portrayal["color"] = "blue"
        elif "NEUTRAL" in agent.state or "Susceptible" in agent.state:
            portrayal["color"] = "gray"

        nodes.append(portrayal)

    for source, target in G.edges():
        edges.append({"source": source, "target": target, "color": "lightgray"})

    return {"nodes": nodes, "edges": edges}

network = NetworkModule(network_portrayal, 500, 864)

# Create charts for both models
rumor_chart = ChartModule([
    {"Label": "Infected", "Color": "red"},
    {"Label": "Neutral", "Color": "gray"},
    {"Label": "Vaccinated", "Color": "blue"}
])

misinfo_chart = ChartModule([
    {"Label": "Susceptible", "Color": "gray"},
    {"Label": "Exposed", "Color": "orange"},
    {"Label": "Infected", "Color": "red"},
    {"Label": "Resistant", "Color": "blue"},
])

model_params = {
    "model_type": Choice(
        "Model Type", 
        value="Rumor Spread",
        choices=["Rumor Spread", "Misinformation"]
    ),
    "num_agents": Slider("Number of Agents", 1000, 100, 5000, 100),
    "initial_outbreak_size": Slider("Initially Infected", 50, 1, 500, 1),
}

rumor_params = {
    "avg_node_degree": Slider("Avg Node Degree", 5, 1, 10, 1),
    "prob_infect": Slider("Infection Probability", 0.3, 0.01, 1, 0.01),
    "prob_accept_deny": Slider("Denial Acceptance", 0.2, 0.01, 1, 0.01),
    "prob_make_denier": Slider("Denier Creation", 0.1, 0.01, 1, 0.01),
}

misinfo_params = {
    "m_links": Slider("Links per New Node", 4, 1, 10, 1),
    "exposure_threshold": Slider("Exposure Threshold", 2, 1, 10, 1),
    "fact_checker_ratio": Slider("Fact Checker Ratio", 0.02, 0.0, 0.5, 0.01),
    "spread_probability": Slider("Spread Probability", 0.6, 0.0, 1.0, 0.05),
}

class ModelWrapper:
    def __init__(self, model_type, *args, **kwargs):
        filtered_kwargs = kwargs.copy()
        
        custom_network = filtered_kwargs.pop('custom_network', None)

        if model_type == "Rumor Spread":
            rumor_kwargs = {
                k: filtered_kwargs[k] 
                for k in ["num_agents", "avg_node_degree", "initial_outbreak_size", 
                         "prob_infect", "prob_accept_deny", "prob_make_denier"]
                if k in filtered_kwargs
            }
            rumor_kwargs.pop('initial_outbreak_size', None)
            self.model = RumorSpreadModel(**rumor_kwargs, custom_network=custom_network)
        else:
            misinfo_kwargs = {
                k: filtered_kwargs[k] 
                for k in ["num_agents", "m_links", 
                         "exposure_threshold", "fact_checker_ratio", "spread_probability"]
                if k in filtered_kwargs
            }
            self.model = MisinformationModel(**misinfo_kwargs, custom_network=custom_network)
    
    def step(self):
        self.model.step()
    
    def __getattr__(self, name):
        # Delegate unknown attributes to the underlying model
        return getattr(self.model, name)

server = ModularServer(
    ModelWrapper,
    [network, rumor_chart, misinfo_chart],
    "Contagion Model Comparison",
    {**model_params, **rumor_params, **misinfo_params}
)

server.port = 8521