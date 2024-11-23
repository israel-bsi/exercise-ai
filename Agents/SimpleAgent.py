from Demos.SystemParametersInfo import new_x
from mesa import Agent
from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure

class SimpleAgent(Agent):
    def __init__(self, unique_id, model, name="SimpleAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None
        self.points = 0
        self.type = "Agent"
        self.color = "blue"
        self.shape = "circle"
        self.layer = 1
        self.known_resources = {}

    def step(self):
        if self.carrying is not None:
            self.move_towards(self.model.base.position)
            if self.pos == self.model.base.position:
                self.deliver_resource()
        else:
            self.random_move()
            self.collect_resource()

        # Detectar recursos próximos
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                self.known_resources[self.pos] = obj
                print(f"{self.name} detectou {obj.type} em {self.pos}.")

    def random_move(self):
        x, y = self.pos

        possible_moves = [
            (x, y - 1),  # Cima
            (x, y + 1),  # Baixo
            (x - 1, y),  # Esquerda
            (x + 1, y)   # Direita
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

    def collect_resource(self):
        if self.carrying is None:
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            resources = [obj for obj in cell_contents if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried]
            for resource in resources:
                if resource.required_agents == 1:
                    resource.carried = True
                    self.carrying = resource
                    print(f"{self.name} coletou {resource.name}.")
                    self.model.grid.remove_agent(resource)
                    break
                elif resource.required_agents == 2:
                    agents_in_cell = [obj for obj in cell_contents if isinstance(obj, SimpleAgent) and obj != self]
                    if agents_in_cell:
                        resource.carried = True
                        self.carrying = resource
                        other_agent = agents_in_cell[0]
                        other_agent.carrying = resource
                        print(f"{self.name} e {other_agent.name} coletaram {resource.name}.")
                        self.model.grid.remove_agent(resource)
                        break

    def deliver_resource(self):
        # Entrega o recurso na base
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.type} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None  # Libera o agente para coletar outro recurso
        self.model.num_resources_delivered += 1
