from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
from mesa.datacollection import DataCollector
import networkx as nx
from agent import RumorAgent, SocialAgent

class RumorSpreadModel(Model):
    def __init__(self, 
                 num_agents=1000, 
                 avg_node_degree=5, 
                 initial_outbreak_size=50, 
                 prob_infect=0.3,
                 prob_accept_deny=0.2,
                 prob_make_denier=0.1):
        super().__init__()
        self.num_agents = num_agents
        self.avg_node_degree = avg_node_degree
        self.initial_outbreak_size = initial_outbreak_size
        self.prob_infect = prob_infect
        self.prob_accept_deny = prob_accept_deny
        self.prob_make_denier = prob_make_denier
        
        self.network = nx.barabasi_albert_graph(n=num_agents, m=avg_node_degree//2)
        self.G = self.network 
        
        self.schedule = RandomActivation(self)
        self.agents = {} 
        
        for i in range(self.num_agents):
            agent = RumorAgent(i, self)
            self.agents[i] = agent
            self.schedule.add(agent)
            self.network.nodes[i]["agent"] = agent  
        
        initially_infected = self.random.sample(list(range(num_agents)), initial_outbreak_size)
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
    def __init__(self, num_agents=1000, m_links=4, exposure_threshold=2, fact_checker_ratio=0.02, spread_probability=0.6):
        super().__init__()
        self.num_agents = num_agents
        self.exposure_threshold = exposure_threshold
        self.spread_probability = spread_probability
        self.graph = nx.barabasi_albert_graph(num_agents, m_links)
        self.G = self.graph 
        self.schedule = BaseScheduler(self)
        self.running = True
        self.beacons = set()
        self._create_agents(fact_checker_ratio)
        for i, agent in enumerate(self.schedule.agents):
            self.graph.nodes[i]["agent"] = agent
        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: self.count_state("Susceptible"),
                "Exposed": lambda m: self.count_state("Exposed"),
                "Infected": lambda m: self.count_state("Infected"),
                "Resistant": lambda m: self.count_state("Resistant")
            }
        )
    
    def _create_agents(self, fact_checker_ratio):
        degrees = dict(self.graph.degree())
        sorted_agents = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        beacon_count = int(self.num_agents * fact_checker_ratio)
        self.beacons = set(agent for agent, degree in sorted_agents[:beacon_count])
        
        for i in range(self.num_agents):
            if i in self.beacons:
                state = "Resistant"
            else:
                state = "Susceptible"
            a = SocialAgent(i, self, initial_state=state)
            self.schedule.add(a)
            self.graph.nodes[i]["agent"] = a  
        
        # Infect a few random non-beacon agents
        non_beacons = [i for i in range(self.num_agents) if i not in self.beacons]
        initial_infected = self.random.sample(non_beacons, 10)
        for idx in initial_infected:
            self.schedule.agents[idx].state = "Infected"
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
    
    def count_state(self, state):
        return sum(1 for a in self.schedule.agents if a.state == state)