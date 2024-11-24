from Agents.CollectingAgent import CollectingAgent
from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure

class UtilityAgent(CollectingAgent):
    def __init__(self, unique_id, model, name="UtilityAgent"):
        super().__init__(unique_id, model)
        self.color = "red"
        self.name = name
        self.requests = {}  # Armazena as solicitações de ajuda

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        # Verificar solicitações de ajuda
        if self.requests:
            self.respond_to_help_requests()

        if self.carrying is not None:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_toward(self.model.base.pos)  # Base como destino
            if self.pos == self.model.base.pos:
                self.deliver_resource()
        elif self.target_resource:
            # Se tem um recurso como alvo, mover-se em direção a ele
            self.move_toward(self.target_resource.pos)  # Recurso como destino
            if self.pos == self.target_resource.pos:
                self.collect_resource()
        else:
            # Procurar por recursos ou explorar
            self.find_target_resource()

        # Atualizar disponibilidade de ajuda no modelo
        self.update_availability()

    def move_toward(self, destination=None):
        """Move-se em direção a um destino (recurso, base ou qualquer posição). Se não houver, move-se aleatoriamente."""
        if destination is None:
            self.random_move()
            return

        # Obter coordenadas do destino
        dest_x, dest_y = destination
        current_x, current_y = self.pos

        # Calcular a direção para mover
        dx = dest_x - current_x
        dy = dest_y - current_y

        # Determinar o próximo passo em x e y
        move_x = current_x + (1 if dx > 0 else -1 if dx < 0 else 0)
        move_y = current_y + (1 if dy > 0 else -1 if dy < 0 else 0)

        # Verificar se a nova posição é válida
        if 0 <= move_x < self.model.grid.width and 0 <= move_y < self.model.grid.height:
            new_position = (move_x, move_y)
        else:
            # Se a posição não for válida, manter posição atual
            new_position = self.pos

        self.model.grid.move_agent(self, new_position)
        print(f"{self.name} move para {new_position} em direção ao destino {destination}.")

    def find_target_resource(self):
        """Procura por recursos não coletados próximos e solicita ajuda para os grandes."""
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False,
            radius=10  # Raio de visão do agente
        )

        for pos in neighborhood:
            cell_contents = self.model.grid.get_cell_list_contents([pos])
            for obj in cell_contents:
                if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                    if obj.required_agents > 1:
                        self.target_resource = obj
                        self.request_help(obj)
                        print(f"{self.name} encontrou {obj.name} e solicitou ajuda.")
                        return
                    else:
                        self.target_resource = obj
                        self.move_toward(pos)
                        print(f"{self.name} encontrou {obj.name} e está coletando sozinho.")
                        return
        # Se não encontrar recursos, mover-se aleatoriamente
        self.random_move()

    def request_help(self, resource):
        """Solicita ajuda de outros UtilityAgents para coletar um recurso grande."""
        for agent in self.model.available_utility_agents.copy():
            if agent != self and not agent.carrying:
                agent.receive_help_request(self, resource)
                print(f"{self.name} solicitou ajuda de {agent.name} para coletar {resource.name}.")

    def receive_help_request(self, requesting_agent, resource):
        """Recebe e armazena uma solicitação de ajuda."""
        if self.carrying is not None:
            print(f"{self.name} está ocupado e não pode ajudar {requesting_agent.name} com {resource.name}.")
            return

        # Calcular a utilidade de ajudar
        utility = self.calculate_utility(resource)
        self.requests[requesting_agent.unique_id] = {
            'agent': requesting_agent,
            'resource': resource,
            'utility': utility
        }
        print(f"{self.name} recebeu solicitação de ajuda de {requesting_agent.name}. Utilidade: {utility}.")

    def respond_to_help_requests(self):
        """Responde ao pedido de ajuda com maior utilidade."""
        if not self.requests:
            return

        best_request = max(self.requests.values(), key=lambda x: x['utility'])
        if best_request['utility'] > self.calculate_utility(self.target_resource) if self.target_resource else 0:
            self.target_resource = best_request['resource']
            self.move_toward(self.target_resource.pos)
            print(f"{self.name} decidiu ajudar {best_request['agent'].name} com {self.target_resource.name}.")

        # Limpar as solicitações após decidir
        self.requests.clear()

    def calculate_utility(self, resource):
        """Calcula a utilidade de ajudar a coletar um recurso com base na distância e no número de agentes."""
        if resource is None or resource.pos is None:
            print(f"{self.name}: Recurso inválido ou sem posição. Utilidade definida como 0.")
            return 0
        # Calcular a distância até o recurso
        distance = self.manhattan_distance(self.pos, resource.pos)

        # Utilidade baseada no tipo de recurso e na distância
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
        """Coleta o recurso se todos os agentes necessários estiverem presentes."""
        from Agents.SimpleAgent import SimpleAgent
        from Agents.StateAgent import StateAgent
        from Agents.ObjectiveAgent import ObjectiveAgent
        from Agents.BDIAgent import BDIAgent
        from Agents.Base import Base
        if self.target_resource and self.pos == self.target_resource.pos:
            resource = self.target_resource
            # Filtra os agentes que não estão carregando nada e que não são recursos nem a base
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            agent_classes = (SimpleAgent, StateAgent, ObjectiveAgent, UtilityAgent, BDIAgent)
            resource_classes = (EnergeticCrystal, RareMetalBlock, AncientStructure)
            agents_in_cell = [obj for obj in cell_contents if isinstance(obj, agent_classes)
                              and obj.carrying is None and not isinstance(obj, resource_classes + (Base,))]

            if len(agents_in_cell) >= resource.required_agents:
                # Todos os agentes necessários estão presentes
                resource.carried = True
                self.carrying = resource
                for agent in agents_in_cell:
                    if agent != self:
                        agent.carrying = resource
                        agent.path = self.plan_path(agent.pos, self.model.base.position)
                        agent.target_resource = None

                self.model.grid.remove_agent(resource)
                self.model.update_all_agents_known_resources(self.pos)
                self.path = self.plan_path(self.pos, self.model.base.position)
                # Limpar o recurso alvo
                self.target_resource = None
                if len(agents_in_cell) == 2:
                    print(f"{self.name} e outros agentes coletaram {resource.name}.")
                else:
                    print(f"{self.name} coletou {resource.name}.")

    def deliver_resource(self):
        """Entrega o recurso na base e ganha pontos."""
        if self.carrying.required_agents == 2:
            points = self.carrying.value / 2
        else:
            points = self.carrying.value
        self.points += points
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {points} pontos.")
        self.carrying = None
        self.path = []
        self.model.num_resources_delivered += 1
        self.update_availability()

    def update_availability(self):
        """Atualiza se o agente está disponível ou não para ajudar."""
        if self.carrying is None and self.target_resource is None:
            if self not in self.model.available_utility_agents:
                self.model.available_utility_agents.append(self)
                print(f"{self.name} agora está disponível para ajudar.")
        else:
            if self in self.model.available_utility_agents:
                self.model.available_utility_agents.remove(self)
                print(f"{self.name} está ocupado e não está mais disponível para ajudar.")

    def random_move(self):
        """Move-se aleatoriamente para uma célula válida."""
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        valid_steps = [pos for pos in possible_steps if
                       0 <= pos[0] < self.model.grid.width and 0 <= pos[1] < self.model.grid.height]
        if valid_steps:
            new_position = self.random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)
            print(f"{self.name} move para {new_position} aleatoriamente.")

    def manhattan_distance(self, pos1, pos2):
        """Calcula a distância de Manhattan entre duas posições."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
