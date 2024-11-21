from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from Agents.SimpleAgent import SimpleAgent
from Agents.StateAgent import StateAgent
from Agents.UtilityAgent import  UtilityAgent
from Agents.ObjectiveAgent import ObjectiveAgent
from Agents.BDIAgent import BDIAgent
from ModelBase import ModelBase

def agent_portrayal(agent):
    if isinstance(agent, SimpleAgent):
        color = "blue"
    elif isinstance(agent, StateAgent):
        color = "green"
    elif isinstance(agent, UtilityAgent):
        color = "red"
    elif isinstance(agent, ObjectiveAgent):
        color = "yellow"
    elif isinstance(agent, BDIAgent):
        color = "purple"
    else:
        color= "gray"

    portrayal = {
        "Shape": "circle",  # Forma do agente
        "Color": color,     # Cor do agente
        "Filled": True,     # Preenchimento da forma
        "Layer": 1,         # Camada onde será desenhado
        "r": 0.5 ,          # Raio do círculo
        "Text": agent.__class__.__name__             # Texto que será exibido
    }
    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
model_params = {"N": 1, "width": 10, "height": 10}
name = "Random Walk Model"
vizualization_elements = [grid]
server = ModularServer(ModelBase, vizualization_elements, name, model_params)
server.port = 8521
server.launch()