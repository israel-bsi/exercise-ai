from Agents.CollectingAgent import CollectingAgent
from threading import Lock

from Resources.AncientStructure import AncientStructure

class UtilityAgent(CollectingAgent):
    lock = Lock()

    def __init__(self, unique_id, model, name="UtilityAgent"):
        super().__init__(unique_id, model)
        self.color = "red"
        self.name = name
        self.available = True  # Flag para indicar disponibilidade para ajudar
        self.current_request = None  # Solicitação atual de ajuda
        self.partner = None  # Referência ao agente parceiro
        self.carrying = None  # Recurso que está carregando

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""

        if self.carrying:
            if self.pos != self.model.base.pos:
                self.move_toward(self.model.base.pos)
            else:
                self.deliver_resource()

        elif self.available and self.model.help_requests:
            self.process_help_requests()

        if self.current_request:
            resource = self.current_request['resource']
            if self.pos != resource.pos:
                self.move_toward(resource.pos)
            else:
                self.assist_collect()

    def process_help_requests(self):
        """Processa as solicitações de ajuda disponíveis e seleciona a melhor para ajudar."""
        with UtilityAgent.lock:
            if not self.available:
                return

        best_request = None
        best_utility = -1

        for request in self.model.help_requests:
            if 'requester' not in request or 'resource' not in request:
                continue

            resource = request['resource']
            if resource is None:
                continue

            # Verifica se o limite de agentes já foi alcançado
            if request.get('assigned_agents', 0) >= request.get('max_agents', 1):
                continue  # Limite atingido, ignora essa solicitação

            distance = self.model.manhattan_distance(self.pos, resource.pos)
            utility = self.calculate_utility(distance, len(self.model.available_utility_agents))

            if utility > best_utility:
                best_utility = utility
                best_request = request

        if best_request:
            self.accept_help(best_request)

    def calculate_utility(self, distance, available_agents):
        """Calcula a utilidade de ajudar com base na distância e no número de agentes disponíveis."""
        utility = available_agents / (distance + 1)
        return utility

    def accept_help(self, request):
        """Aceita uma solicitação de ajuda."""

        # Verifica novamente dentro do lock se a solicitação ainda pode receber mais agentes
        if request.get('assigned_agents', 0) >= request.get('max_agents', 1):
            return  # Limite já atingido, não pode aceitar

        self.current_request = request
        self.available = False
        requester = request['requester']
        resource = request['resource']

        # Incrementa o contador de agentes atribuídos
        request['assigned_agents'] = request.get('assigned_agents', 0) + 1

        # Se o limite for alcançado após a atribuição, remove a solicitação
        if request['assigned_agents'] >= request.get('max_agents', 1):
            self.model.remove_help_request(request)
            print(f"Solicitação para {resource.name} removida após atingir o limite de agentes.")

        # Remover a solicitação da fila
        self.model.remove_help_request(request)

        # Remover o UtilityAgent da lista de disponíveis
        if self in self.model.available_utility_agents:
            self.model.available_utility_agents.remove(self)

        # Planejar caminho para o recurso
        self.path = self.plan_path(self.pos, resource.pos)
        print(f"{self.name} aceitou ajudar {requester.name} na coleta de {resource.name} em {resource.pos}.")

    def assist_collect(self):
        """Assiste na coleta do recurso junto com o agente solicitante."""
        if not self.current_request:
            return

        if 'requester' not in self.current_request:
            self.current_request = None
            self.available = True
            return

        requester = self.current_request['requester']
        resource = self.current_request['resource']

        if resource is None:
            self.current_request = None
            self.available = True
            return

        # Configurar estados de ambos os agentes
        self.carrying = resource
        requester.carrying = resource

        # Definir parceiros
        self.partner = requester
        requester.partner = self

        # Planejar caminho para a base
        self.path = self.plan_path(self.pos, self.model.base.pos)
        requester.path = self.plan_path(requester.pos, self.model.base.pos)

        # Remover o recurso da grade para evitar múltiplas coletas
        self.model.grid.remove_agent(resource)
        print(f"{self.name} e {requester.name} coletaram {resource.name} e estão a caminho da base.")

        # Resetar a solicitação atual
        self.current_request = None

        # Atualizar disponibilidade
        self.available = True
        if self not in self.model.available_utility_agents:
            self.model.available_utility_agents.append(self)

    def move_toward(self, destination):
        """Move-se em direção ao destino."""
        if self.pos == destination:
            return

        new_position = self.get_next_position_toward(destination)
        if new_position:
            self.model.grid.move_agent(self, new_position)

    def get_next_position_toward(self, destination):
        """Determina a próxima posição para mover em direção ao destino."""
        current_x, current_y = self.pos
        dest_x, dest_y = destination

        dx = dest_x - current_x
        dy = dest_y - current_y

        step_x = current_x + (1 if dx > 0 else -1 if dx < 0 else 0)
        step_y = current_y + (1 if dy > 0 else -1 if dy < 0 else 0)

        # Verificar se a nova posição é válida
        if 0 <= step_x < self.model.grid.width and 0 <= step_y < self.model.grid.height:
            return (step_x, step_y)
        else:
            return None

    def deliver_resource(self):
        """Entrega o recurso na base e atualiza os pontos."""
        if self.carrying is None:
            return

        # Calcular pontos com base no tipo de recurso
        if isinstance(self.carrying, AncientStructure):
            points = self.carrying.value / 2
        else:
            points = self.carrying.value

        self.points += points
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {points} pontos.")

        # Atualizar disponibilidade
        self.available = True
        with UtilityAgent.lock:
            if self not in self.model.available_utility_agents:
                self.model.available_utility_agents.append(self)

        # Resetar estado
        self.carrying = None
        self.partner = None
        self.model.num_resources_delivered += 1
