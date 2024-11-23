from mesa import Agent

class Base(Agent):
    def __init__(self, unique_id, model, position, name="Base"):
        super().__init__(unique_id, model)
        self.name = name
        self.position = position
        self.type = "Base"
        self.color = "brown"
        self.shape = "rect"
        self.layer = 0

    def step(self):
        pass
