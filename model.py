from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
import networkx as nx
from agent import SocialAgent

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
        self.beacons = set(agent for agent, _ in sorted_agents[:beacon_count])

        for i in range(self.num_agents):
            if i in self.beacons:
                state = "Resistant"
            else:
                state = "Susceptible"
            a = SocialAgent(i, self, initial_state=state)
            self.schedule.add(a)

        # Infect a few random non-beacon agents
        non_beacons = [i for i in range(self.num_agents) if i not in self.beacons]
        initial_infected = self.random.sample(non_beacons, 10)
        for idx in initial_infected:
            self.schedule.agents[idx].state = "Infected"

    def step(self):
        print(f"Model step: {self.schedule.time}")
        self.datacollector.collect(self)
        self.schedule.step()

    def count_state(self, state):
        return sum(1 for a in self.schedule.agents if a.state == state)
