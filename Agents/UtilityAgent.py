from Agents import *

class UtilityAgent(AgentBase):
    def __init__(self, unique_id, model, name="UtilityAgent"):
        super().__init__(unique_id, model)
        self.color = "red"
        self.name = name

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        if self.waiting:
            return

        self.visited_positions.add(self.pos)

        if self.carrying:
            self.move_towards(self.model.base.pos)
            if self.pos == self.model.base.pos:
                self.deliver_resource()
            return
        if self.known_resources and not self.carrying:
            self.move_towards(self.known_resources[0].pos)
            if self.pos == self.known_resources[0].pos:
                self.collect_any_resource()
            return

        self.random_move_to_unvisited_position()
        self.collect_any_resource()
        self.check_resources()