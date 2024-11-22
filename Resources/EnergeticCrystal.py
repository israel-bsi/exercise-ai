from mesa import Agent

class EnergeticCrystal(Agent):
    def __init__(self, unique_id, model, name="EnergeticCrystal"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = 10
        self.carried = False
        self.type = "Resource"
        self.required_agents = 1
        self.color = "cyan"
        self.shape = "rect"
        self.layer = 0
        self.collected = False