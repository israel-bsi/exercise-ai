from Agents.CollectingAgent import CollectingAgent
from Resources.AncientStructure import AncientStructure  # Importar classes de recursos grandes

class ObjectiveAgent(CollectingAgent):
    def __init__(self, unique_id, model, name="ObjectiveAgent"):
        super().__init__(unique_id, model)
        self.color = "yellow"
        self.name = name
        self.carrying = None  # Recurso que está carregando
        self.partner = None  # Referência ao agente parceiro

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        #print(f"{self.name} - Posição: {self.pos}, Carregando: {self.carrying}, Parceiro: {self.partner}")

        if self.carrying:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_toward(self.model.base.pos)
            if self.pos == self.model.base.pos:
                self.deliver_resource()
        else:
            # Procurar por recursos grandes
            resource = self.find_nearest_large_resource()
            if resource:
                # Se encontrar um recurso grande, solicitar ajuda
                self.request_help(resource)
                # Mover-se em direção ao recurso (apenas para visualização ou aproximação inicial)
                self.move_toward(resource.pos)
            else:
                # Se não encontrar, mover-se aleatoriamente ou realizar outra ação
                self.random_move()

    def find_nearest_large_resource(self):
        """Procura pelo recurso grande mais próximo."""
        min_distance = float('inf')
        nearest_resource = None
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False,
            radius=10  # Raio de visão do agente
        )
        for pos in neighborhood:
            cell_contents = self.model.grid.get_cell_list_contents([pos])
            for obj in cell_contents:
                if isinstance(obj, AncientStructure) and not obj.carried:
                    distance = self.model.manhattan_distance(self.pos, pos)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_resource = obj
        return nearest_resource

    def request_help(self, resource):
        """Envia uma solicitação de ajuda para o UtilityAgent."""
        if resource is None:
            print(f"{self.name} tentou solicitar ajuda, mas nenhum recurso foi encontrado.")
            return

        if self.model.available_utility_agents:
            self.model.add_help_request(self, resource)

    def move_toward(self, destination):
        """Move-se em direção ao destino."""
        if self.pos == destination:
            return  # Já está no destino

        # Calcula o próximo passo em direção ao destino (caminho simplificado)
        new_position = self.get_next_position_toward(destination)
        if new_position:
            self.model.grid.move_agent(self, new_position)
           #print(f"{self.name} move para {new_position} em direção a {destination}.")

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
            #print(f"{self.name} não está carregando nenhum recurso para entregar.")
            return

        # Calcular pontos com base no tipo de recurso
        if isinstance(self.carrying, AncientStructure):
            points = self.carrying.value / 2
        else:
            points = self.carrying.value

        self.points += points
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {points} pontos.")

        # Resetar estado
        self.carrying = None
        self.partner = None
        self.model.num_resources_delivered += 1
