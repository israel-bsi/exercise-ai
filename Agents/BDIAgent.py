from Agents import AgentBase

class BDIAgent(AgentBase):
    def __init__(self, unique_id, model, name="BDIAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.beliefs = []  #Lista com os recursos informados por outros agentes
        self.desires = [] #Lista com os recursos que deseja coletar
        self.color = "purple"

    def step(self):
        for resource in self.beliefs:
            if resource.pos is None:
                self.beliefs.remove(resource)

        if self.waiting:
            return

        self.update_desires()
        self.execute_intention()

        self.visited_positions.add(self.pos)

        if self.carrying:
            self.move_towards(self.model.base.pos)
            if self.pos == self.model.base.pos:
                self.deliver_resource()
            return
        if self.desires and not self.carrying:
            # print(f"{self.name} conhece {len(self.desires)} recursos.")
            # print(f"{self.name} está se movendo em direção ao recurso {self.desires[0].name}.")
            # print(f"{self.name} está na posição {self.pos}.")
            self.move_towards(self.desires[0].pos)
            if self.pos == self.desires[0].pos:
                self.collect_any_resource()
            return

        self.random_move_to_unvisited_position()
        self.collect_any_resource()
        self.check_resources()

    def update_desires(self):
        """Atualiza a lista de desejos com os recursos que deseja coletar."""
        for resource in self.beliefs:
            if resource is not None and resource.carried == False and resource.required_agents == 2:
                if resource not in self.desires:
                    self.desires.append(resource)

    def execute_intention(self):
        """Executa a intenção de coletar um recurso."""
        if self.desires:
            for resource in self.desires:
                self.move_towards(resource.pos) # Erro aqui NoneType
                if resource.pos == self.pos:
                    self.waiting = True
                    self.collect_any_resource()
                    self.desires.remove(resource)
                    self.waiting = False
                    return