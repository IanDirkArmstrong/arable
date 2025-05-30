"""
Base agent class for ARABLE agent system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

class AgentCapability(BaseModel):
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]

class AgentState(BaseModel):
    agent_id: str
    status: str
    memory: Dict[str, Any] = {}
    last_action: Optional[str] = None
    metrics: Dict[str, float] = {}

class BaseAgent(ABC):
    """Base class for all ARABLE agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.state = AgentState(agent_id=agent_id, status="initialized")
        self.logger = logging.getLogger(f"arable.agents.{agent_id}")
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific task"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Define what this agent can do"""
        pass
        
    def update_memory(self, key: str, value: Any):
        """Update agent memory state"""
        self.state.memory[key] = value
        
    def get_memory(self, key: str) -> Any:
        """Retrieve from agent memory"""
        return self.state.memory.get(key)
        
    def get_status(self) -> str:
        """Get current agent status"""
        return self.state.status
        
    def set_status(self, status: str):
        """Update agent status"""
        self.state.status = status
        self.logger.info(f"Agent {self.agent_id} status: {status}")
