from mesa.visualization.modules import TextElement

class Captions(TextElement):
    def render(self, model):
        return """
        <div style="position: absolute; top: 10px; left: 620px; width: 200px; background-color: white; border: 1px solid black; padding: 10px;">
            <h3>Captions</h3>
            <ul style="list-style: none; padding: 0;">
                <li><span style="display:inline-block;width:12px;height:12px;background-color:blue;margin-right:5px;border-radius:50%"></span> SimpleAgent</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:green;margin-right:5px;border-radius:50%"></span> StateAgent</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:red;margin-right:5px;border-radius:50%"></span> UtilityAgent</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:yellow;margin-right:5px;border-radius:50%"></span> ObjectiveAgent</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:purple;margin-right:5px;border-radius:50%"></span> BDIAgent</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:brown;margin-right:5px;"></span> Base</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:cyan;margin-right:5px;"></span> EnergeticCrystal</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:silver;margin-right:5px;"></span> RareMetalBlock</li>
                <li><span style="display:inline-block;width:12px;height:12px;background-color:gold;margin-right:5px;"></span> AncientStructure</li>
            </ul>
        </div>
        """
