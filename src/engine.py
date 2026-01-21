from typing import List


class BaseAgent():
    pass


class CustomerAgent(BaseAgent):
    pass

class StaffAgent(BaseAgent):
    pass


class SimulationEngine:
    def __init__(self, config: "SimulationConfig"):
        self.config = config
        self.grid = config.grid
        self.agents = self._initialize_agents()
        self.current_step = 0
        
    def _initialize_agents(self) -> List[Agent]:
        agents = []
        for _ in range(self.config.agent_count):
            spawn_x, spawn_y = self._get_spawn()
            agent = Agent(spawn_x, spawn_y)
            agents.append(agent)
        return agents
    
    def _get_spawn(self):
        # Logic to get spawn position for an agent
        pass