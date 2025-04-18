from mesa.visualization.modules import NetworkModule, ChartModule, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice, NumberInput
from model import RumorSpreadModel, MisinformationModel

# Create a NetworkInfo visualization element to display custom network details
class NetworkInfoElement(TextElement):
    def __init__(self):
        super().__init__()
        
    def render(self, model):
        if hasattr(model, "G") and model.G is not None:
            network_name = getattr(model, "network_name", "Custom Network")
            nodes = model.G.number_of_nodes()
            edges = model.G.number_of_edges()
            return f"<b>{network_name}</b>: {nodes} nodes, {edges} edges"
        return "Network information not available"

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
        if "INFECTED" in agent.state or "Infected" in agent.state:
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

# Create visualization elements
network_info = NetworkInfoElement()
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

# Merged common parameters and model-specific parameters
model_params = {
    "model_type": Choice(
        "Model Type", 
        value="Rumor Spread",
        choices=["Rumor Spread", "Misinformation"]
    ),
    # Common parameters
    "initial_outbreak_size": NumberInput("Initially Infected", value=5),
    "prob_infect": NumberInput("Infection Probability", value=0.05),
    "prob_make_denier": NumberInput("Probability of Creating Deniers", value=0.02),
    "prob_accept_deny": NumberInput("Probability of Accepting Denial", value=0.05),
    # Misinformation model specific parameter
    "exposure_threshold": NumberInput("Exposure Threshold (Misinformation Model Only)", value=2),
}

class ModelWrapper:
    def __init__(self, model_type, *args, **kwargs):
        custom_network = kwargs.pop('custom_network', None)
        self.network_name = kwargs.pop('network_name', "Custom Network") if custom_network else "Generated Network"
        
        # Set common parameters for both models
        common_params = {
            "initial_outbreak_size": kwargs.get("initial_outbreak_size", 5),
            "prob_infect": kwargs.get("prob_infect", 0.05),
            "prob_make_denier": kwargs.get("prob_make_denier", 0.02),
            "prob_accept_deny": kwargs.get("prob_accept_deny", 0.05),
        }
        
        if model_type == "Rumor Spread":
            # Parameters for RumorSpreadModel
            rumor_kwargs = {
                "num_agents": kwargs.get("num_agents", 1000),
                "avg_node_degree": kwargs.get("avg_node_degree", 5),
                **common_params
            }
            self.model = RumorSpreadModel(**rumor_kwargs, custom_network=custom_network)
        else:
            # Parameters for MisinformationModel
            misinfo_kwargs = {
                "num_agents": kwargs.get("num_agents", 1000),
                "avg_node_degree": kwargs.get("avg_node_degree", 4),
                "exposure_threshold": kwargs.get("exposure_threshold", 2),
                **common_params
            }
            self.model = MisinformationModel(**misinfo_kwargs, custom_network=custom_network)
        
        # Pass the network name to the model for display
        self.model.network_name = self.network_name
    
    def step(self):
        self.model.step()
    
    def __getattr__(self, name):
        # Delegate unknown attributes to the underlying model
        return getattr(self.model, name)

server = ModularServer(
    ModelWrapper,
    [network_info, network, rumor_chart, misinfo_chart],
    "Contagion Model Comparison",
    model_params
)

server.port = 8521