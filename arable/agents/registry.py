"""
Agent Registry for ARABLE
Manages agent discovery, registration, and lifecycle
"""

from typing import Dict, List, Type, Optional, Any
from dataclasses import dataclass
import importlib
import logging
from pathlib import Path

from .base import BaseAgent, AgentCapability


@dataclass
class AgentConfig:
    """Configuration for agent registration"""
    agent_class: Type[BaseAgent]
    name: str
    description: str
    enabled: bool = True
    config: Dict[str, Any] = None


class AgentRegistry:
    """Central registry for managing ARABLE agents"""
    
    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self.instances: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("arable.agents.registry")
        
    def register_agent(
        self, 
        agent_class: Type[BaseAgent], 
        name: str,
        description: str = "",
        enabled: bool = True,
        config: Dict[str, Any] = None
    ) -> None:
        """Register an agent class with the registry"""
        
        agent_config = AgentConfig(
            agent_class=agent_class,
            name=name,
            description=description,
            enabled=enabled,
            config=config or {}
        )
        
        self.agents[name] = agent_config
        self.logger.info(f"Registered agent: {name}")
        
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get agent instance, creating if necessary"""
        
        if agent_name not in self.agents:
            self.logger.error(f"Agent '{agent_name}' not registered")
            return None
            
        # Return existing instance
        if agent_name in self.instances:
            return self.instances[agent_name]
            
        # Create new instance
        agent_config = self.agents[agent_name]
        if not agent_config.enabled:
            self.logger.warning(f"Agent '{agent_name}' is disabled")
            return None
            
        try:
            agent_instance = agent_config.agent_class(
                agent_id=agent_name,
                config=agent_config.config
            )
            self.instances[agent_name] = agent_instance
            self.logger.info(f"Created agent instance: {agent_name}")
            return agent_instance
            
        except Exception as e:
            self.logger.error(f"Failed to create agent '{agent_name}': {e}")
            return None
            
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents and their status"""
        
        agent_list = []
        for name, config in self.agents.items():
            agent_info = {
                "name": name,
                "description": config.description,
                "enabled": config.enabled,
                "instantiated": name in self.instances,
                "status": self.instances[name].get_status() if name in self.instances else "not_created"
            }
            
            # Get capabilities if agent is instantiated
            if name in self.instances:
                agent_info["capabilities"] = [
                    cap.model_dump() for cap in self.instances[name].get_capabilities()
                ]
            
            agent_list.append(agent_info)
            
        return agent_list
        
    def shutdown_agent(self, agent_name: str) -> bool:
        """Shutdown and remove agent instance"""
        
        if agent_name in self.instances:
            agent = self.instances[agent_name]
            agent.set_status("shutting_down")
            del self.instances[agent_name]
            self.logger.info(f"Shutdown agent: {agent_name}")
            return True
            
        return False
        
    def auto_discover_agents(self, agents_dir: Path = None) -> int:
        """Auto-discover and register agents from specialized directory"""
        
        if agents_dir is None:
            agents_dir = Path(__file__).parent / "specialized"
            
        discovered_count = 0
        
        if not agents_dir.exists():
            self.logger.warning(f"Agents directory not found: {agents_dir}")
            return 0
            
        # Import all Python files in specialized directory
        for agent_file in agents_dir.glob("*.py"):
            if agent_file.name.startswith("__"):
                continue
                
            module_name = f"arable.agents.specialized.{agent_file.stem}"
            
            try:
                module = importlib.import_module(module_name)
                
                # Look for BaseAgent subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseAgent) and 
                        attr != BaseAgent):
                        
                        # Register with auto-generated info
                        agent_name = attr_name.lower().replace("agent", "")
                        self.register_agent(
                            agent_class=attr,
                            name=agent_name,
                            description=f"Auto-discovered agent from {agent_file.name}"
                        )
                        discovered_count += 1
                        
            except Exception as e:
                self.logger.error(f"Failed to discover agents in {agent_file}: {e}")
                
        self.logger.info(f"Auto-discovered {discovered_count} agents")
        return discovered_count


# Global registry instance
registry = AgentRegistry()
