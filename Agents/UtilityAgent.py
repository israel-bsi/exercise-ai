from Agents.CollectingAgent import CollectingAgent

class UtilityAgent(CollectingAgent):
    def __init__(self, unique_id, model, name="UtilityAgent"):
        super().__init__(unique_id, model)
        self.color = "red"
        self.name = name
        self.available = True  # Flag para indicar disponibilidade para ajudar
        self.current_request = None  # Solicitação atual de ajuda
        self.partner = None  # Referência ao agente parceiro

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        print(
            f"{self.name} - Posição: {self.pos}, Disponível: {self.available}, Solicitação Atual: {self.current_request}")

        if self.available and self.model.help_requests:
            self.process_help_requests()

        if self.current_request:
            resource = self.current_request['resource']
            if self.pos != resource.pos:
                self.move_toward(resource.pos)
                print(f"{self.name} está se movendo para {resource.pos} para ajudar na coleta.")
            else:
                self.assist_collect(resource)

    def process_help_requests(self):
        """Processa as solicitações de ajuda disponíveis e seleciona a melhor para ajudar."""
        best_request = None
        best_utility = -1

        for request in self.model.help_requests:
            print(f"Processando solicitação: {request}")
            if 'requester' not in request or 'resource' not in request:
                print(f"Solicitação malformada ignorada: {request}")
                continue  # Ignora solicitações malformadas

            resource = request['resource']
            if resource is None:
                print(f"Solicitação ignorada porque 'resource' é None: {request}")
                continue  # Ignora solicitações com resource=None

            distance = self.model.manhattan_distance(self.pos, resource.pos)
            utility = self.calculate_utility(distance, len(self.model.available_utility_agents))

            print(
                f"Solicitação: requester={request['requester'].name}, resource={resource.type}, distance={distance}, utility={utility}")

            if utility > best_utility:
                best_utility = utility
                best_request = request

        if best_request:
            self.accept_help(best_request)
        else:
            print(f"{self.name} não encontrou solicitações de ajuda com utilidade positiva.")

    def calculate_utility(self, distance, available_agents):
        """Calcula a utilidade de ajudar com base na distância e no número de agentes disponíveis."""
        # Exemplo de cálculo: mais próximo e mais agentes disponíveis aumentam a utilidade
        utility = (available_agents) / (distance + 1)
        print(f"{self.name} calculou utilidade {utility} para ajudar.")
        return utility

    def accept_help(self, request):
        """Aceita uma solicitação de ajuda."""
        self.current_request = request
        self.available = False
        requester = request['requester']
        resource = request['resource']

        # Remover a solicitação da fila
        self.model.remove_help_request(request)

        # Remover o UtilityAgent da lista de disponíveis
        if self in self.model.available_utility_agents:
            self.model.available_utility_agents.remove(self)

        # Planejar caminho para o recurso
        self.path = self.plan_path(self.pos, resource.pos)
        print(f"{self.name} aceitou ajudar {requester.name} na coleta de {resource.type} em {resource.pos}.")

        # Log adicional para verificar o conteúdo de current_request
        print(f"Current Request após aceitação: {self.current_request}")

    def assist_collect(self, resource):
        """Assiste na coleta do recurso junto com o agente solicitante."""
        if not self.current_request:
            print(f"{self.name} não tem uma solicitação atual para processar.")
            return

        if 'requester' not in self.current_request:
            print(f"{self.name} recebeu uma solicitação sem 'requester': {self.current_request}")
            self.current_request = None
            self.available = True
            return

        requester = self.current_request['requester']
        resource = self.current_request['resource']

        if resource is None:
            print(f"{self.name} está tentando coletar um recurso que é None.")
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
        print(f"{self.name} e {requester.name} coletaram {resource.type} e estão a caminho da base.")

        # Resetar a solicitação atual
        self.current_request = None

        # Atualizar disponibilidade
        self.available = True
        if self not in self.model.available_utility_agents:
            self.model.available_utility_agents.append(self)
            print(f"{self.name} está agora disponível para ajudar.")

    def move_toward(self, destination):
        """Move-se em direção ao destino."""
        if self.pos == destination:
            return  # Já está no destino

        # Calcula o próximo passo em direção ao destino (caminho simplificado)
        new_position = self.get_next_position_toward(destination)
        if new_position:
            self.model.grid.move_agent(self, new_position)
            print(f"{self.name} move para {new_position} em direção a {destination}.")

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

    def manhattan_distance(self, pos1, pos2):
        """Calcula a distância de Manhattan entre duas posições."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
