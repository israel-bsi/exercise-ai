def agent_portrayal(agent):
    color = agent.color
    shape = agent.shape
    layer = agent.layer

    # Definir as dimensões e propriedades visuais
    portrayal = {
        "Shape": shape,
        "Color": color,
        "Filled": True,
        "Layer": layer,
        "Text_Color": "black",
        "Font_Size": 8
    }

    # Ajustar tamanho de acordo com a forma
    if shape == "circle":
        portrayal["r"] = 0.5  # Raio para círculos
    elif shape == "rect":
        portrayal["w"] = 0.5  # Largura para retângulos
        portrayal["h"] = 0.5  # Altura para retângulos

    # Definir o texto a ser exibido
    if hasattr(agent, 'name'):
        portrayal["Text"] = agent.name
    elif hasattr(agent, 'type'):
        portrayal["Text"] = agent.type
    else:
        portrayal["Text"] = ""

    # Ajustes específicos para agentes carregando recursos
    if hasattr(agent, 'carrying') and agent.carrying:
        if shape == "circle":
            portrayal["r"] = 0.8
        elif shape == "rect":
            portrayal["w"] = 0.8
            portrayal["h"] = 0.8

        # Manter o preenchimento
        portrayal["Filled"] = True

        portrayal["Text"] += " (C)"

    return portrayal