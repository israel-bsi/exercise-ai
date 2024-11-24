from collections import deque

from Agents.AgenteBase import AgentBase

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

    def request_help(self, resource):
        """Solicita ajuda de UtilityAgents para coletar um recurso grande."""
        # Itera sobre os UtilityAgents disponíveis
        for agent in self.model.available_utility_agents.copy():  # Usar copy para evitar erros durante iteração
            if agent != self and not agent.carrying:
                agent.receive_help_request(self, resource)
                print(f"{self.name} solicitou ajuda de {agent.name} para coletar {resource.type} em {resource.pos}.")

    def plan_path(self, start_pos, goal_pos):
        """Planeja um caminho do ponto de partida até o ponto de destino usando BFS."""
        grid_width = self.model.grid.width
        grid_height = self.model.grid.height
        visited = set()
        queue = deque([start_pos])
        came_from = {}

        visited.add(start_pos)

        while queue:
            current = queue.popleft()
            if current == goal_pos:
                # Reconstruir o caminho
                path = []
                while current != start_pos:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            neighbors = self.model.grid.get_neighborhood(current, moore=False, include_center=False)
            for neighbor in neighbors:
                if neighbor not in visited and 0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
        return []  # Se não encontrar um caminho