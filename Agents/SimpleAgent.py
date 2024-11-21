from mesa import Agent
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation

class SimpleAgentModel(Model):
    def __init__(self, N, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = SimultaneousActivation(self)
        self.running = True  # Inicializa o atributo 'running'

        # Cria agentes
        for i in range(self.num_agents):
            agent = SimpleAgent(i, self)
            self.schedule.add(agent)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def step(self):
        self.schedule.step()
        if self.schedule.steps > 100:  # Condição para parar a simulação
            self.running = False
        self.check_collision()

    def check_collision(self):
        print("Checking collisions")
        for agent1 in self.schedule.agents:
            for agent2 in self.schedule.agents:
                if agent1 != agent2:
                    if agent1.pos == agent2.pos:
                        self.grid.remove_agent(agent1)
                        self.schedule.remove(agent1)
                        print("Agent removed")

class SimpleAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        """Move o agente para uma celula adjacente(para cima, para baixo, para a esquerda ou para a direita)"""
        x, y = self.pos

        # Definir possiveis direções de movimento:
        possible_moves = [
            (x, y-1),  # Cima
            (x, y+1),  # Baixo
            (x-1, y),  # Esquerda
            (x+1, y)   # Direita
        ]

        valid_moves = []
        for move in possible_moves:
            new_x, new_y = move
            if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
                valid_moves.append(move)

        if valid_moves:
            new_position = self.random.choice(valid_moves)
            self.model.grid.move_agent(self, new_position)