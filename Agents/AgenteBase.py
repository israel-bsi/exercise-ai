from mesa import Agent

class AgentBase(Agent):
    def __init__(self, unique_id, model, name="Agent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None
        self.points = 0
        self.target_resource = None
        self.path = []
        self.type = "Agent"
        self.shape = "circle"
        self.layer = 1
        self.known_resources = {}
        self.partner = None

    def step(self):
        pass  # Implementação específica nas subclasses
