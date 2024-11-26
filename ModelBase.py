from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from Agents.CollectingAgent import CollectingAgent
from Agents.SimpleAgent import SimpleAgent
from Agents.Base import Base
from Agents.StateAgent import StateAgent
from Agents.UtilityAgent import UtilityAgent
from Agents.ObjectiveAgent import ObjectiveAgent
from Agents.BDIAgent import BDIAgent

from Resources.EnergeticCrystal import EnergeticCrystal
from Resources.RareMetalBlock import RareMetalBlock
from Resources.AncientStructure import AncientStructure

class ModelBase(Model):
    def __init__(self, num_agents, num_resources, grid_params):
        super().__init__()
        self.current_id = 0
        self.num_agents = num_agents
        self.num_resources = num_resources
        self.grid = MultiGrid(grid_params["width"], grid_params["height"], False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.resource_id = 1000
        self.num_resources_total = 0
        self.available_utility_agents = []
        self.help_requests = []

        # Inicializar a base
        self.base_position = (0, 0)
        self.base = Base(self.next_id(), self, self.base_position)
        self.grid.place_agent(self.base, self.base_position)

        # Inicializar os agentes
        id = 0
        for i in range(self.num_agents["SimpleAgent"]):
            agent = SimpleAgent(unique_id=id + 1, model=self, name=f"SimpleAgent_{id + 1}")
            self.grid.place_agent(agent, self.find_random_empty_cell())
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["StateAgent"]):
            agent = StateAgent(unique_id=id + 1, model=self, name=f"StateAgent_{id + 1}")
            self.grid.place_agent(agent, self.find_random_empty_cell())
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["ObjectiveAgent"]):
            agent = ObjectiveAgent(unique_id=id + 1, model=self, name=f"ObjectiveAgent_{id + 1}")
            self.grid.place_agent(agent, self.find_random_empty_cell())
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["UtilityAgent"]):
            agent = UtilityAgent(unique_id=id + 1, model=self, name=f"UtilityAgent_{id + 1}")
            self.grid.place_agent(agent, self.find_random_empty_cell())
            self.schedule.add(agent)
            self.available_utility_agents.append(agent)
            id += 1

        for i in range(self.num_agents["BDIAgent"]):
            bdi_agent = BDIAgent(unique_id=id + 1, model=self, name=f"BDIAgent_{id + 1}")
            self.grid.place_agent(bdi_agent, self.find_random_empty_cell())
            self.schedule.add(bdi_agent)
            id += 1

        # Inicializar os recursos
        resource_types = [("EnergeticCrystal", num_resources["EnergeticCrystal"]),
                          ("RareMetalBlock", num_resources["RareMetalBlock"]),
                          ("AncientStructure", num_resources["AncientStructure"])]

        self.num_resources_total = num_resources["EnergeticCrystal"] + num_resources["RareMetalBlock"] + num_resources["AncientStructure"]
        self.num_resources_delivered = 0

        for resource_type, quantity in resource_types:
            for _ in range(quantity):
                if resource_type == "EnergeticCrystal":
                    resource = EnergeticCrystal(self.resource_id, self)
                elif resource_type == "RareMetalBlock":
                    resource = RareMetalBlock(self.resource_id, self)
                elif resource_type == "AncientStructure":
                    resource = AncientStructure(self.resource_id, self)
                self.resource_id += 1
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.place_agent(resource, (x, y))
                self.num_resources_total += 1

        self.datacollector = DataCollector(
            model_reporters={"TotalPoints": self.compute_total_points}
        )

    def find_random_empty_cell(self):
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            cell = (x, y)
            if not self.grid.is_cell_empty(cell):
                continue
            return cell

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        if self.num_resources_delivered == self.num_resources_total:
            self.running = False  # Para a simulação

            # Imprimir os pontos de cada agente
            print("\nSimulação finalizada. Pontos coletados por cada agente:")
            agents_with_points = [
                agent for agent in self.schedule.agents if hasattr(agent, 'points')
            ]
            agents_with_points.sort(key=lambda agent: agent.points, reverse=True)
            for agent in agents_with_points:
                print(f"{agent.name} (ID: {agent.unique_id}): {agent.points} pontos")

            # Imprimir o total de pontos coletados
            total_points = sum(agent.points for agent in agents_with_points)
            print(f"Total de pontos coletados por todos os agentes: {total_points}")

    def compute_total_points(self):
        total = sum([agent.points for agent in self.schedule.agents if hasattr(agent, 'points')])
        return total

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def update_all_agents_known_resources(self, pos):
        """Atualiza a lista de recursos conhecidos para todos os agentes após coleta."""
        cell_contents = self.grid.get_cell_list_contents([pos])
        resource_present = any(isinstance(obj, AncientStructure) and not obj.carried for obj in cell_contents)

        for agent in self.schedule.agents:
            if isinstance(agent, CollectingAgent):
                # Remove o recurso da lista de conhecidos se ele foi coletado e não está mais na grade
                if pos in agent.known_resources and not resource_present:
                    del agent.known_resources[pos]
                    print(f"{agent.name} removeu {pos} de known_resources após coleta.")

    def add_help_request(self, requester, resource):
        """Adiciona uma solicitação de ajuda à fila."""
        if not requester or not resource:
            print("Erro: `requester` ou `resource` é `None` ao adicionar solicitação de ajuda.")
            return

        request = {
            'requester': requester,
            'resource': resource,
            'assigned_agents': 0,
            'max_agents': 2
        }
        self.help_requests.append(request)
        print(f"Solicitação de ajuda adicionada para {resource.name} em {resource.pos} por {requester.name}.")

    def get_best_help_request(self):
        """Retorna a solicitação de ajuda com a maior utilidade."""
        best_utility = -1
        best_request = None
        for request in self.help_requests:
            distance = self.manhattan_distance(self.base.pos, request['resource'].pos)
            utility = 1 / (distance + 1)  # Exemplo de cálculo de utilidade
            if utility > best_utility:
                best_utility = utility
                best_request = request
        return best_request

    def remove_help_request(self, request):
        """Remove uma solicitação de ajuda da fila."""
        if request in self.help_requests:
            self.help_requests.remove(request)
            print(f"Solicitação de ajuda removida para {request['resource'].name} em {request['resource'].pos}.")

    def manhattan_distance(self, pos1, pos2):
        """Calcula a distância de Manhattan entre duas posições."""
        if pos1 is None or pos2 is None:
            return
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])