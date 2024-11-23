from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

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

        # Inicializar a base
        self.base_position = (0, 0)
        self.base = Base(self.next_id(), self, self.base_position)
        self.grid.place_agent(self.base, self.base_position)

        # Inicializar o BDI Agent
        id = 0
        for i in range(self.num_agents["SimpleAgent"]):
            agent = SimpleAgent(unique_id=id + 1, model=self, name=f"SimpleAgent_{id + 1}")
            self.grid.place_agent(agent, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["StateAgent"]):
            agent = StateAgent(unique_id=id + 1, model=self, name=f"StateAgent_{id + 1}")
            self.grid.place_agent(agent, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["ObjectiveAgent"]):
            agent = ObjectiveAgent(unique_id=id + 1, model=self, name=f"ObjectiveAgent_{id + 1}")
            self.grid.place_agent(agent, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["UtilityAgent"]):
            agent = UtilityAgent(unique_id=id + 1, model=self, name=f"UtilityAgent_{id + 1}")
            self.grid.place_agent(agent, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))
            self.schedule.add(agent)
            id += 1

        for i in range(self.num_agents["BDIAgent"]):
            bdi_agent = BDIAgent(unique_id=id + 1, model=self, name=f"BDIAgent_{id + 1}")
            self.grid.place_agent(bdi_agent,(self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))
            self.schedule.add(bdi_agent)
            id += 1

        # Criar recursos
        self.resource_id = 1000

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
        for agent in self.schedule.agents:
            if hasattr(agent, 'known_resources') and pos in agent.known_resources:
                del agent.known_resources[pos]
                print(f"{agent.name} removeu {pos} de known_resources.")

        # Remover de todas as solicitações
        for agent in self.schedule.agents:
            if hasattr(agent, 'requests') and isinstance(agent.requests, dict):
                keys_to_remove = [key for key, req in agent.requests.items() if req['resource'].pos == pos]
                for key in keys_to_remove:
                    del agent.requests[key]
                    print(f"{agent.name} removeu a solicitação de {key} relacionada ao recurso em {pos}.")
