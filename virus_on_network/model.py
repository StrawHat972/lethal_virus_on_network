import math
from enum import Enum
import networkx as nx

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid
from mesa.batchrunner import BatchRunner
from datetime import date

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2
    DECEASED = 3


def number_state(model, state):
    return sum(1 for a in model.grid.get_all_cell_contents() if a.state is state)


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


def number_deceased(model):
    return number_state(model, State.DECEASED)


class VirusOnNetwork(Model):
    """A virus model with some number of agents"""

    def __init__(
        self,
        num_nodes=10,
        avg_node_degree=3,
        initial_outbreak_size=1,
        virus_spread_chance=0.4,
        recovery_chance=0.3,
        gain_resistance_chance=0.5,
        lethality=0.1,
    ):

        self.num_nodes = num_nodes
        prob = avg_node_degree / self.num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.initial_outbreak_size = (
            initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        )
        self.virus_spread_chance = virus_spread_chance
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.lethality = lethality

        self.datacollector = DataCollector(
            {
                "Infected": number_infected,
                "Susceptible": number_susceptible,
                "Resistant": number_resistant,
                "Deceased": number_deceased,
            }
        )

        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = VirusAgent(
                i,
                self,
                State.SUSCEPTIBLE,
                self.virus_spread_chance,
                self.recovery_chance,
                self.gain_resistance_chance,
                self.lethality,
            )
            self.schedule.add(a)
            # Add the agent to the node
            self.grid.place_agent(a, node)

        # Infect some nodes
        infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        for a in self.grid.get_cell_list_contents(infected_nodes):
            a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    def dead_healthy_ratio(self):
        try:
            return number_state(self, State.DECEASED) / (number_state(
                self, State.SUSCEPTIBLE) + number_state(self, State.RESISTANT))
        except ZeroDivisionError:
            return math.inf

    def resistant_susceptible_ratio(self):
        try:
            return number_state(self, State.RESISTANT) / number_state(
                self, State.SUSCEPTIBLE
            )
        except ZeroDivisionError:
            return math.inf
    
    def death_rate(self):
        return number_state(self, State.DECEASED) / self.num_nodes
    
    def susceptible_rate(self):
        return number_state(self, State.SUSCEPTIBLE) / self.num_nodes

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()


INCUBATION_PERIOD = 2
ACUTE_PERIOD = 5

class VirusAgent(Agent):
    def __init__(
        self,
        unique_id,
        model,
        initial_state,
        virus_spread_chance,
        recovery_chance,
        gain_resistance_chance,
        lethality,
    ):
        super().__init__(unique_id, model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance
        self.lethality = lethality

        # How long the agent is infected
        self.time_infected = 0

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
            if agent.state is State.SUSCEPTIBLE
        ]
        for a in susceptible_neighbors:
            if self.random.random() < self.virus_spread_chance:
                a.state = State.INFECTED

    def try_gain_resistance(self):
        if self.random.random() < self.gain_resistance_chance and self.time_infected > ACUTE_PERIOD:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if self.random.random() < self.recovery_chance and self.time_infected > INCUBATION_PERIOD:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
            self.time_infected = 0
        else:
            # Failed
            self.state = State.INFECTED

    def try_kill_agent(self):
        if self.random.random() < self.lethality and self.time_infected > INCUBATION_PERIOD:
            self.state = State.DECEASED

    def step(self):
        if self.state is State.INFECTED:
            self.time_infected += 1
            self.try_kill_agent()
            # Still alive
            if self.state is not State.DECEASED:
                self.try_remove_infection()
                self.try_to_infect_neighbors()
            

def batch_run():
    # Control variables
    fixed_params = {
        'num_nodes': 1000,
        'avg_node_degree': 8,
        'initial_outbreak_size': 1,
        'lethality': 0.1,
        'recovery_chance': 0.4,
        'gain_resistance_chance': 0.3
    }

    # Independent variables
    variable_params = {
        'virus_spread_chance': [0.25, 0.5, 1.0]
    }

    # Number of simulations to reach normal distribution
    iterations = 500
    # After 100 steps the model is stable
    max_steps = 100

    batch_run = BatchRunner(
        VirusOnNetwork,
        variable_params,
        fixed_params,
        iterations,
        max_steps,
        model_reporters={
            # Dependent variables
            'Dead Healthy Ratio': lambda m: m.dead_healthy_ratio(),
            'Death Rate': lambda m: m.death_rate(),
            'Resistant Susceptible Ratio': lambda m: m.resistant_susceptible_ratio(),
            'Susceptible Rate': lambda m: m.susceptible_rate(),
        },
        agent_reporters={
            'State': 'state'
        }
    )
    # Run Batch
    batch_run.run_all()

    # Data Collector
    batch_data_agent = batch_run.get_agent_vars_dataframe()
    batch_data_model = batch_run.get_model_vars_dataframe()

    batch_data_agent.to_csv(
        'agent_data_' + 
        str(iterations) + '_simulations_' + 
        str(max_steps) + '_steps_' + 
        str(date.today()) + '.csv'
    )

    batch_data_model.to_csv(
        'model_data_' + 
        str(iterations) + '_simulations_' + 
        str(max_steps) + '_steps_' + 
        str(date.today()) + '.csv'
    )