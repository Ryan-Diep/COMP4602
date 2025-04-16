from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
from mesa.datacollection import DataCollector
import networkx as nx
from agent import RumorAgent, SocialAgent

class RumorSpreadModel(Model):
    def __init__(self, 
                 num_agents=1000, 
                 avg_node_degree=5, 
                 initial_outbreak_size=7, 
                 prob_infect=0.02,
                 prob_accept_deny=0.00,
                 prob_make_denier=0.00,
                 custom_network=None):
        super().__init__()
        self.num_agents = num_agents
        self.avg_node_degree = avg_node_degree
        self.initial_outbreak_size = initial_outbreak_size
        self.prob_infect = prob_infect
        self.prob_accept_deny = prob_accept_deny
        self.prob_make_denier = prob_make_denier
        if custom_network is not None:
            self.network = custom_network
            self.num_agents = len(custom_network.nodes())
        else:
            self.network = nx.barabasi_albert_graph(n=num_agents, m=avg_node_degree//2)
        self.G = self.network 
        
        self.schedule = RandomActivation(self)
        self.agents = {} 
        for i in self.network.nodes():
            agent = RumorAgent(i, self)
            self.agents[i] = agent
            self.schedule.add(agent)
            self.network.nodes[i]["agent"] = agent 
        
        node_list = list(self.network.nodes())
        initially_infected = self.random.sample(node_list, min(int(initial_outbreak_size), len(node_list)))
        for agent_id in initially_infected:
            self.agents[agent_id].state = "INFECTED"
        
        self.datacollector = DataCollector(
            model_reporters={
                "Infected": lambda m: sum(1 for a in m.schedule.agents if a.state == "INFECTED"),
                "Neutral": lambda m: sum(1 for a in m.schedule.agents if a.state == "NEUTRAL"),
                "Vaccinated": lambda m: sum(1 for a in m.schedule.agents if a.state == "VACCINATED")
            }
        )
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

class MisinformationModel(Model):
    def __init__(self, 
                num_agents=1000, 
                avg_node_degree=4,
                exposure_threshold=2,
                initial_outbreak_size=5,
                prob_accept_deny=0.00,
                prob_make_denier=0.02, 
                prob_infect=0.02,
                custom_network=None):
        super().__init__()
        self.num_agents = num_agents
        self.exposure_threshold = exposure_threshold
        self.prob_infect = prob_infect
        self.prob_accept_deny = prob_accept_deny
        self.prob_make_denier = prob_make_denier
        self.initial_outbreak_size = initial_outbreak_size
        
        if custom_network is not None:
            self.graph = custom_network
            self.num_agents = len(custom_network.nodes())
        else:
            self.graph = nx.barabasi_albert_graph(num_agents, avg_node_degree)
        self.G = self.graph 
        self.schedule = RandomActivation(self)  # Changed to RandomActivation to match RumorModel
        self.running = True
        
        # Create agents
        self.agents = {}
        for i in self.graph.nodes():
            agent = SocialAgent(i, self)
            self.agents[i] = agent
            self.schedule.add(agent)
            self.graph.nodes[i]["agent"] = agent
        
        # Set initial deniers (resistant agents)
        node_list = list(self.graph.nodes())
        initial_denier_count = int(self.num_agents * self.prob_make_denier)
        initial_deniers = self.random.sample(node_list, min(initial_denier_count, len(node_list)))
        for agent_id in initial_deniers:
            self.agents[agent_id].state = "Resistant"
        
        # Set initial infected agents
        # First filter out nodes that are already deniers
        uninfected_nodes = [node for node in node_list if self.agents[node].state != "Resistant"]
        initially_infected = self.random.sample(uninfected_nodes, 
                                                min(int(initial_outbreak_size), len(uninfected_nodes)))
        for agent_id in initially_infected:
            self.agents[agent_id].state = "Infected"
        
        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: self.count_state("Susceptible"),
                "Exposed": lambda m: self.count_state("Exposed"),
                "Infected": lambda m: self.count_state("Infected"),
                "Resistant": lambda m: self.count_state("Resistant")
            }
        )
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
    
    def count_state(self, state):
        return sum(1 for a in self.schedule.agents if a.state == state)