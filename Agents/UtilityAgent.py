from mesa import Agent

from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure
from collections import deque

class UtilityAgent(Agent):
    def __init__(self, unique_id, model, name="UtilityAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None
        self.points = 0
        self.target_resource = None
        self.path = []
        self.requests = {}
        self.type = "Agent"
        self.color = "red"
        self.shape = "circle"
        self.layer = 1
        self.known_resources = {}

    def step(self):
        # Verificar solicitações de ajuda
        if self.requests:
            self.respond_to_help_requests()

        if self.carrying is not None:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_along_path(self.model.base.position)
            # Verificar se chegou à base para entregar o recurso
            if self.pos == self.model.base.position:
                self.deliver_resource()
        else:
            if self.target_resource is None:
                # Procurar por recursos
                self.find_target_resource()
            else:
                if not self.path:
                    # Planejar caminho até o recurso alvo
                    self.path = self.plan_path(self.pos, self.target_resource.pos)
                else:
                    # Seguir o caminho até o recurso
                    self.move_along_path()
                    self.collect_resource()

        # Detectar recursos próximos
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                self.known_resources[self.pos] = obj
                print(f"{self.name} detectou {obj.type} em {self.pos}.")

    def find_target_resource(self):
        # Escanear recursos próximos
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False,
            radius=5  # Raio de visão do agente
        )
        for pos in neighborhood:
            cell_contents = self.model.grid.get_cell_list_contents([pos])
            for obj in cell_contents:
                if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                    self.target_resource = obj
                    # Se o recurso requer múltiplos agentes, solicitar ajuda
                    if obj.required_agents > 1:
                        self.request_help(obj)
                    return
        # Se não encontrar recursos, mover-se aleatoriamente
        self.random_move()

    def request_help(self, resource):
        # Enviar pedido de ajuda para outros agentes
        for agent in self.model.schedule.agents:
            if agent != self and isinstance(agent, UtilityAgent):
                agent.receive_help_request(self, resource)

    def receive_help_request(self, requesting_agent, resource):
        # Calcular a utilidade de ajudar
        utility = self.calculate_utility(resource)
        self.requests[requesting_agent.unique_id] = {
            'agent': requesting_agent,
            'resource': resource,
            'utility': utility
        }

    def respond_to_help_requests(self):
        if not self.requests:
            return

        best_request = None
        best_utility = -1

        for req_id, req_info in self.requests.items():
            utility = self.calculate_utility(req_info['resource'])
            if utility > best_utility:
                best_utility = utility
                best_request = req_info
        # Escolher o pedido com maior utilidade
        if best_request:
            best_request = max(self.requests.values(), key=lambda x: x['utility'])
            if best_request['utility'] > self.calculate_utility(self.target_resource) if self.target_resource else 0:
                # Aceitar o pedido
                self.target_resource = best_request['resource']
                self.path = self.plan_path(self.pos, self.target_resource.pos)
                print(f"{self.name} decidiu ajudar {best_request['agent'].name} com {self.target_resource.type}.")
            # Limpar as solicitações após decidir
            self.requests.clear()

    def calculate_utility(self, resource):
        if resource is None or resource.pos is None:
            print(f"{self.name}: Recurso inválido ou sem posição. Utilidade definida como 0.")
            return 0
        # Calcular a distância até o recurso
        distance = self.manhattan_distance(self.pos, resource.pos)

        if resource.type == "EnergeticCrystal":
            utility = 10 / (distance + 1)
        elif resource.type == "RareMetalBlock":
            utility = 20 / (distance + 1)
        elif resource.type == "AncientStructure":
            utility = 30 / (distance + 1)
        else:
            utility = 5 / (distance + 1)
        return utility

    def collect_resource(self):
        from Agents.SimpleAgent import SimpleAgent
        from Agents.StateAgent import StateAgent
        from Agents.ObjectiveAgent import ObjectiveAgent
        from Agents.BDIAgent import BDIAgent
        from Agents.Base import Base

        if self.target_resource and self.pos == self.target_resource.pos:
            resource = self.target_resource
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            agent_classes = (SimpleAgent, StateAgent, ObjectiveAgent, UtilityAgent, BDIAgent)
            resource_classes = (EnergeticCrystal, RareMetalBlock, AncientStructure)
            agents_in_cell = [obj for obj in cell_contents if isinstance(obj, agent_classes)
                              and obj.carrying is None and not isinstance(obj, resource_classes +(Base,))]
            if len(agents_in_cell) >= resource.required_agents:
                # Todos os agentes necessários estão presentes
                resource.carried = True
                self.carrying = resource
                for agent in agents_in_cell:
                    if agent != self:
                        agent.carrying = resource
                        agent.path = self.plan_path(agent.pos, self.model.base.position)
                if len(agents_in_cell) == 2:
                    print(f"{self.name} e outros agentes coletaram {resource.name}.")
                else:
                    print(f"{self.name} coletou {resource.name}.")
                self.model.grid.remove_agent(resource)
                self.model.update_all_agents_known_resources(self.pos)
                self.path = self.plan_path(self.pos, self.model.base.position)
                # Limpar o recurso alvo
                self.target_resource = None

    def deliver_resource(self):
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None
        self.path = []
        self.model.num_resources_delivered += 1

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
                path = []
                while current != start_pos:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
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
        return []

    def move_along_path(self, destination=None):
        if not self.path and destination:
            self.path = self.plan_path(self.pos, destination)
        if self.path:
            next_step = self.path.pop(0)
            self.model.grid.move_agent(self, next_step)
        else:
            if destination:
                self.path = self.plan_path(self.pos, destination)

    def random_move(self):
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

    def manhattan_distance(self, pos1, pos2):
        if pos1 is None or pos2 is None:
            print(f"{self.name}: Uma das posições é None. Retornando distância infinita.")
            return float('inf')  # Retorna um valor alto para indicar distância infinita

        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
