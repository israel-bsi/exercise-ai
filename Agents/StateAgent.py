from Resources import *
from Agents import *

class StateAgent(AgentBase):
    def __init__(self, unique_id, model, name="StateAgent"):
        super().__init__(unique_id, model)
        self.color = "green"
        self.name = name
        self.visited_positions = set()

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        if self.waiting:
            return

        # Memorizar a posição atual
        self.visited_positions.add(self.pos)

        if self.carrying:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_towards(self.model.base.pos)
            if self.pos == self.model.base.pos:
                self.deliver_resource()
        elif self.known_resources and (not self.carrying):
            print(f"{self.name} conhece {len(self.known_resources)} recursos.")
            # Se houver recursos conhecidos, mover-se em direção ao recurso mais próximo
            self.move_towards(self.known_resources[0].pos)
            if self.pos == self.known_resources[0].pos:
                self.collect_resource()
        else:
            # Procurar por recursos ou explorar
            self.random_move()
            self.collect_resource()

        self.check_resources()

    def random_move(self):
        """Move-se para uma célula aleatória não visitada. Se não houver, move-se para qualquer célula adjacente válida."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        unvisited_steps = [
            pos for pos in possible_steps
            if pos not in self.visited_positions and
               0 <= pos[0] < self.model.grid.width and
               0 <= pos[1] < self.model.grid.height
        ]

        if unvisited_steps:
            new_position = self.random.choice(unvisited_steps)
            self.model.grid.move_agent(self, new_position)
            self.visited_positions.add(new_position)
        else:
            valid_steps = [
                pos for pos in possible_steps
                if 0 <= pos[0] < self.model.grid.width and
                   0 <= pos[1] < self.model.grid.height
            ]

            if valid_steps:
                new_position = self.random.choice(valid_steps)
                self.model.grid.move_agent(self, new_position)

    def collect_resource(self):
        """Coleta o recurso na célula atual se todos os agentes necessários estiverem presentes."""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        resources = [obj for obj in cell_contents if isinstance(obj, ResourceBase) and not obj.carried]
        if len(resources) == 0:
            return
        agents = [obj for obj in cell_contents if isinstance(obj, AgentBase) and not obj.carrying]

        for resource in resources:
            if len(agents) >= resource.required_agents:
                self.known_resources.remove(resource)
                self.carrying = resource
                resource.carried = True
                self.model.grid.remove_agent(resource)
                if resource.required_agents == 2:
                    self.waiting = False
                    print(f"{self.name} e {agents[0].name} coletaram {resource.name}.")
                    agents[0].carrying = resource
                    agents[0].partner = self
                    agents[0].waiting = False
                    self.partner = agents[0]
                else:
                    print(f"{self.name} coletou {resource.name}.")
                break
            else:
                self.waiting = True

    def deliver_resource(self):
        """Entrega o recurso na base"""
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None
        self.model.num_resources_delivered += 1