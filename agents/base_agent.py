"""
Base Agent class for Devlar's agentic workforce.
Provides core functionality and interface for all specialized agents.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class AgentResult:
    """Standard result format for all agent operations"""
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: datetime
    agent_id: str

    def to_json(self) -> str:
        """Convert result to JSON string"""
        result_dict = asdict(self)
        result_dict['timestamp'] = self.timestamp.isoformat()
        return json.dumps(result_dict, indent=2)

@dataclass
class AgentTask:
    """Standard task format for agent operations"""
    id: str
    type: str
    priority: int  # 1-5, where 1 is highest priority
    payload: Dict[str, Any]
    created_at: datetime
    assigned_to: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed

class BaseAgent(ABC):
    """
    Base class for all Devlar agents.
    Implements core functionality including logging, task management, and communication.
    """

    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = "idle"  # idle, busy, error, offline
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup agent-specific logging"""
        logger = logging.getLogger(f"devlar.agent.{self.agent_id}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @abstractmethod
    async def execute_task(self, task: AgentTask) -> AgentResult:
        """
        Execute a specific task. Must be implemented by each agent type.

        Args:
            task: The task to execute

        Returns:
            AgentResult with execution details
        """
        pass

    async def process_task(self, task: AgentTask) -> AgentResult:
        """
        Process a task with error handling and status management.

        Args:
            task: The task to process

        Returns:
            AgentResult with execution details
        """
        self.logger.info(f"Starting task {task.id}: {task.type}")
        self.status = "busy"
        self.current_task = task
        task.status = "in_progress"
        task.assigned_to = self.agent_id

        try:
            result = await self.execute_task(task)
            task.status = "completed" if result.success else "failed"
            self.task_history.append(task)
            self.logger.info(f"Task {task.id} {'completed' if result.success else 'failed'}: {result.message}")

        except Exception as e:
            self.logger.error(f"Task {task.id} failed with exception: {str(e)}")
            result = AgentResult(
                success=False,
                data={},
                message=f"Task failed with exception: {str(e)}",
                timestamp=datetime.now(),
                agent_id=self.agent_id
            )
            task.status = "failed"
            self.task_history.append(task)

        finally:
            self.status = "idle"
            self.current_task = None

        return result

    def can_handle_task(self, task_type: str) -> bool:
        """
        Check if this agent can handle a specific task type.

        Args:
            task_type: The type of task to check

        Returns:
            True if agent can handle the task, False otherwise
        """
        return task_type in self.capabilities

    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and metrics.

        Returns:
            Dictionary with agent status information
        """
        completed_tasks = len([t for t in self.task_history if t.status == "completed"])
        failed_tasks = len([t for t in self.task_history if t.status == "failed"])

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities,
            "current_task": self.current_task.id if self.current_task else None,
            "tasks_completed": completed_tasks,
            "tasks_failed": failed_tasks,
            "success_rate": completed_tasks / (completed_tasks + failed_tasks) if (completed_tasks + failed_tasks) > 0 else 0,
            "last_active": self.task_history[-1].created_at.isoformat() if self.task_history else None
        }

    async def health_check(self) -> bool:
        """
        Perform a health check on the agent.

        Returns:
            True if agent is healthy, False otherwise
        """
        try:
            # Basic health check - can be overridden by specific agents
            return self.status != "error"
        except Exception:
            return False