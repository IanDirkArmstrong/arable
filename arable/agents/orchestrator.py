"""
Agent Orchestrator for ARABLE
Coordinates multi-agent workflows and task execution
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import json

from .registry import registry
from .base import BaseAgent
from .memory import memory_manager


@dataclass
class WorkflowTask:
    """Individual task in a workflow"""
    task_id: str
    agent_name: str
    task_data: Dict[str, Any]
    dependencies: List[str] = None  # List of task_ids that must complete first
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error: str = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass 
class Workflow:
    """Multi-agent workflow definition"""
    workflow_id: str
    name: str
    description: str
    tasks: List[WorkflowTask]
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None


class AgentOrchestrator:
    """Orchestrates multi-agent workflows and task execution"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.logger = logging.getLogger("arable.agents.orchestrator")
        self._task_callbacks: Dict[str, List[Callable]] = {}
        
    async def execute_single_task(
        self, 
        agent_name: str, 
        task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single task with an agent"""
        
        # Get agent from registry
        agent = registry.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found or disabled")
            
        self.logger.info(f"Executing task with agent '{agent_name}'")
        
        try:
            agent.set_status("running")
            result = await agent.execute(task_data)
            agent.set_status("idle")
            
            self.logger.info(f"Task completed successfully with agent '{agent_name}'")
            return {
                "success": True,
                "agent": agent_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            agent.set_status("error")
            self.logger.error(f"Task failed with agent '{agent_name}': {e}")
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def create_workflow(
        self, 
        workflow_id: str, 
        name: str, 
        description: str = ""
    ) -> Workflow:
        """Create a new workflow"""
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            tasks=[],
            created_at=datetime.now()
        )
        
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow: {name} ({workflow_id})")
        return workflow
        
    def add_task_to_workflow(
        self,
        workflow_id: str,
        task_id: str,
        agent_name: str,
        task_data: Dict[str, Any],
        dependencies: List[str] = None
    ) -> bool:
        """Add a task to an existing workflow"""
        
        if workflow_id not in self.workflows:
            self.logger.error(f"Workflow '{workflow_id}' not found")
            return False
            
        # Verify agent exists
        if not registry.get_agent(agent_name):
            self.logger.error(f"Agent '{agent_name}' not available")
            return False
            
        task = WorkflowTask(
            task_id=task_id,
            agent_name=agent_name,
            task_data=task_data,
            dependencies=dependencies or []
        )
        
        self.workflows[workflow_id].tasks.append(task)
        self.logger.info(f"Added task '{task_id}' to workflow '{workflow_id}'")
        return True
        
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a complete workflow with dependency management"""
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
            
        workflow = self.workflows[workflow_id]
        workflow.status = "running"
        
        self.logger.info(f"Starting workflow execution: {workflow.name}")
        
        # Track task completion
        completed_tasks = set()
        task_results = {}
        
        try:
            # Execute tasks respecting dependencies
            while len(completed_tasks) < len(workflow.tasks):
                # Find tasks ready to execute
                ready_tasks = []
                
                for task in workflow.tasks:
                    if (task.status == "pending" and 
                        all(dep in completed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # Check for circular dependencies or blocked workflow
                    pending_tasks = [t for t in workflow.tasks if t.status == "pending"]
                    if pending_tasks:
                        raise RuntimeError("Workflow blocked - possible circular dependencies")
                    break
                    
                # Execute ready tasks concurrently
                task_futures = []
                for task in ready_tasks:
                    task.status = "running"
                    task.started_at = datetime.now()
                    
                    # Create execution future
                    future = self._execute_workflow_task(task, task_results)
                    task_futures.append((task, future))
                    
                # Wait for tasks to complete
                for task, future in task_futures:
                    try:
                        result = await future
                        task.status = "completed"
                        task.result = result
                        task.completed_at = datetime.now()
                        completed_tasks.add(task.task_id)
                        task_results[task.task_id] = result
                        
                        self.logger.info(f"Task '{task.task_id}' completed successfully")
                        
                    except Exception as e:
                        task.status = "failed"
                        task.error = str(e)
                        task.completed_at = datetime.now()
                        
                        self.logger.error(f"Task '{task.task_id}' failed: {e}")
                        
                        # For now, continue with other tasks
                        # In future, could add failure handling strategies
                        
            workflow.status = "completed"
            workflow.completed_at = datetime.now()
            
            # Calculate workflow summary
            total_tasks = len(workflow.tasks)
            successful_tasks = len([t for t in workflow.tasks if t.status == "completed"])
            failed_tasks = len([t for t in workflow.tasks if t.status == "failed"])
            
            self.logger.info(
                f"Workflow '{workflow.name}' completed: "
                f"{successful_tasks}/{total_tasks} tasks successful"
            )
            
            return {
                "workflow_id": workflow_id,
                "success": failed_tasks == 0,
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks, 
                "failed_tasks": failed_tasks,
                "task_results": task_results,
                "execution_time": (workflow.completed_at - workflow.created_at).total_seconds()
            }
            
        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.now()
            
            self.logger.error(f"Workflow '{workflow.name}' failed: {e}")
            raise
            
    async def _execute_workflow_task(
        self, 
        task: WorkflowTask, 
        previous_results: Dict[str, Any]
    ) -> Any:
        """Execute a single workflow task with access to previous results"""
        
        # Enhance task data with results from dependency tasks
        enhanced_task_data = task.task_data.copy()
        enhanced_task_data["previous_results"] = {
            dep_id: previous_results.get(dep_id) 
            for dep_id in task.dependencies
        }
        
        # Execute with agent
        result = await self.execute_single_task(task.agent_name, enhanced_task_data)
        
        # Store workflow result in memory for inter-agent access
        await memory_manager.store_workflow_result(
            workflow_id="workflow_" + task.task_id,  # Use task-specific workflow ID
            agent_id=task.agent_name,
            task_id=task.task_id,
            result=result
        )
        
        # Trigger any registered callbacks
        await self._trigger_task_callbacks(task.task_id, result)
        
        return result
        
    def register_task_callback(
        self, 
        task_id: str, 
        callback: Callable[[Any], None]
    ) -> None:
        """Register callback for task completion"""
        
        if task_id not in self._task_callbacks:
            self._task_callbacks[task_id] = []
        self._task_callbacks[task_id].append(callback)
        
    async def _trigger_task_callbacks(self, task_id: str, result: Any) -> None:
        """Trigger registered callbacks for task completion"""
        
        if task_id in self._task_callbacks:
            for callback in self._task_callbacks[task_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(result)
                    else:
                        callback(result)
                except Exception as e:
                    self.logger.error(f"Task callback failed for '{task_id}': {e}")
                    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current status of a workflow"""
        
        if workflow_id not in self.workflows:
            return {"error": f"Workflow '{workflow_id}' not found"}
            
        workflow = self.workflows[workflow_id]
        
        task_summary = {}
        for status in ["pending", "running", "completed", "failed"]:
            task_summary[status] = len([t for t in workflow.tasks if t.status == status])
            
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat(),
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "task_summary": task_summary,
            "tasks": [
                {
                    "task_id": task.task_id,
                    "agent_name": task.agent_name,
                    "status": task.status,
                    "dependencies": task.dependencies,
                    "error": task.error
                }
                for task in workflow.tasks
            ]
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
