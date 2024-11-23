from mesa import Agent

class RareMetalBlock(Agent):
    def __init__(self, unique_id, model, name = "RareMetalBlock"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = 20
        self.type = "Resource"
        self.carried = False
        self.required_agents = 1
        self.color = "silver"
        self.shape = "rect"
        self.layer = 0
        self.collected = False