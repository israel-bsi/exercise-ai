from mesa import Agent

class ResourceBase(Agent):
    def __init__(self, unique_id, model, name="Resource"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = None
        self.carried = False
        self.type = "Resource"
        self.shape = "rect"
        self.layer = 0
        self.color = None
        self.required_agents = 1