"""
Agent Orchestrator for Devlar's agentic workforce.
Manages task distribution, agent coordination, and workflow optimization.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from enum import Enum

from .base_agent import BaseAgent, AgentTask, AgentResult

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class Workflow:
    """Represents a complex workflow composed of multiple tasks"""
    id: str
    name: str
    description: str
    tasks: List[AgentTask] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # task_id -> [dependency_task_ids]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentOrchestrator:
    """
    Central orchestrator for managing the agentic workforce.
    Handles task distribution, workflow management, and agent coordination.
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[AgentTask] = []
        self.workflows: Dict[str, Workflow] = {}
        self.task_history: List[AgentTask] = []
        self.logger = self._setup_logging()
        self.is_running = False
        self.max_concurrent_tasks = 10

    def _setup_logging(self) -> logging.Logger:
        """Setup orchestrator logging"""
        logger = logging.getLogger("devlar.orchestrator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - Orchestrator - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def register_agent(self, agent: BaseAgent) -> None:
        """Register a new agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the orchestrator"""
        if agent_id in self.agents:
            agent_name = self.agents[agent_id].name
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_name} ({agent_id})")

    def create_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        workflow_id: Optional[str] = None
    ) -> AgentTask:
        """Create a new task"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.task_queue)}"

        task = AgentTask(
            id=task_id,
            type=task_type,
            priority=priority.value,
            payload=payload,
            created_at=datetime.now()
        )

        if workflow_id and workflow_id in self.workflows:
            self.workflows[workflow_id].tasks.append(task)

        self.task_queue.append(task)
        self.logger.info(f"Created task: {task_id} ({task_type}) with priority {priority.name}")
        return task

    def create_workflow(
        self,
        name: str,
        description: str,
        workflow_definition: Dict[str, Any]
    ) -> Workflow:
        """Create a new workflow from definition"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            metadata=workflow_definition.get("metadata", {})
        )

        # Create tasks from workflow definition
        for task_def in workflow_definition.get("tasks", []):
            task = self.create_task(
                task_type=task_def["type"],
                payload=task_def["payload"],
                priority=TaskPriority(task_def.get("priority", 3)),
                workflow_id=workflow_id
            )
            workflow.tasks.append(task)

        # Set up dependencies
        workflow.dependencies = workflow_definition.get("dependencies", {})

        self.workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow: {name} ({workflow_id}) with {len(workflow.tasks)} tasks")
        return workflow

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow with dependency management"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.IN_PROGRESS
        workflow.started_at = datetime.now()

        self.logger.info(f"Starting workflow execution: {workflow.name}")

        try:
            # Execute tasks based on dependencies
            completed_tasks = set()
            failed_tasks = set()

            while len(completed_tasks) + len(failed_tasks) < len(workflow.tasks):
                # Find tasks ready to execute (dependencies satisfied)
                ready_tasks = []
                for task in workflow.tasks:
                    if (task.id not in completed_tasks and
                        task.id not in failed_tasks and
                        task.status == "pending"):

                        dependencies = workflow.dependencies.get(task.id, [])
                        if all(dep_id in completed_tasks for dep_id in dependencies):
                            ready_tasks.append(task)

                if not ready_tasks:
                    # Check if we're stuck due to failed dependencies
                    remaining_tasks = [t for t in workflow.tasks if t.id not in completed_tasks and t.id not in failed_tasks]
                    if remaining_tasks:
                        self.logger.error("Workflow stuck - remaining tasks have unsatisfied dependencies")
                        workflow.status = WorkflowStatus.FAILED
                        break
                    else:
                        break

                # Execute ready tasks concurrently
                task_results = await asyncio.gather(
                    *[self._assign_and_execute_task(task) for task in ready_tasks],
                    return_exceptions=True
                )

                for task, result in zip(ready_tasks, task_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Task {task.id} failed with exception: {result}")
                        failed_tasks.add(task.id)
                    elif isinstance(result, AgentResult):
                        if result.success:
                            completed_tasks.add(task.id)
                        else:
                            failed_tasks.add(task.id)

            # Determine final workflow status
            if failed_tasks:
                workflow.status = WorkflowStatus.FAILED if len(failed_tasks) > len(completed_tasks) else WorkflowStatus.COMPLETED
            else:
                workflow.status = WorkflowStatus.COMPLETED

            workflow.completed_at = datetime.now()
            execution_time = (workflow.completed_at - workflow.started_at).total_seconds()

            result = {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "execution_time_seconds": execution_time,
                "tasks_completed": len(completed_tasks),
                "tasks_failed": len(failed_tasks),
                "total_tasks": len(workflow.tasks)
            }

            self.logger.info(f"Workflow {workflow.name} completed: {result}")
            return result

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            self.logger.error(f"Workflow {workflow.name} failed: {str(e)}")
            raise

    async def _assign_and_execute_task(self, task: AgentTask) -> AgentResult:
        """Assign task to best available agent and execute it"""
        # Find best agent for the task
        suitable_agents = [
            agent for agent in self.agents.values()
            if agent.can_handle_task(task.type) and agent.status == "idle"
        ]

        if not suitable_agents:
            # No suitable agents available
            raise Exception(f"No available agents can handle task type: {task.type}")

        # Select best agent (for now, just pick the first available)
        # TODO: Implement more sophisticated agent selection based on workload, performance, etc.
        selected_agent = suitable_agents[0]

        # Execute the task
        result = await selected_agent.process_task(task)
        self.task_history.append(task)

        return result

    async def start_orchestrator(self) -> None:
        """Start the orchestrator main loop"""
        self.is_running = True
        self.logger.info("Agent orchestrator started")

        while self.is_running:
            try:
                # Process pending tasks
                await self._process_task_queue()

                # Health check agents
                await self._health_check_agents()

                # Clean up completed workflows
                self._cleanup_old_workflows()

                # Wait before next iteration
                await asyncio.sleep(5)

            except Exception as e:
                self.logger.error(f"Error in orchestrator main loop: {str(e)}")
                await asyncio.sleep(10)

    async def stop_orchestrator(self) -> None:
        """Stop the orchestrator"""
        self.is_running = False
        self.logger.info("Agent orchestrator stopped")

    async def _process_task_queue(self) -> None:
        """Process tasks in the queue"""
        if not self.task_queue:
            return

        # Get active tasks count
        active_tasks = sum(1 for agent in self.agents.values() if agent.status == "busy")

        if active_tasks >= self.max_concurrent_tasks:
            return

        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority)

        # Process high-priority tasks
        tasks_to_process = self.task_queue[:self.max_concurrent_tasks - active_tasks]

        for task in tasks_to_process:
            try:
                await self._assign_and_execute_task(task)
                self.task_queue.remove(task)
            except Exception as e:
                self.logger.error(f"Failed to process task {task.id}: {str(e)}")
                # Move failed task to end of queue with lower priority
                task.priority = min(task.priority + 1, 5)

    async def _health_check_agents(self) -> None:
        """Perform health checks on all registered agents"""
        for agent in self.agents.values():
            try:
                is_healthy = await agent.health_check()
                if not is_healthy:
                    self.logger.warning(f"Agent {agent.name} failed health check")
            except Exception as e:
                self.logger.error(f"Health check failed for agent {agent.name}: {str(e)}")

    def _cleanup_old_workflows(self) -> None:
        """Clean up workflows older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)
        workflows_to_remove = [
            wf_id for wf_id, workflow in self.workflows.items()
            if workflow.completed_at and workflow.completed_at < cutoff_date
        ]

        for wf_id in workflows_to_remove:
            del self.workflows[wf_id]

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get current orchestrator status and metrics"""
        active_workflows = len([wf for wf in self.workflows.values() if wf.status == WorkflowStatus.IN_PROGRESS])
        completed_workflows = len([wf for wf in self.workflows.values() if wf.status == WorkflowStatus.COMPLETED])
        failed_workflows = len([wf for wf in self.workflows.values() if wf.status == WorkflowStatus.FAILED])

        return {
            "status": "running" if self.is_running else "stopped",
            "registered_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() if a.status != "offline"]),
            "pending_tasks": len(self.task_queue),
            "total_tasks_processed": len(self.task_history),
            "active_workflows": active_workflows,
            "completed_workflows": completed_workflows,
            "failed_workflows": failed_workflows,
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()}
        }

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        completed_tasks = len([t for t in workflow.tasks if t.status == "completed"])
        failed_tasks = len([t for t in workflow.tasks if t.status == "failed"])

        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "total_tasks": len(workflow.tasks),
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "progress_percentage": (completed_tasks / len(workflow.tasks)) * 100 if workflow.tasks else 0
        }