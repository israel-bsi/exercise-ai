from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from Agents.SimpleAgent import SimpleAgent
from Agents.StateAgent import StateAgent
from Agents.UtilityAgent import  UtilityAgent
from Agents.ObjectiveAgent import ObjectiveAgent
from Agents.BDIAgent import BDIAgent

# Defina seu modelo que gerenciará os agentes
class ModelBase(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)  # True para grid toroidal
        self.schedule = RandomActivation(self)
        self.running = True  # Inicializa o atributo 'running'

        # Cria agentes de diferentes tipos
        for i in range(self.num_agents):
            # Cria um agente de cada tipo e adiciona à grade
            simple_agent = SimpleAgent(i, self)
            self.schedule.add(simple_agent)

            # state_agent = StateAgent(i + 1, self)
            # self.schedule.add(state_agent)
            #
            # utility_agent = UtilityAgent(i + 2, self)
            # self.schedule.add(utility_agent)
            #
            # objective_agent = ObjectiveAgent(i + 3, self)
            # self.schedule.add(objective_agent)
            #
            # bdi_agent = BDIAgent(i + 4, self)
            # self.schedule.add(bdi_agent)

            # Coloca os agentes nas posições da grade (aleatórias)
            x = self.random.randint(0, self.grid.width - 1)
            y = self.random.randint(0, self.grid.height - 1)
            self.grid.place_agent(simple_agent, (x, y+1))
            simple_agent.step()
            # self.grid.place_agent(state_agent, (x, y+2))
            # self.grid.place_agent(utility_agent, (x, y+3))
            # self.grid.place_agent(objective_agent, (x, y+4))
            # self.grid.place_agent(bdi_agent, (x, y+5))

    def step(self):
        """Avança um passo da simulação"""
        self.schedule.step()
