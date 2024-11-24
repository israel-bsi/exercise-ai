from mesa import Agent


from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure

class BDIAgent(Agent):
    def __init__(self, unique_id, model, name="BDIAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.beliefs = {}  # Dicionário: posição -> tipo de recurso
        self.desires = "Collect maximum resources collectively"
        self.intentions = []  # Lista de intenções ou ações planejadas
        self.path = []  # Lista de posições a seguir
        self.carrying = None
        self.points = 0
        self.shape = "circle"
        self.color = "purple"
        self.type = "Agent"
        self.layer = 1
        self.known_resources = {}

    def step(self):
        # Passo 1: Receber informações dos outros agentes
        self.update_beliefs()

        # Passo 2: Administrar o painel de informações
        self.update_information_panel()

        # Passo 3: Planejar ações baseadas nas crenças e desejos
        self.plan_actions()

        # Passo 4: Executar intenções planejadas
        self.execute_intention()

        # Passo 5: Entregar recursos na base
        self.deliver_resource()

    def update_beliefs(self):
        # Detectar recursos próximos
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                self.known_resources[self.pos] = obj
                #print(f"{self.name} detectou {obj.type} em {self.pos}.")

        # Receber informações dos outros agentes
        for agent in self.model.schedule.agents:
            if agent != self and hasattr(agent, 'known_resources'):
                for pos, resource in agent.known_resources.items():
                    if pos not in self.beliefs:
                        self.beliefs[pos] = resource.type
                        print(f"{self.name} atualizou crença: Recurso {resource.type} em {pos}.")

    def update_information_panel(self):
        # Implementar lógica adicional para gerenciar o painel de informações
        # Aqui, apenas imprimimos as crenças atuais
        print(f"{self.name} - Painel de Informação:")
        for pos, res_type in self.beliefs.items():
            print(f"  Recurso: {res_type} em {pos}")

    def plan_actions(self):
        # Baseado nas crenças, planeje coletar recursos
        if not self.intentions:
            # Identificar recursos não coletados
            resources_to_collect = [(pos, res_type) for pos, res_type in self.beliefs.items()]
            # Ordenar por utilidade (quanto maior a utilidade, maior a prioridade)
            resources_sorted = sorted(resources_to_collect, key=lambda x: self.calculate_utility(x[0], x[1]),
                                      reverse=True)

            for pos, res_type in resources_sorted:
                # Planejar rota até o recurso
                path = self.plan_path(self.pos, pos)
                if path:
                    self.intentions.append(('collect', pos, res_type, path))
                    print(f"{self.name} planeja coletar {res_type} em {pos}.")
                    break  # Planeja uma ação por passo

    def calculate_utility(self, pos, res_type):
        # Calcular a utilidade de coletar este recurso
        # Exemplo simples: utilidade baseada no tipo de recurso e distância
        distance = self.manhattan_distance(self.pos, pos)
        utility = 0
        if res_type == "EnergeticCrystal":
            utility = 10 / (distance + 1)
        elif res_type == "RareMetalBlock":
            utility = 20 / (distance + 1)
        elif res_type == "AncientStructure":
            utility = 30 / (distance + 1)
        return utility

    def plan_path(self, start_pos, goal_pos):
        # Implementar BFS para encontrar o caminho mais curto
        from collections import deque

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

    def execute_intention(self):
        if self.intentions:
            action = self.intentions.pop(0)
            action_type, pos, res_type, path = action
            if action_type == 'collect':
                # Executar a ação de coletar
                # Mover o BDIAgent para o recurso
                if path:
                    next_step = path.pop(0)
                    self.model.grid.move_agent(self, next_step)
                    print(f"{self.name} move para {next_step} para coletar {res_type}.")
                    # Coordenar a coleta com outros agentes
                    self.collect_resource(pos, res_type)
        else:
            # Se não há intenções, verificar se o agente está carregando um recurso
            if self.carrying:
                # Se estiver carregando, planejar o caminho de volta à base
                if not self.path:
                    self.path = self.plan_path(self.pos, self.model.base.position)
                if self.path:
                    next_step = self.path.pop(0)
                    self.model.grid.move_agent(self, next_step)
                    print(f"{self.name} move para {next_step} para entregar {self.carrying.type}.")
                    # Verificar se chegou na base
                    if self.pos == self.model.base.position:
                        self.deliver_resource()

    def collect_resource(self, pos, res_type):
        # Implementar a lógica de coleta, semelhante aos outros agentes
        cell_contents = self.model.grid.get_cell_list_contents([pos])
        resource = None
        for obj in cell_contents:
            if isinstance(obj, (
                    EnergeticCrystal, RareMetalBlock, AncientStructure)) and obj.type == res_type and not obj.carried:
                resource = obj
                break
        if resource:
            # Importar classes de agentes aqui para evitar circular imports
            from Agents.SimpleAgent import SimpleAgent
            from Agents.StateAgent import StateAgent
            from Agents.ObjectiveAgent import ObjectiveAgent
            from Agents.UtilityAgent import UtilityAgent
            from Agents.BDIAgent import BDIAgent

            # Informar os agentes disponíveis para ajudar
            agents_in_cell = [
                obj for obj in cell_contents
                if isinstance(obj, (SimpleAgent, StateAgent, ObjectiveAgent, UtilityAgent,
                                    BDIAgent)) and obj.carrying is None and obj != self
            ]
            if len(agents_in_cell) >= resource.required_agents - 1:
                # Coletar recurso com ajuda de outros agentes
                resource.carried = True
                self.carrying = resource
                for agent in agents_in_cell[:resource.required_agents - 1]:
                    agent.carrying = resource
                    agent.path = self.plan_path(agent.pos, self.model.base.position)
                print(f"{self.name} e outros agentes coletaram {resource.type} em {pos}.")
                self.model.grid.remove_agent(resource)
                self.path = self.plan_path(self.pos, self.model.base.position)
                self.beliefs.pop(pos, None)

    def deliver_resource(self):
        # Implementar a lógica de entrega de recursos na base
        if self.carrying and self.pos == self.model.base.position:
            # Assegure-se de que a base possui um atributo para armazenar pontos
            self.model.base.points += self.carrying.value
            self.points += self.carrying.value
            print(f"{self.name} entregou {self.carrying.type} na base e ganhou {self.carrying.value} pontos.")
            self.carrying = None
            self.model.num_resources_delivered += 1

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
