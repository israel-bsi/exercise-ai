from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from Captions import Captions

from ModelBase import ModelBase
from AgentPortrayal import agent_portrayal

captions = Captions()

grid = CanvasGrid(agent_portrayal, 15, 15, 600, 600)
chart = ChartModule([{"Label": "TotalPoints", "Color": "Black"}])

num_agents = {
    "SimpleAgent": 0,
    "StateAgent": 2,
    "ObjectiveAgent": 0,
    "UtilityAgent": 0,
    "BDIAgent": 1
}
num_resources ={
    "EnergeticCrystal": 5,
    "RareMetalBlock": 5,
    "AncientStructure": 5
}
grid_params = {
    "width": 15,
    "height": 15
}
model_params = {
    "num_agents": num_agents,
    "num_resources": num_resources,
    "grid_params" : grid_params
}
name = "Resource Collection Model"

server = ModularServer(ModelBase, [grid, chart, captions], name, model_params)
server.port = 8521
server.launch()