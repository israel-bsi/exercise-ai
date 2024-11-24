from Agents.AgenteBase import AgentBase
from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure

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

        # Detectar recursos próximos
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                self.known_resources[self.pos] = obj
                #print(f"{self.name} detectou {obj.type} em {self.pos}.")

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

    def deliver_resource(self):
        # Entrega o recurso na base
        if self.carrying.required_agents == 2:
            points = self.carrying.value / 2
        else:
            points = self.carrying.value
        self.points += points
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {points} pontos.")
        self.carrying = None  # Libera o agente para coletar outro recurso
        self.partner.carrying = None # Libera o parceiro para coletar outro recurso
        self.model.num_resources_delivered += 1
