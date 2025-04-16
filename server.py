from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice, NumberInput
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
    "initial_outbreak_size": NumberInput("Initially Infected", value=5),
}

rumor_params = {
    "prob_infect": NumberInput("Infection Probability", value=0.05),
    "prob_accept_deny": NumberInput("Denial Acceptance", value=0.05),
    "prob_make_denier": NumberInput("Denier Creation", value=0.05),
}

misinfo_params = {
    "exposure_threshold": NumberInput("Exposure Threshold", value=2),
    "fact_checker_ratio": NumberInput("Fact Checker Ratio", value=0.05),
    "spread_probability": NumberInput("Spread Probability", value=0.05),
}

class ModelWrapper:
    def __init__(self, model_type, *args, **kwargs):
        custom_network = kwargs.pop('custom_network', None)
        
        if model_type == "Rumor Spread":
            # Keep all relevant parameters for RumorSpreadModel
            rumor_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["num_agents", "avg_node_degree", "initial_outbreak_size",
                        "prob_infect", "prob_accept_deny", "prob_make_denier"]
            }
            # Ensure avg_node_degree is passed (it's missing in your current code)
            if 'avg_node_degree' not in rumor_kwargs:
                rumor_kwargs['avg_node_degree'] = 5  # or some default
            self.model = RumorSpreadModel(**rumor_kwargs, custom_network=custom_network)
        else:
            # Keep all relevant parameters for MisinformationModel
            misinfo_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["num_agents", "m_links", "exposure_threshold", 
                        "fact_checker_ratio", "spread_probability"]
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