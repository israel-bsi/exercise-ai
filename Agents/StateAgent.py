from mesa import Agent

from Agents.CollectingAgent import CollectingAgent
from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure
from Agents.Base import Base

class StateAgent(CollectingAgent):
    def __init__(self, unique_id, model, name="StateAgent"):
        super().__init__(unique_id, model)
        self.color = "green"
        self.name = name

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        # Memorizar a posição atual
        self.visited_positions.add(self.pos)

        # Interagir com outros agentes na mesma célula
        self.interact_with_agents()

        if self.carrying:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_toward(self.model.base.pos)
            if self.pos == self.model.base.pos:
                self.deliver_resource()
        elif self.target_resource:
            # Se tem um recurso como alvo, mover-se em direção a ele
            self.move_toward(self.target_resource.pos)
            if self.pos == self.target_resource.pos:
                self.collect_resource()
        else:
            # Procurar por recursos ou explorar
            self.find_target_resource()

    def receive_help_request(self, requesting_agent, resource):
        """Recebe solicitação de ajuda para coletar um recurso."""
        if self.carrying is None and self.target_resource is None:
            self.target_resource = resource
            self.model.available_utility_agents.remove(self)
            print(f"{self.name} aceitou ajudar {requesting_agent.name} a coletar {resource.type} em {resource.pos}.")
        else:
            print(f"{self.name} não pode ajudar no momento.")

    def collect_resource(self):
        """Coleta o recurso na célula atual se todos os agentes necessários estiverem presentes."""
        from Agents.UtilityAgent import UtilityAgent
        from Agents.ObjectiveAgent import ObjectiveAgent
        from Agents.BDIAgent import BDIAgent

        if self.target_resource and self.pos == self.target_resource.pos:
            resource = self.target_resource
            cell_contents = self.model.grid.get_cell_list_contents([self.pos])
            agents_in_cell = [
                obj for obj in cell_contents
                if isinstance(obj, (StateAgent, UtilityAgent, ObjectiveAgent, BDIAgent)) and obj.carrying is None
            ]
            if len(agents_in_cell) >= resource.required_agents:
                # Coletar o recurso
                resource.carried = True
                self.carrying = resource
                for agent in agents_in_cell:
                    agent.carrying = resource
                    agent.target_resource = None  # Resetar o recurso alvo
                    agent.visited_positions.add(agent.pos)
                    print(f"{self.name} e {agent.name} coletaram {resource.type}.")
                self.model.grid.remove_agent(resource)
                self.move_toward(self.model.base.pos)
                self.target_resource = None
            else:
                print(f"{self.name} está esperando por mais agentes para coletar {resource.type}.")

    def interact_with_agents(self):
        # Obter os conteúdos da célula atual
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        other_agents = [obj for obj in cell_contents if isinstance(obj, Agent) and obj != self and not isinstance(obj, Base)]

        for agent in other_agents:
            # Armazenar informações sobre o agente
            agent_info = {
                'type': type(agent).__name__,
                'position': agent.pos,
                # Adicione outras informações relevantes se necessário
            }
            self.known_agents[agent.unique_id] = agent_info
            #print(f"{self.name} encontrou {agent_info['type']} (ID: {agent.unique_id}) na posição {agent_info['position']}.")

    def deliver_resource(self):
        # Entrega o recurso na base
        if self.carrying.required_agents == 2:
            points = self.carrying.value / 2
        else:
            points = self.carrying.value
        self.points += points
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {points} pontos.")
        self.carrying = None  # Libera o agente para coletar outro recurso
        #self.partner.carrying = None
        self.model.num_resources_delivered += 1
        if self not in self.model.available_utility_agents:
            self.model.available_utility_agents.append(self)
            print(f"{self.name} agora está disponível para ajudar novamente.")

    def find_target_resource(self):
        """Procura por recursos não coletados próximos e evita áreas já exploradas."""
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False,
            radius=5  # Raio de visão do agente
        )

        for pos in neighborhood:
            if pos in self.visited_positions:
                continue  # Ignorar posições já visitadas

            cell_contents = self.model.grid.get_cell_list_contents([pos])
            for obj in cell_contents:
                if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                    self.target_resource = obj
                    self.move_toward(pos)
                    self.known_resources[pos] = obj  # Armazenar informações sobre o recurso
                    print(f"{self.name} detectou {obj.type} em {pos}.")
                    return

        # Se nenhum recurso for encontrado, mover-se aleatoriamente
        self.random_move()

    def random_move(self):
        """Move-se para uma célula aleatória não visitada. Se não houver, move-se para qualquer célula adjacente válida."""
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,  # Sem movimento diagonal
            include_center=False
        )

        # Filtrar células adjacentes não visitadas
        unvisited_steps = [
            pos for pos in possible_steps
            if pos not in self.visited_positions and
               0 <= pos[0] < self.model.grid.width and
               0 <= pos[1] < self.model.grid.height
        ]

        if unvisited_steps:
            # Se houver células não visitadas, mover-se para uma delas
            new_position = self.random.choice(unvisited_steps)
            self.model.grid.move_agent(self, new_position)
            #print(f"{self.name} move para {new_position} aleatoriamente (não visitada).")
        else:
            # Se não houver células não visitadas, permitir mover-se para qualquer célula adjacente válida
            valid_steps = [
                pos for pos in possible_steps
                if 0 <= pos[0] < self.model.grid.width and
                   0 <= pos[1] < self.model.grid.height
            ]

            if valid_steps:
                new_position = self.random.choice(valid_steps)
                self.model.grid.move_agent(self, new_position)
                #print(f"{self.name} move para {new_position} aleatoriamente (já visitada).")
            else:
                # Se não houver células adjacentes válidas (muito raro em grades conectadas), o agente fica parado
                print(f"{self.name} não encontrou passos válidos para mover.")

    def move_toward(self, destination=None):
        """Move-se em direção a um destino (recurso, base ou qualquer posição). Se não houver, move-se aleatoriamente."""
        # Se não houver destino, mover aleatoriamente
        if destination is None:
            self.random_move()
            return

        # Obter coordenadas do destino
        dest_x, dest_y = destination
        current_x, current_y = self.pos

        # Calcular a direção para mover
        dx = dest_x - current_x
        dy = dest_y - current_y

        # Determinar o próximo passo em x
        move_x = current_x + (1 if dx > 0 else -1 if dx < 0 else 0)
        # Determinar o próximo passo em y
        move_y = current_y + (1 if dy > 0 else -1 if dy < 0 else 0)

        # Verificar se a nova posição é válida
        if 0 <= move_x < self.model.grid.width and 0 <= move_y < self.model.grid.height:
            new_position = (move_x, move_y)
        else:
            # Se a posição não for válida, manter posição atual
            new_position = self.pos

        self.model.grid.move_agent(self, new_position)
        #print(f"{self.name} move para {new_position} em direção ao destino {destination}.")