from Resources import ResourceBase

class EnergeticCrystal(ResourceBase):
    def __init__(self, unique_id, model, name="EnergeticCrystal"):
        super().__init__(unique_id, model)
        self.name = name
        self.value = 10
        self.required_agents = 1
        self.color = "cyan"