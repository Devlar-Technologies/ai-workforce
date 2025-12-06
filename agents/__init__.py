"""
Devlar Agents - AI-first agentic workforce for software development.

This package provides a comprehensive agentic workforce system designed for
Devlar Technologies' AI-first approach to software development.
"""

from .base_agent import BaseAgent, AgentTask, AgentResult
from .orchestrator import AgentOrchestrator, TaskPriority, WorkflowStatus, Workflow

__version__ = "0.1.0"
__author__ = "Devlar Technologies"
__email__ = "info@devlar.io"

__all__ = [
    "BaseAgent",
    "AgentTask",
    "AgentResult",
    "AgentOrchestrator",
    "TaskPriority",
    "WorkflowStatus",
    "Workflow",
]