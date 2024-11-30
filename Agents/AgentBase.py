from mesa import Agent
from Resources import *

class AgentBase(Agent):
    def __init__(self, unique_id, model, name="Agent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None
        self.points = 0
        self.type = "Agent"
        self.shape = "circle"
        self.layer = 1
        self.waiting = False
        self.target_resource = None
        self.path = []
        self.known_resources = []
        self.partner = None

    def step(self):
        pass

    def random_move(self):
        x, y = self.pos

        possible_moves = [
            (x, y - 1),
            (x, y + 1),
            (x - 1, y),
            (x + 1, y)
        ]

        valid_moves = []
        for move in possible_moves:
            new_x, new_y = move
            if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
                valid_moves.append(move)

        if valid_moves:
            new_position = self.random.choice(valid_moves)
            self.model.grid.move_agent(self, new_position)

    def move_towards(self, destination):
        current_x, current_y, = self.pos
        dest_x, dest_y = destination

        # Calcula a direção do movimento
        dx = dest_x - current_x
        dy = dest_y - current_y

        # Determina o próximo passo em x
        if dx > 0:
            new_x = current_x + 1
        elif dx < 0:
            new_x = current_x - 1
        else:
            new_x = current_x

        # Determina o próximo passo em y
        if dy > 0:
            new_y = current_y + 1
        elif dy < 0:
            new_y = current_y - 1
        else:
            new_y = current_y

        # Verifica se a nova posição está dentro dos limites do grid
        if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
            new_position = (new_x, new_y)
            self.model.grid.move_agent(self, new_position)

    def check_resources(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )

        neighbors_contents = self.model.grid.get_cell_list_contents(neighbors)
        for obj in neighbors_contents:
            if isinstance(obj, ResourceBase) and not obj.carried:
                self.inform_resource_to_bdi(obj)
                if obj not in self.known_resources:
                    self.known_resources.append(obj)

    def inform_resource_to_bdi(self, resource):
        """Informa ao agente BDI a localização de um recurso que foi visto"""
        for agent in self.model.bdi_agents:
            if resource not in agent.beliefs:
                agent.beliefs.append(resource)

    def deliver_resource(self):
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None
        self.model.num_resources_delivered += 1