import networkx as nx
import matplotlib.pyplot as plt
import random
import json
import logging
import os
from enum import Enum
import time
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BigTweet')

os.makedirs('configuration', exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "numusers": 5000,
    "initialspreadmodel": "M2",
    "modelConfPath": "./configuration/model_config.json"
}

DEFAULT_MODEL_CONFIG = {
    "spreadModels": {
        "M1": {
            "selectedSetOfParametersValues": "default",
            "setsOfParametersValues": {
                "default": {
                    "users": 5000,
                    "maxLinkPerNode": 1,
                    "initiallyInfected": 500,
                    "probInfect": 0.5,
                    "timeLag": 10,
                    "probAcceptDeny": 0.3,
                    "beacons": 3
                }
            }
        },
        "M2": {
            "selectedSetOfParametersValues": "default",
            "setsOfParametersValues": {
                "default": {
                    "users": 5000,
                    "maxLinkPerNode": 1,
                    "initiallyInfected": 500,
                    "probInfect": 0.5,
                    "timeLag": 10,
                    "probAcceptDeny": 0.3,
                    "beacons": 3,
                    "probMakeDenier": 0.2,
                    "selectionMethodForInfectedAndBeaconsM2": "first"
                }
            }
        },
        "M3": {
            "selectedSetOfParametersValues": "default",
            "setsOfParametersValues": {
                "default": {
                    "users": 5000,
                    "maxLinkPerNode": 1,
                    "initiallyInfected": 500,
                    "probInfect": 0.5,
                    "timeLag": 10,
                    "probAcceptDeny": 0.3,
                    "beacons": 3
                }
            }
        }
    }
}

def create_default_configs():
    config_path = "./configuration/config.properties"
    model_config_path = "./configuration/model_config.json"
    
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            for key, value in DEFAULT_CONFIG.items():
                f.write(f"{key}={value}\n")
        logger.info(f"Created default configuration at {config_path}")
    
    if not os.path.exists(model_config_path):
        with open(model_config_path, 'w') as f:
            json.dump(DEFAULT_MODEL_CONFIG, f, indent=2)
        logger.info(f"Created default model configuration at {model_config_path}")

def get_property(key):
    config_path = "./configuration/config.properties"
    if not os.path.exists(config_path):
        create_default_configs()
        return str(DEFAULT_CONFIG.get(key, ""))
    
    with open(config_path, 'r') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                if k == key:
                    return v
    return str(DEFAULT_CONFIG.get(key, ""))

class StateM1(Enum):
    INFECTED = "INFECTED"
    NEUTRAL = "NEUTRAL"
    VACCINATED = "VACCINATED"
    CURED = "CURED"
    BEACONON = "BEACONON"
    BEACONOFF = "BEACONOFF"
    ENDORSER = "ENDORSER"
    DENIER = "DENIER"

class SimState:
    def __init__(self, seed=None):
        if seed is None:
            seed = int(time.time())
        self.seed = seed
        random.seed(seed)
        self.step_count = 0
        self.network_seed = seed
        self.results_log = {"steps": []}
    
    def step(self):
        self.step_count += 1
        return self.step_count

class UserAgent(ABC):
    def __init__(self, agent_id, model):
        self.id = agent_id
        self.name = f"agent_{agent_id}"
        self.model = model
        self.state = StateM1.NEUTRAL.value
        self.neighbors = []
        logger.debug(f"Created agent {self.name}")
    
    def get_name(self):
        return self.name
    
    def get_state(self):
        return self.state
    
    def set_state(self, state):
        previous_state = self.state
        self.state = state
        self.model.record_agent_state_change(previous_state, state)
        logger.debug(f"Agent {self.name} changed state from {previous_state} to {state}")
    
    @abstractmethod
    def step(self):
        pass

class UserAgentM1(UserAgent):
    def __init__(self, agent_id, model):
        super().__init__(agent_id, model)
        self.time_infected = -1
    
    def step(self):
        if self.state == StateM1.INFECTED.value:
            if self.model.sim.step_count - self.time_infected == 1:
                for neighbor_id in self.neighbors:
                    neighbor = self.model.sim.get_agent(f"agent_{neighbor_id}")
                    if neighbor and neighbor.get_state() == StateM1.NEUTRAL.value:
                        if random.random() < self.model.prob_infect:
                            neighbor.set_state(StateM1.INFECTED.value)
                            neighbor.time_infected = self.model.sim.step_count
                
                self.set_state(StateM1.CURED.value)
            
        elif self.state == StateM1.BEACONOFF.value:
            if self.model.sim.step_count >= self.model.time_lag:
                self.set_state(StateM1.BEACONON.value)
                
        elif self.state == StateM1.BEACONON.value:
            for neighbor_id in self.neighbors:
                neighbor = self.model.sim.get_agent(f"agent_{neighbor_id}")
                if neighbor and neighbor.get_state() == StateM1.NEUTRAL.value:
                    if random.random() < self.model.prob_accept_deny:
                        neighbor.set_state(StateM1.VACCINATED.value)

class UserAgentM2(UserAgentM1):
    def step(self):
        super().step()
        
        if self.state == StateM1.NEUTRAL.value:
            for neighbor_id in self.neighbors:
                neighbor = self.model.sim.get_agent(f"agent_{neighbor_id}")
                if neighbor and neighbor.get_state() == StateM1.INFECTED.value:
                    if random.random() < self.model.prob_make_denier:
                        self.set_state(StateM1.VACCINATED.value)
                        break

class MonitorAgent:
    def __init__(self, sim):
        self.sim = sim
        self.model = sim.get_spread_model()
        logger.info("Monitor agent initialized")
    
    def step(self):
        agents_per_state = self.model.get_agents_per_state()
        step_data = {
            "step": self.sim.step_count,
            "states": agents_per_state
        }
        self.sim.results_log["steps"].append(step_data)
        
        self.display_status()
        
        if self.sim.step_count % 5 == 0 or self.sim.step_count == 1:
            self.save_results()
    
    def display_status(self):
        states = self.model.get_agents_per_state()
        logger.info(f"Step {self.sim.step_count} - States: {states}")
        
        
    def save_results(self):
        filename = f"./results/simulation_{int(time.time())}.json"
        os.makedirs('./results', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(self.sim.results_log, f, indent=2)
        
        logger.info(f"Results saved to {filename}")

class SpreadModel(ABC):
    def __init__(self, sim):
        self.sim = sim
        self.graph = None
        self.agents_per_state = {}
        self.last_step_stored = 0
        self.last_states_stored = {}
        self.parameters_set_for_batch = None
    
    def get_name(self):
        return self.sim.get_spread_model_name()
    
    @abstractmethod
    def load_model(self):
        pass
    
    @abstractmethod
    def create_agent(self, agent_id, model):
        pass
    
    def generate_users(self):
        for i in range(self.sim.num_users):
            agent = self.create_agent(i, self)
            self.sim.agents.append(agent)
            
            if i in self.graph.nodes():
                neighbors = list(self.graph.neighbors(i))
                agent.neighbors = neighbors
    
    def get_agents_per_state(self):
        return self.agents_per_state
    
    def get_agents_with_state(self, state):
        return self.agents_per_state.get(state, 0)
    
    def record_agent_state_change(self, previous_state, current_state):
        step = self.sim.step_count
        
        if step > self.last_step_stored:
            self.last_step_stored = step
            self.last_states_stored = self.agents_per_state.copy()
        
        if previous_state is None and current_state is None:
            return
        
        if previous_state is not None and previous_state in self.agents_per_state:
            self.agents_per_state[previous_state] = self.agents_per_state[previous_state] - 1
        
        if current_state not in self.agents_per_state:
            self.agents_per_state[current_state] = 0
        self.agents_per_state[current_state] = self.agents_per_state[current_state] + 1
    
    def load_parameters(self):
        model_config = self.get_model_configuration()
        spread_models = model_config.get("spreadModels", {})
        model_name = self.get_name()
        
        if model_name in spread_models:
            model_config = spread_models[model_name]
            parameters_set_name = model_config.get("selectedSetOfParametersValues", "default")
            parameters = model_config.get("setsOfParametersValues", {}).get(parameters_set_name, {})
            
            if self.parameters_set_for_batch:
                parameters.update(self.parameters_set_for_batch)
            
            return parameters
        
        return {}
    
    def get_model_configuration(self):
        model_conf_path = get_property("modelConfPath")
        
        if not os.path.exists(model_conf_path):
            create_default_configs()
            return DEFAULT_MODEL_CONFIG
        
        with open(model_conf_path, 'r') as f:
            return json.load(f)

class SpreadModelM1(SpreadModel):
    def __init__(self, sim):
        super().__init__(sim)
        self.initially_infected = 5
        self.prob_infect = 0.5
        self.time_lag = 10
        self.prob_accept_deny = 0.3
        self.beacons = 0
        self.beacon_links_number = 0
        self.beacon_links_centrality = None
    
    def load_model(self):
        self.load_parameters()
        
        self.graph = self.generate_graph(
            self.sim.network_seed,
            self.sim.max_link_per_node,
            self.sim.num_users
        )
        
        self.generate_users()
        
        self.infect_initial_nodes(
            self.sim.get_n_random_users(self.initially_infected, None)
        )
        
        self.make_beacons_nodes(
            self.sim.get_n_random_users(self.beacons, StateM1.INFECTED.value),
            False
        )
        
        self.monitor = MonitorAgent(self.sim)
        self.sim.monitor = self.monitor
    
    def create_agent(self, agent_id, model):
        return UserAgentM1(agent_id, model)
    
    def generate_graph(self, seed, m, n):
        random.seed(seed)
        G = nx.barabasi_albert_graph(n, m, seed=seed)
        return G
    
    def infect_initial_nodes(self, agents_to_infect):
        logger.info(f"Agents initially infected: {[a.get_name() for a in agents_to_infect]}")
        for agent in agents_to_infect:
            agent.set_state(StateM1.INFECTED.value)
            agent.time_infected = 0
    
    def make_beacons_nodes(self, agents_beacons, on):
        for agent in agents_beacons:
            if on:
                agent.set_state(StateM1.BEACONON.value)
            else:
                agent.set_state(StateM1.BEACONOFF.value)
    
    def load_parameters(self):
        parameters = super().load_parameters()
        
        self.initially_infected = int(parameters.get("initiallyInfected", 5))
        self.prob_infect = float(parameters.get("probInfect", 0.5))
        self.time_lag = int(parameters.get("timeLag", 10))
        self.prob_accept_deny = float(parameters.get("probAcceptDeny", 0.3))
        self.beacons = int(parameters.get("beacons", 0))
        
        if "beaconLinksNumber" in parameters:
            self.beacon_links_number = int(parameters.get("beaconLinksNumber"))
        
        if "beaconLinksCentrality" in parameters:
            self.beacon_links_centrality = parameters.get("beaconLinksCentrality")

class SpreadModelM2(SpreadModelM1):
    def __init__(self, sim):
        super().__init__(sim)
        self.prob_make_denier = 0.2
    
    def create_agent(self, agent_id, model):
        return UserAgentM2(agent_id, model)
    
    def load_model(self):
        self.load_parameters()
        
        self.graph = self.generate_graph(
            self.sim.network_seed,
            self.sim.max_link_per_node,
            self.sim.num_users
        )
        
        self.generate_users()
        
        selection_method = get_property("selectionMethodForInfectedAndBeaconsM2")
        
        self.infect_initial_nodes(
            self.sim.get_n_users(self.initially_infected, selection_method, None)
        )
        
        self.make_beacons_nodes(
            self.sim.get_n_users(self.beacons, selection_method, StateM1.INFECTED.value),
            False
        )
        
        self.monitor = MonitorAgent(self.sim)
        self.sim.monitor = self.monitor
    
    def load_parameters(self):
        super().load_parameters()
        parameters = super().load_parameters()
        
        self.prob_make_denier = float(parameters.get("probMakeDenier", 0.2))

class BTSim:
    def __init__(self, seed=None):
        self.sim_state = SimState(seed)
        self.seed = self.sim_state.seed
        self.network_seed = self.sim_state.network_seed
        self.num_users = int(get_property("numusers"))
        self.max_link_per_node = 1
        self.spread_model_name = get_property("initialspreadmodel")
        self.agents = []
        self.monitor = None
        self.step_count = 0
        self.parameters_set_for_batch = None
        self.random = random
        self.results_log = {"steps": []}
        random.seed(self.seed)
        
        if self.spread_model_name == "M1":
            self.spread_model = SpreadModelM1(self)
        elif self.spread_model_name == "M2":
            self.spread_model = SpreadModelM2(self)
        else:
            logger.warning(f"Unknown model: {self.spread_model_name}, using M1")
            self.spread_model = SpreadModelM1(self)
    
    def get_spread_model(self):
        return self.spread_model
    
    def get_spread_model_name(self):
        return self.spread_model_name
    
    def start(self):
        logger.info(f"Starting simulation with {self.num_users} users")
        self.spread_model.load_model()
    
    def step(self):
        self.step_count = self.sim_state.step()
        
        for agent in self.agents:
            agent.step()
        
        if self.monitor:
            self.monitor.step()
    
    def run(self, steps):
        self.start()
        
        for _ in range(steps):
            self.step()
            
        logger.info(f"Simulation completed after {steps} steps")
        return self.sim_state.results_log
    
    def get_agent(self, name):
        for agent in self.agents:
            if agent.get_name() == name:
                return agent
        return None
    
    def get_n_random_users(self, n, except_state):
        if n == 0:
            return []
        
        result = []
        added = 0
        tries = 0
        
        while added < n and tries < n * 10:
            tries += 1
            agent = self.agents[random.randint(0, len(self.agents) - 1)]
            
            if (agent not in result and 
                (except_state is None or agent.get_state() != except_state)):
                result.append(agent)
                added += 1
        
        if added < n:
            raise RuntimeError(f"Could not find {n} agents to add")
            
        return result
    
    def get_n_users(self, n, selecting_method, except_state):
        if n == 0:
            return []
        
        result = []
        
        if selecting_method == "first":
            for agent in self.agents:
                if (except_state is None or agent.get_state() != except_state):
                    result.append(agent)
                    if len(result) == n:
                        break
                        
        elif selecting_method == "last":
            for agent in reversed(self.agents):
                if (except_state is None or agent.get_state() != except_state):
                    result.append(agent)
                    if len(result) == n:
                        break
        else:
            result = self.get_n_random_users(n, except_state)
            
        if len(result) < n:
            raise RuntimeError(f"Could not find {n} agents using method {selecting_method}")
            
        return result

def visualize_results(results):
    """Visualize the simulation results"""
    steps = [step_data["step"] for step_data in results["steps"]]
    
    if not steps:
        logger.warning("No results to visualize")
        return
    
    all_states = set()
    for step_data in results["steps"]:
        all_states.update(step_data["states"].keys())
    
    plt.figure(figsize=(10, 6))
    
    for state in all_states:
        values = [step_data["states"].get(state, 0) for step_data in results["steps"]]
        plt.plot(steps, values, label=state)
    
    plt.title("Information Spread Simulation")
    plt.xlabel("Time Step")
    plt.ylabel("Number of Agents")
    plt.legend()
    plt.grid(True)
    
    os.makedirs('./results', exist_ok=True)
    plt.savefig(f"./results/simulation_{int(time.time())}.png")
    
    plt.show()

def main():
    create_default_configs()
    
    sim = BTSim()
    
    results = sim.run(50)
    
    visualize_results(results)
    
    logger.info("Simulation complete")

if __name__ == "__main__":
    main()