"""
Tests for the agent orchestrator functionality.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from agents.orchestrator import AgentOrchestrator, TaskPriority, WorkflowStatus
from agents.base_agent import BaseAgent, AgentTask, AgentResult

class MockAgent(BaseAgent):
    """Mock agent for testing orchestrator functionality"""

    def __init__(self, agent_id: str, capabilities: list):
        super().__init__(agent_id, f"Mock Agent {agent_id}", capabilities)
        self.execution_delay = 0.1

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Mock task execution with configurable delay"""
        await asyncio.sleep(self.execution_delay)

        if task.payload.get("should_fail", False):
            return AgentResult(
                success=False,
                data={},
                message="Mock task failed",
                timestamp=datetime.now(),
                agent_id=self.agent_id
            )

        return AgentResult(
            success=True,
            data={"mock_result": f"completed by {self.agent_id}"},
            message="Mock task completed successfully",
            timestamp=datetime.now(),
            agent_id=self.agent_id
        )

@pytest.fixture
def orchestrator():
    """Fixture providing a fresh orchestrator instance"""
    return AgentOrchestrator()

@pytest.fixture
def mock_agents():
    """Fixture providing mock agents"""
    return [
        MockAgent("agent_001", ["task_a", "task_b"]),
        MockAgent("agent_002", ["task_b", "task_c"]),
        MockAgent("agent_003", ["task_c", "task_d"])
    ]

class TestAgentOrchestrator:
    """Test cases for agent orchestrator functionality"""

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert len(orchestrator.agents) == 0
        assert len(orchestrator.task_queue) == 0
        assert len(orchestrator.workflows) == 0
        assert orchestrator.is_running is False

    def test_agent_registration(self, orchestrator, mock_agents):
        """Test agent registration and unregistration"""
        # Register agents
        for agent in mock_agents:
            orchestrator.register_agent(agent)

        assert len(orchestrator.agents) == 3
        assert "agent_001" in orchestrator.agents
        assert "agent_002" in orchestrator.agents

        # Unregister agent
        orchestrator.unregister_agent("agent_001")
        assert len(orchestrator.agents) == 2
        assert "agent_001" not in orchestrator.agents

    def test_task_creation(self, orchestrator):
        """Test task creation"""
        task = orchestrator.create_task(
            task_type="test_task",
            payload={"test": "data"},
            priority=TaskPriority.HIGH
        )

        assert task.type == "test_task"
        assert task.priority == 2  # HIGH priority value
        assert task.payload["test"] == "data"
        assert len(orchestrator.task_queue) == 1

    def test_workflow_creation(self, orchestrator):
        """Test workflow creation"""
        workflow_definition = {
            "tasks": [
                {"type": "task_a", "payload": {"step": 1}, "priority": 2},
                {"type": "task_b", "payload": {"step": 2}, "priority": 2}
            ],
            "dependencies": {
                "task_2": ["task_1"]
            },
            "metadata": {"project": "test"}
        }

        workflow = orchestrator.create_workflow(
            name="Test Workflow",
            description="A test workflow",
            workflow_definition=workflow_definition
        )

        assert workflow.name == "Test Workflow"
        assert len(workflow.tasks) == 2
        assert workflow.status == WorkflowStatus.PENDING
        assert len(orchestrator.workflows) == 1

    @pytest.mark.asyncio
    async def test_single_task_execution(self, orchestrator, mock_agents):
        """Test single task assignment and execution"""
        orchestrator.register_agent(mock_agents[0])

        task = AgentTask(
            id="single_task",
            type="task_a",
            priority=2,
            payload={"test": "data"},
            created_at=datetime.now()
        )

        result = await orchestrator._assign_and_execute_task(task)

        assert result.success is True
        assert result.agent_id == "agent_001"
        assert task.status == "completed"

    @pytest.mark.asyncio
    async def test_task_assignment_no_suitable_agent(self, orchestrator, mock_agents):
        """Test task assignment when no suitable agent is available"""
        orchestrator.register_agent(mock_agents[0])  # Only handles task_a, task_b

        task = AgentTask(
            id="unhandled_task",
            type="task_z",  # No agent can handle this
            priority=2,
            payload={},
            created_at=datetime.now()
        )

        with pytest.raises(Exception) as exc_info:
            await orchestrator._assign_and_execute_task(task)

        assert "No available agents" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self, orchestrator, mock_agents):
        """Test simple workflow execution without dependencies"""
        # Register agents
        for agent in mock_agents:
            orchestrator.register_agent(agent)

        workflow_definition = {
            "tasks": [
                {"type": "task_a", "payload": {"step": 1}, "priority": 2},
                {"type": "task_b", "payload": {"step": 2}, "priority": 2}
            ],
            "dependencies": {},
            "metadata": {"project": "simple_test"}
        }

        workflow = orchestrator.create_workflow(
            name="Simple Test Workflow",
            description="A simple test workflow",
            workflow_definition=workflow_definition
        )

        result = await orchestrator.execute_workflow(workflow.id)

        assert result["status"] == WorkflowStatus.COMPLETED.value
        assert result["tasks_completed"] == 2
        assert result["tasks_failed"] == 0

    @pytest.mark.asyncio
    async def test_workflow_with_dependencies(self, orchestrator, mock_agents):
        """Test workflow execution with task dependencies"""
        # Register agents
        for agent in mock_agents:
            orchestrator.register_agent(agent)

        # Create workflow with dependencies
        workflow = orchestrator.create_workflow(
            name="Dependent Workflow",
            description="Workflow with task dependencies",
            workflow_definition={
                "tasks": [
                    {"type": "task_a", "payload": {"step": 1}, "priority": 2},
                    {"type": "task_b", "payload": {"step": 2}, "priority": 2},
                    {"type": "task_c", "payload": {"step": 3}, "priority": 2}
                ],
                "dependencies": {},  # Will be set manually
                "metadata": {}
            }
        )

        # Set up dependencies manually (task_b depends on task_a, task_c depends on task_b)
        task_ids = [task.id for task in workflow.tasks]
        workflow.dependencies = {
            task_ids[1]: [task_ids[0]],  # task_b depends on task_a
            task_ids[2]: [task_ids[1]]   # task_c depends on task_b
        }

        result = await orchestrator.execute_workflow(workflow.id)

        assert result["status"] == WorkflowStatus.COMPLETED.value
        assert result["tasks_completed"] == 3

    @pytest.mark.asyncio
    async def test_workflow_with_failing_task(self, orchestrator, mock_agents):
        """Test workflow execution with a failing task"""
        # Register agents
        for agent in mock_agents:
            orchestrator.register_agent(agent)

        workflow_definition = {
            "tasks": [
                {"type": "task_a", "payload": {"step": 1}, "priority": 2},
                {"type": "task_b", "payload": {"step": 2, "should_fail": True}, "priority": 2}
            ],
            "dependencies": {},
            "metadata": {}
        }

        workflow = orchestrator.create_workflow(
            name="Failing Workflow",
            description="Workflow with failing task",
            workflow_definition=workflow_definition
        )

        result = await orchestrator.execute_workflow(workflow.id)

        assert result["tasks_completed"] == 1
        assert result["tasks_failed"] == 1

    def test_orchestrator_status(self, orchestrator, mock_agents):
        """Test orchestrator status reporting"""
        # Register agents
        for agent in mock_agents:
            orchestrator.register_agent(agent)

        # Create some tasks
        orchestrator.create_task("task_a", {"test": 1}, TaskPriority.HIGH)
        orchestrator.create_task("task_b", {"test": 2}, TaskPriority.MEDIUM)

        status = orchestrator.get_orchestrator_status()

        assert status["registered_agents"] == 3
        assert status["pending_tasks"] == 2
        assert status["active_workflows"] == 0
        assert len(status["agents"]) == 3

    def test_workflow_status(self, orchestrator):
        """Test workflow status reporting"""
        workflow_definition = {
            "tasks": [
                {"type": "task_a", "payload": {"step": 1}, "priority": 2}
            ],
            "dependencies": {},
            "metadata": {"test": "workflow"}
        }

        workflow = orchestrator.create_workflow(
            name="Status Test Workflow",
            description="Testing workflow status",
            workflow_definition=workflow_definition
        )

        status = orchestrator.get_workflow_status(workflow.id)

        assert status["name"] == "Status Test Workflow"
        assert status["status"] == WorkflowStatus.PENDING.value
        assert status["total_tasks"] == 1
        assert status["completed_tasks"] == 0
        assert status["progress_percentage"] == 0.0

    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self, orchestrator, mock_agents):
        """Test concurrent execution of multiple tasks"""
        # Use agents with very short delay for faster testing
        for agent in mock_agents:
            agent.execution_delay = 0.01
            orchestrator.register_agent(agent)

        # Create multiple tasks that can run concurrently
        tasks = []
        for i in range(3):
            task = AgentTask(
                id=f"concurrent_task_{i}",
                type="task_a",
                priority=2,
                payload={"task_number": i},
                created_at=datetime.now()
            )
            tasks.append(task)

        # Execute tasks concurrently
        start_time = datetime.now()
        results = await asyncio.gather(
            *[orchestrator._assign_and_execute_task(task) for task in tasks]
        )
        end_time = datetime.now()

        execution_time = (end_time - start_time).total_seconds()

        # Should complete in roughly the same time as a single task (due to concurrency)
        # Adding some buffer for test reliability
        assert execution_time < 0.1  # Should be much faster than sequential execution
        assert all(result.success for result in results)

    def test_workflow_not_found(self, orchestrator):
        """Test workflow status for non-existent workflow"""
        with pytest.raises(ValueError) as exc_info:
            orchestrator.get_workflow_status("non_existent_workflow")

        assert "not found" in str(exc_info.value)