from Agents import AgentBase

class BDIAgent(AgentBase):
    def __init__(self, unique_id, model, name="BDIAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.beliefs = []  #Lista com os recursos informados por outros agentes
        self.desires = [] #Lista com os recursos que deseja coletar
        self.intentions = []  # Lista de passos para coletar recursos desejados
        self.color = "purple"

    def step(self):
        for resource in self.beliefs:
            if resource.pos is None:
                self.beliefs.remove(resource)
            print(f"Tipo: {resource.name} Posicao: {resource.pos}")

        if self.waiting:
            return

        self.visited_positions.add(self.pos)

        if self.carrying:
            self.move_towards(self.model.base.pos)
            if self.pos == self.model.base.pos:
                self.deliver_resource()
            return
        if self.known_resources and not self.carrying:
            # print(f"{self.name} conhece {len(self.known_resources)} recursos.")
            # print(f"{self.name} está se movendo em direção ao recurso {self.known_resources[0].name}.")
            # print(f"{self.name} está na posição {self.pos}.")
            self.move_towards(self.known_resources[0].pos)
            if self.pos == self.known_resources[0].pos:
                self.collect_any_resource()
            return

        self.random_move_to_unvisited_position()
        self.collect_any_resource()
        self.check_resources()