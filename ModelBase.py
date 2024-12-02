from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from Agents import *
from Resources import *

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
        self.bdi_agents = []

        self.base_position = (0, 0)
        self.base = Base(self.next_id(), self, self.base_position)
        self.grid.place_agent(self.base, self.base_position)

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
            id += 1

        for i in range(self.num_agents["BDIAgent"]):
            bdi_agent = BDIAgent(unique_id=id + 1, model=self, name=f"BDIAgent_{id + 1}")
            self.grid.place_agent(bdi_agent, self.find_random_empty_cell())
            self.schedule.add(bdi_agent)
            id += 1
            self.bdi_agents.append(bdi_agent)

        self.num_resources_delivered = 0
        resource_types = [("EnergeticCrystal", num_resources["EnergeticCrystal"]),
                          ("RareMetalBlock", num_resources["RareMetalBlock"]),
                          ("AncientStructure", num_resources["AncientStructure"])]

        for resource_type, quantity in resource_types:
            for _ in range(quantity):
                if resource_type == "EnergeticCrystal":
                    resource = EnergeticCrystal(self.resource_id, self)
                    self.num_resources_total += 1
                elif resource_type == "RareMetalBlock":
                    resource = RareMetalBlock(self.resource_id, self)
                    self.num_resources_total += 1
                elif resource_type == "AncientStructure":
                    resource = AncientStructure(self.resource_id, self)
                    self.num_resources_total += 1
                self.resource_id += 1
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.place_agent(resource, (x, y))

        print(f"Modelo inicializado com {self.num_agents} agentes e {self.num_resources_total} recursos.")

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

        #print(f"Foram entregues {self.num_resources_delivered}")
        #print(f"Deveriam ser entregues {self.num_resources_total}")

        if self.num_resources_delivered >= self.num_resources_total:
            self.running = False

            print("\nSimulação finalizada. Pontos coletados por cada agente:")
            agents_with_points = [
                agent for agent in self.schedule.agents if hasattr(agent, 'points')
            ]
            agents_with_points.sort(key=lambda agent: agent.points, reverse=True)
            for agent in agents_with_points:
                print(f"{agent.name} (ID: {agent.unique_id}): {agent.points} pontos")

            total_points = sum(agent.points for agent in agents_with_points)
            print(f"Total de pontos coletados por todos os agentes: {total_points}")

    def compute_total_points(self):
        total = sum([agent.points for agent in self.schedule.agents if hasattr(agent, 'points')])
        return total

    def next_id(self):
        self.current_id += 1
        return self.current_id