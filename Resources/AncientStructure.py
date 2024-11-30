from Resources import ResourceBase

class AncientStructure(ResourceBase):
    def __init__(self, unique_id, model, name="AncientStructure"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = 50
        self.required_agents = 2
        self.color = "gold"