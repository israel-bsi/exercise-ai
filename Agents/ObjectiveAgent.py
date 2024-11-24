from mesa import Agent
from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure
from collections import deque

class ObjectiveAgent(Agent):
    def __init__(self, unique_id, model, name="ObjectiveAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None
        self.points = 0
        self.known_resources = {}  # Dicionário de recursos conhecidos com suas posições
        self.path = []             # Lista de posições para o caminho planejado
        self.shape = "circle"
        self.color = "yellow"
        self.type = "Agent"
        self.layer = 1
        self.known_resources = {}

    def step(self):
        if self.carrying is not None:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_along_path(self.model.base.position)
            # Verificar se chegou à base para entregar o recurso
            if self.pos == self.model.base.position:
                self.deliver_resource()
        else:
            if not self.path:
                # Se não tem um caminho planejado, planejar um
                if self.known_resources:
                    # Se conhece recursos, planejar caminho até o mais próximo
                    resource_pos = self.find_nearest_resource()
                    if resource_pos:
                        self.path = self.plan_path(self.pos, resource_pos)
                    else:
                        # Se não encontrar um recurso, mover-se aleatoriamente e procurar
                        self.random_move_and_scan()
                else:
                    # Se não conhece recursos, mover-se aleatoriamente e procurar
                    self.random_move_and_scan()
            else:
                # Seguir o caminho planejado
                self.move_along_path()
                self.collect_resource()

        # Detectar recursos próximos
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                self.known_resources[self.pos] = obj
                #print(f"{self.name} detectou {obj.type} em {self.pos}.")

    def find_nearest_resource(self):
        # Encontra o recurso conhecido mais próximo
        min_distance = float('inf')
        nearest_resource_pos = None
        for pos in self.known_resources.keys():
            distance = self.manhattan_distance(self.pos, pos)
            if distance < min_distance:
                min_distance = distance
                nearest_resource_pos = pos
        return nearest_resource_pos

    def plan_path(self, start_pos, goal_pos):
        grid_width = self.model.grid.width
        grid_height = self.model.grid.height
        visited = set()
        queue = deque()
        came_from = {}

        queue.append(start_pos)
        visited.add(start_pos)

        while queue:
            current = queue.popleft()
            if current == goal_pos:
                # Reconstruir o caminho
                path = []
                while current != start_pos:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path  # Lista de posições a seguir
            neighbors = self.model.grid.get_neighborhood(
                current,
                moore=False,
                include_center=False
            )
            for neighbor in neighbors:
                if neighbor not in visited and 0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
        return []  # Se não encontrar um caminho

    def move_along_path(self, destination=None):
        if not self.path and destination:
            # Planejar caminho até o destino
            self.path = self.plan_path(self.pos, destination)
        if self.path:
            next_step = self.path.pop(0)
            self.model.grid.move_agent(self, next_step)
        else:
            # Se não há caminho, tentar planejar novamente
            if destination:
                self.path = self.plan_path(self.pos, destination)

    def random_move_and_scan(self):
        # Movimento aleatório
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False
        )
        valid_steps = []
        for pos in possible_steps:
            x, y = pos
            if 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height:
                valid_steps.append(pos)
        if valid_steps:
            new_position = self.random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)
            # Escanear por recursos adjacentes
            self.scan_for_resources()

    def scan_for_resources(self):
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,  # Incluir diagonais
            include_center=False
        )
        for pos in neighborhood:
            cell_contents = self.model.grid.get_cell_list_contents([pos])
            for obj in cell_contents:
                if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                    self.known_resources[pos] = obj

    def collect_resource(self):
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        resources = [obj for obj in cell_contents if
                     isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried]

        for resource in resources:
            if resource.required_agents == 1:
                resource.carried = True
                self.carrying = resource
                print(f"{self.name} coletou {resource.name}.")
                self.model.grid.remove_agent(resource)
                # Remover o recurso dos recursos conhecidos
                if self.pos in self.known_resources:
                    del self.known_resources[self.pos]
                # Planejar caminho até a base
                self.path = self.plan_path(self.pos, self.model.base.position)
                break
            elif resource.required_agents == 2:
                agents_in_cell = [obj for obj in cell_contents if
                                  isinstance(obj, ObjectiveAgent) and obj != self and obj.carrying is None]
                if agents_in_cell:
                    resource.carried = True
                    self.carrying = resource
                    other_agent = agents_in_cell[0]
                    other_agent.carrying = resource
                    print(f"{self.name} e {other_agent.name} coletaram {resource.name}.")
                    self.model.grid.remove_agent(resource)
                    # Remover o recurso dos recursos conhecidos
                    if self.pos in self.known_resources:
                        del self.known_resources[self.pos]
                    # Planejar caminho até a base
                    self.path = self.plan_path(self.pos, self.model.base.position)
                    break

    def deliver_resource(self):
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.type} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None
        self.model.num_resources_delivered += 1
        # Limpar o caminho atual
        self.path = []

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
