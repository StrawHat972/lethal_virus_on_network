import math

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement
from .model import VirusOnNetwork, State, number_infected


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        return {State.INFECTED: "#FF0000", State.SUSCEPTIBLE: "#008000", State.DECEASED: "#3D0154"}.get(
            agent.state, "#1399F3"
        )

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": "#e8e8e8",
            "width": 2,
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = NetworkModule(network_portrayal, 500, 500, library="d3")
chart = ChartModule(
    [
        {"Label": "Infected", "Color": "#FF0000"},
        {"Label": "Susceptible", "Color": "#008000"},
        {"Label": "Resistant", "Color": "#1399F3"},
        {"Label": "Deceased", "Color": "#3D0154"},
    ]
)


class MyTextElement(TextElement):
    def render(self, model):
        dead_healthy = model.dead_healthy_ratio()
        dead_healthy_text =  "&infin;" if dead_healthy is math.inf else f"{dead_healthy:.2f}"
        death_rate = f"{model.death_rate():.2f}"
        susceptible_rate = f"{model.susceptible_rate():.2f}"
        resistant = model.resistant_susceptible_ratio()
        resistant_text = "&infin;" if resistant is math.inf else f"{resistant:.2f}"
        infected_text = str(number_infected(model))

        textOnScree = "Dead/Healthy Ratio: {}<br>"
        textOnScree += "Death Rate: {}<br>"
        textOnScree += "Resistant/Susceptible Ratio: {}<br>"
        textOnScree += "Susceptible Rate: {}<br>"
        textOnScree += "Infected Remaining: {}"

        return textOnScree.format(
            dead_healthy_text, death_rate, resistant_text, susceptible_rate, infected_text
        )


model_params = {
    "num_nodes": UserSettableParameter(
        "slider",
        "Number of agents",
        10,
        10,
        100,
        1,
        description="Choose how many agents to include in the model",
    ),
    "avg_node_degree": UserSettableParameter(
        "slider", "Avg Node Degree", 3, 3, 8, 1, description="Avg Node Degree"
    ),
    "initial_outbreak_size": UserSettableParameter(
        "slider",
        "Initial Outbreak Size",
        1,
        1,
        10,
        1,
        description="Initial Outbreak Size",
    ),
    "virus_spread_chance": UserSettableParameter(
        "slider",
        "Virus Spread Chance",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Probability that susceptible neighbor will be infected",
    ),
    "recovery_chance": UserSettableParameter(
        "slider",
        "Recovery Chance",
        0.3,
        0.0,
        1.0,
        0.1,
        description="Probability that the virus will be removed",
    ),
    "gain_resistance_chance": UserSettableParameter(
        "slider",
        "Gain Resistance Chance",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Probability that a recovered agent will become "
        "resistant to this virus in the future",
    ),
    "lethality": UserSettableParameter(
        "slider",
        "Lethality",
        0.1,
        0.0,
        1.0,
        0.05,
        description="Probability that an infected agent dies due to virus",
    )
}

server = ModularServer(
    VirusOnNetwork, [network, MyTextElement(), chart], "Virus Model", model_params
)
server.port = 8521
