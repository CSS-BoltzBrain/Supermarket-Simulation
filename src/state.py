from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class StateMap:
    pass


@dataclass
class AgentMap:
    """
    Update the location of agents on the map.
    """
    def __init__(self, agent_map):
        self.agent_map = agent_map

    def _potential_deadlock_detection(self) -> bool:
        """Detect potential deadlocks in the agent map."""
        return False

    def _write_agent_map(self) -> None:
        """Write/replace the agent map."""
        # if potential deadlock detected, update slightly differently
        if self._potential_deadlock_detection():
            pass
        else:
            pass
    
    def update(self) -> None:
        """Update the agent map with arbitrary keyword arguments."""
        self._write_agent_map()
