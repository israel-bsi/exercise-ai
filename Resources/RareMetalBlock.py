from Resources import ResourceBase

class RareMetalBlock(ResourceBase):
    def __init__(self, unique_id, model, name = "RareMetalBlock"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = 20
        self.required_agents = 1
        self.color = "silver"