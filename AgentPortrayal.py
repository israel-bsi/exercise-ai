def agent_portrayal(agent):
    color = agent.color
    shape = agent.shape
    layer = agent.layer

    portrayal = {
        "Shape": shape,
        "Color": color,
        "Filled": True,
        "Layer": layer,
        "Text_Color": "black",
        "Font_Size": 8
    }

    if shape == "circle":
        portrayal["r"] = 0.5
    elif shape == "rect":
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5

    if hasattr(agent, 'name'):
        portrayal["Text"] = agent.name
    elif hasattr(agent, 'type'):
        portrayal["Text"] = agent.type
    else:
        portrayal["Text"] = ""

    if hasattr(agent, 'carrying') and agent.carrying:
        if shape == "circle":
            portrayal["r"] = 0.8
        elif shape == "rect":
            portrayal["w"] = 0.8
            portrayal["h"] = 0.8

        portrayal["Filled"] = True

        portrayal["Text"] += " (C)"

    return portrayal