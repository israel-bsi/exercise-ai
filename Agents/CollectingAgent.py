from collections import deque

from Agents.AgentBase import AgentBase

class CollectingAgent(AgentBase):
    def __init__(self, unique_id, model, name="CollectingAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.carrying = None
        self.points = 0
        self.target_resource = None
        self.path = []
        self.requests = {}
        self.type = "Agent"
        self.shape = "circle"
        self.layer = 1
        self.known_resources = {}
        self.partner = None
        self.known_agents = {}
        self.visited_positions = set()
#
#     def plan_path(self, start_pos, goal_pos):
#         """Planeja um caminho do ponto de partida até o ponto de destino usando BFS."""
#         grid_width = self.model.grid.width
#         grid_height = self.model.grid.height
#         visited = set()
#         queue = deque([start_pos])
#         came_from = {}
#
#         visited.add(start_pos)
#
#         while queue:
#             current = queue.popleft()
#             if current == goal_pos:
#                 # Reconstruir o caminho
#                 path = []
#                 while current != start_pos:
#                     path.append(current)
#                     current = came_from[current]
#                 path.reverse()
#                 return path
#             neighbors = self.model.grid.get_neighborhood(current, moore=False, include_center=False)
#             for neighbor in neighbors:
#                 if neighbor not in visited and 0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height:
#                     visited.add(neighbor)
#                     came_from[neighbor] = current
#                     queue.append(neighbor)
#         return []  # Se não encontrar um caminho
#
#     def random_move(self):
#         """Move-se para uma célula aleatória não visitada. Se não houver, move-se para qualquer célula adjacente válida."""
#         possible_steps = self.model.grid.get_neighborhood(
#             self.pos,
#             moore=False,  # Sem movimento diagonal
#             include_center=False
#         )
#
#         # Filtrar células adjacentes não visitadas
#         unvisited_steps = [
#             pos for pos in possible_steps
#             if pos not in self.visited_positions and
#                0 <= pos[0] < self.model.grid.width and
#                0 <= pos[1] < self.model.grid.height
#         ]
#
#         if unvisited_steps:
#             # Se houver células não visitadas, mover-se para uma delas
#             new_position = self.random.choice(unvisited_steps)
#             self.model.grid.move_agent(self, new_position)
#             #print(f"{self.name} move para {new_position} aleatoriamente (não visitada).")
#         else:
#             # Se não houver células não visitadas, permitir mover-se para qualquer célula adjacente válida
#             valid_steps = [
#                 pos for pos in possible_steps
#                 if 0 <= pos[0] < self.model.grid.width and
#                    0 <= pos[1] < self.model.grid.height
#             ]
#
#             if valid_steps:
#                 new_position = self.random.choice(valid_steps)
#                 self.model.grid.move_agent(self, new_position)
#                 #print(f"{self.name} move para {new_position} aleatoriamente (já visitada).")
#             else:
#                 # Se não houver células adjacentes válidas (muito raro em grades conectadas), o agente fica parado
#                 print(f"{self.name} não encontrou passos válidos para mover.")
#
#     def move_toward(self, destination=None):
#         """Move-se em direção a um destino (recurso, base ou qualquer posição). Se não houver, move-se aleatoriamente."""
#         # Se não houver destino, mover aleatoriamente
#         if destination is None:
#             self.random_move()
#             return
#
#         # Obter coordenadas do destino
#         dest_x, dest_y = destination
#         current_x, current_y = self.pos
#
#         # Calcular a direção para mover
#         dx = dest_x - current_x
#         dy = dest_y - current_y
#
#         # Determinar o próximo passo em x
#         move_x = current_x + (1 if dx > 0 else -1 if dx < 0 else 0)
#         # Determinar o próximo passo em y
#         move_y = current_y + (1 if dy > 0 else -1 if dy < 0 else 0)
#
#         # Verificar se a nova posição é válida
#         if 0 <= move_x < self.model.grid.width and 0 <= move_y < self.model.grid.height:
#             new_position = (move_x, move_y)
#         else:
#             # Se a posição não for válida, manter posição atual
#             new_position = self.pos
#
#         self.model.grid.move_agent(self, new_position)
#         # print(f"{self.name} move para {new_position} em direção ao destino {destination}.")