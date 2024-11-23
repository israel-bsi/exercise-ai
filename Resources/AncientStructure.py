from mesa import Agent

class AncientStructure(Agent):
    def __init__(self, unique_id, model, name="AncientStructure"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = 50
        self.carried = False
        self.type = "Resource"
        self.color = "gold"
        self.shape = "rect"
        self.layer = 0
        self.required_agents = 2
        self.collected = False