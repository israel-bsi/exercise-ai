from Agents.AgentBase import AgentBase
from Resources import *

class SimpleAgent(AgentBase):
    def __init__(self, unique_id, model, name="SimpleAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.color = "blue"

    def step(self):
        if self.carrying is not None:
            self.move_towards(self.model.base.position)
            if self.pos == self.model.base.position:
                self.deliver_resource()
        else:
            self.random_move()
            self.collect_resource()

        self.check_resources()

    def collect_resource(self):
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        resources = [obj for obj in cell_contents if isinstance(obj, ResourceBase)
                     and not obj.carried and obj.required_agents == 1]
        for resource in resources:
            resource.carried = True
            self.carrying = resource
            print(f"{self.name} coletou {resource.name}.")
            self.model.grid.remove_agent(resource)
            break