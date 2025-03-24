from mesa import Agent

class SocialAgent(Agent):
    def __init__(self, unique_id, model, initial_state="Susceptible"):
        super().__init__(unique_id, model)
        self.state = initial_state
        self.exposure_count = 0

    def step(self):
        if self.state == "Infected":
            for neighbor in self.model.graph.neighbors(self.unique_id):
                other = self.model.schedule.agents[neighbor]
                if other.state == "Susceptible":
                    other.exposure_count += 1

        if self.state == "Susceptible" and self.exposure_count >= self.model.exposure_threshold:
            self.state = "Exposed"
        elif self.state == "Exposed" and self.exposure_count >= self.model.exposure_threshold:
            if self.random.random() < self.model.spread_probability:
                self.state = "Infected"

        # Beacon intervention
        if self.unique_id in self.model.beacons:
            for neighbor in self.model.graph.neighbors(self.unique_id):
                other = self.model.schedule.agents[neighbor]
                if other.state in ["Susceptible", "Exposed"]:
                    other.state = "Resistant"
