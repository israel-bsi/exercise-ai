from mesa import Agent
from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure
from Agents.Base import Base

class StateAgent(Agent):
    def __init__(self, unique_id, model, name="StateAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None  # Recurso que o agente está carregando
        self.points = 0
        self.visited_positions = []  # Lista de posições visitadas
        self.known_agents = {}       # Dicionário para armazenar informações sobre outros agentes
        self.shape = "circle"
        self.color = "green"
        self.type = "Agent"
        self.layer = 1
        self.known_resources = {}

    def step(self):
        if self.carrying is not None:
            # Se estiver carregando um recurso, mover-se em direção à base
            self.move_towards(self.model.base.position)
            # Verificar se chegou à base para entregar o recurso
            if self.pos == self.model.base.position:
                self.deliver_resource()
        else:
            # Se não estiver carregando nada, mover-se evitando posições visitadas
            self.move_avoiding_visited()
            self.collect_resource()
            self.interact_with_agents()

        # Detectar recursos próximos
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, (EnergeticCrystal, RareMetalBlock, AncientStructure)) and not obj.carried:
                self.known_resources[self.pos] = obj
                print(f"{self.name} detectou {obj.type} em {self.pos}.")

    def move_avoiding_visited(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,      # Usa vizinhança de Von Neumann (4 direções)
            include_center=False
        )

        # Filtrar posições dentro dos limites da grade
        valid_steps = []
        for pos in possible_steps:
            x, y = pos
            if 0 <= x < self.model.grid.width and 0 <= y < self.model.grid.height:
                valid_steps.append(pos)

        if not valid_steps:
            # Não há movimentos válidos
            return

        # Filtrar posições que não foram visitadas
        new_positions = [pos for pos in possible_steps if pos not in self.visited_positions]

        if new_positions:
            # Escolher uma posição não visitada aleatoriamente
            new_position = self.random.choice(new_positions)
        else:
            # Se todas as posições adjacentes já foram visitadas, escolher qualquer uma
            new_position = self.random.choice(possible_steps)

        # Mover para a nova posição
        self.model.grid.move_agent(self, new_position)
        # Adicionar a posição atual à lista de posições visitadas
        self.visited_positions.append(new_position)

    def move_towards(self, destination):
        current_x, current_y = self.pos
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

        # Verificar limites do grid
        if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
            new_position = (new_x, new_y)
        else:
            # Manter a posição atual se o movimento levaria para fora da grade
            new_position = self.pos

        self.model.grid.move_agent(self, new_position)
        self.visited_positions.append(new_position)

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
                elif resource.required_agents == 2:
                    agents_in_cell = [obj for obj in cell_contents if isinstance(obj, StateAgent) and obj != self and obj.carrying is None]
                    if agents_in_cell:
                        resource.carried = True
                        self.carrying = resource
                        other_agent = agents_in_cell[0]
                        other_agent.carrying = resource
                        print(f"{self.name} e {other_agent.name} coletaram {resource.name}.")
                        self.model.grid.remove_agent(resource)
                        break

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
            print(f"{self.name} encontrou {agent_info['type']} (ID: {agent.unique_id}) na posição {agent_info['position']}.")

    def deliver_resource(self):
        # Entrega o recurso na base
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.type} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None  # Libera o agente para coletar outro recurso
        self.model.num_resources_delivered += 1