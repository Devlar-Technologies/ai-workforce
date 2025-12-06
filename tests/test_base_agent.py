"""
Tests for the base agent functionality.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from agents.base_agent import BaseAgent, AgentTask, AgentResult

class TestAgent(BaseAgent):
    """Test agent implementation for testing purposes"""

    def __init__(self):
        super().__init__("test_agent_001", "Test Agent", ["test_task", "demo_task"])

    async def execute_task(self, task: AgentTask) -> AgentResult:
        """Simple test task execution"""
        if task.type == "test_task":
            return AgentResult(
                success=True,
                data={"result": "test_completed"},
                message="Test task completed successfully",
                timestamp=datetime.now(),
                agent_id=self.agent_id
            )
        elif task.type == "demo_task":
            await asyncio.sleep(0.1)  # Simulate work
            return AgentResult(
                success=True,
                data={"result": "demo_completed", "duration": 0.1},
                message="Demo task completed successfully",
                timestamp=datetime.now(),
                agent_id=self.agent_id
            )
        elif task.type == "failing_task":
            return AgentResult(
                success=False,
                data={},
                message="Task intentionally failed",
                timestamp=datetime.now(),
                agent_id=self.agent_id
            )
        else:
            raise Exception(f"Unknown task type: {task.type}")

@pytest.fixture
def test_agent():
    """Fixture providing a test agent instance"""
    return TestAgent()

@pytest.fixture
def sample_task():
    """Fixture providing a sample task"""
    return AgentTask(
        id="test_task_001",
        type="test_task",
        priority=3,
        payload={"test_data": "sample"},
        created_at=datetime.now()
    )

class TestBaseAgent:
    """Test cases for base agent functionality"""

    def test_agent_initialization(self, test_agent):
        """Test agent initialization"""
        assert test_agent.agent_id == "test_agent_001"
        assert test_agent.name == "Test Agent"
        assert "test_task" in test_agent.capabilities
        assert "demo_task" in test_agent.capabilities
        assert test_agent.status == "idle"
        assert test_agent.current_task is None

    def test_can_handle_task(self, test_agent):
        """Test task capability checking"""
        assert test_agent.can_handle_task("test_task") is True
        assert test_agent.can_handle_task("demo_task") is True
        assert test_agent.can_handle_task("unknown_task") is False

    @pytest.mark.asyncio
    async def test_successful_task_execution(self, test_agent, sample_task):
        """Test successful task execution"""
        result = await test_agent.process_task(sample_task)

        assert result.success is True
        assert result.agent_id == test_agent.agent_id
        assert "test_completed" in result.data["result"]
        assert sample_task.status == "completed"
        assert sample_task.assigned_to == test_agent.agent_id
        assert test_agent.status == "idle"

    @pytest.mark.asyncio
    async def test_failing_task_execution(self, test_agent):
        """Test failed task execution"""
        failing_task = AgentTask(
            id="failing_task_001",
            type="failing_task",
            priority=3,
            payload={},
            created_at=datetime.now()
        )

        result = await test_agent.process_task(failing_task)

        assert result.success is False
        assert failing_task.status == "failed"
        assert test_agent.status == "idle"

    @pytest.mark.asyncio
    async def test_task_exception_handling(self, test_agent):
        """Test task execution with exceptions"""
        exception_task = AgentTask(
            id="exception_task_001",
            type="unknown_task",
            priority=3,
            payload={},
            created_at=datetime.now()
        )

        result = await test_agent.process_task(exception_task)

        assert result.success is False
        assert "exception" in result.message.lower()
        assert exception_task.status == "failed"

    def test_agent_status_tracking(self, test_agent):
        """Test agent status tracking"""
        status = test_agent.get_status()

        assert status["agent_id"] == test_agent.agent_id
        assert status["name"] == test_agent.name
        assert status["status"] == "idle"
        assert status["capabilities"] == test_agent.capabilities
        assert status["current_task"] is None
        assert status["tasks_completed"] == 0
        assert status["tasks_failed"] == 0

    @pytest.mark.asyncio
    async def test_agent_health_check(self, test_agent):
        """Test agent health check"""
        is_healthy = await test_agent.health_check()
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_multiple_task_execution(self, test_agent):
        """Test executing multiple tasks"""
        tasks = []
        for i in range(3):
            task = AgentTask(
                id=f"task_{i}",
                type="test_task",
                priority=3,
                payload={"task_number": i},
                created_at=datetime.now()
            )
            tasks.append(task)

        results = []
        for task in tasks:
            result = await test_agent.process_task(task)
            results.append(result)

        assert all(result.success for result in results)
        assert len(test_agent.task_history) == 3

    def test_agent_result_serialization(self, test_agent):
        """Test agent result JSON serialization"""
        result = AgentResult(
            success=True,
            data={"test": "data"},
            message="Test message",
            timestamp=datetime.now(),
            agent_id=test_agent.agent_id
        )

        json_str = result.to_json()
        assert isinstance(json_str, str)
        assert "success" in json_str
        assert "test_agent_001" in json_str