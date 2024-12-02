from Agents.AgentBase import AgentBase

class SimpleAgent(AgentBase):
    def __init__(self, unique_id, model, name="SimpleAgent"):
        super().__init__(unique_id, model)
        self.name = name
        self.color = "blue"

    def step(self):
        """Executa as ações do agente em cada passo da simulação."""
        if self.carrying is not None:
            self.move_towards(self.model.base.position)
            if self.pos == self.model.base.position:
                self.deliver_resource()
        else:
            self.random_move()
            self.collect_simple_resource()

        self.check_resources()

    def random_move(self):
        """Move-se para uma célula adjacente válida aleatória."""
        x, y = self.pos

        possible_moves = [
            (x, y - 1),
            (x, y + 1),
            (x - 1, y),
            (x + 1, y)
        ]

        valid_moves = []
        for move in possible_moves:
            new_x, new_y = move
            if 0 <= new_x < self.model.grid.width and 0 <= new_y < self.model.grid.height:
                valid_moves.append(move)

        if valid_moves:
            new_position = self.random.choice(valid_moves)
            self.model.grid.move_agent(self, new_position)

    def deliver_resource(self):
        """Entrega o recurso na base."""
        self.points += self.carrying.value
        print(f"{self.name} entregou {self.carrying.name} na base e ganhou {self.carrying.value} pontos.")
        self.carrying = None
        self.model.num_resources_delivered += 1