from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from model import MisinformationModel
import networkx as nx

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

        if agent.state == "Infected":
            portrayal["color"] = "red"
        elif agent.state == "Exposed":
            portrayal["color"] = "orange"
        elif agent.state == "Resistant":
            portrayal["color"] = "blue"

        nodes.append(portrayal)

    for source, target in G.edges():
        edges.append({"source": source, "target": target, "color": "lightgray"})


    return {"nodes": nodes, "edges": edges}




def get_network(model):
    portrayal = model.graph.copy()
    for node in portrayal.nodes:
        portrayal.nodes[node]["agent"] = model.schedule.agents[node]
    return portrayal

network = NetworkModule(network_portrayal, 500, 864)

chart = ChartModule([
    {"Label": "Susceptible", "Color": "gray"},
    {"Label": "Exposed", "Color": "orange"},
    {"Label": "Infected", "Color": "red"},
    {"Label": "Resistant", "Color": "blue"},
])

server = ModularServer(
    MisinformationModel,
    [network, chart],
    "Misinformation Contagion Model",
    {
        "num_agents": 1000,
        "exposure_threshold": UserSettableParameter("slider", "Exposure Threshold", 2, 1, 10, 1),
        "fact_checker_ratio": UserSettableParameter("slider", "Fact Checker Ratio", 0.02, 0.0, 0.5, 0.01),
        "spread_probability": UserSettableParameter("slider", "Spread Probability", 0.6, 0.0, 1.0, 0.05),
        "m_links": 4
    }
)

server.port = 8521
