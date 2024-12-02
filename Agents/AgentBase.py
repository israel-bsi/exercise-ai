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
        self.known_resources = []
        self.partner = None
        self.visited_positions = set()

    def step(self):
        pass

    def move_towards(self, destination):
        """Move-se em direção a uma posição específica."""
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

    def random_move_to_unvisited_position(self):
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

    def check_resources(self):
        """Verifica se há recursos na vizinhança e informa ao agente BDI"""
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

    def collect_any_resource(self):
        """Coleta qualquer tipo de recurso na célula atual se todos os agentes necessários estiverem presentes."""
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
                print(f"{self.name} está esperando por mais um agente para coletar {resource.name} em {resource.pos}.")

    def collect_simple_resource(self):
        """Coleta um recurso simples na célula atual."""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        resources = [obj for obj in cell_contents if isinstance(obj, EnergeticCrystal) and not obj.carried]
        for resource in resources:
            resource.carried = True
            self.carrying = resource
            print(f"{self.name} coletou {resource.name}.")
            self.model.grid.remove_agent(resource)
            break

    def deliver_resource(self):
        """Entrega o recurso na base"""
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {self.carrying.value} pontos.")
        if self.carrying in self.known_resources:
            self.known_resources.remove(self.carrying)
        if self.carrying.required_agents == 2:
            self.model.num_resources_delivered += 0.5
        else:
            self.model.num_resources_delivered += 1
        self.carrying = None