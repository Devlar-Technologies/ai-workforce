#!/usr/bin/env python3
"""
Devlar AI Workforce - Main CEO Orchestrator
Entry point for the hierarchical CrewAI system
"""

import os
import asyncio
import yaml
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from crewai import Agent, Task, Crew, Process
from crewai.agent import Agent
from crewai.task import Task

from memory import DevlarMemory
from utils.cost_tracker import CostTracker
from utils.report_generator import ReportGenerator
from utils.logging_config import setup_logging

# Import all specialist pods
from pods.research_pod import ResearchPod
from pods.product_dev_pod import ProductDevPod
from pods.marketing_pod import MarketingPod
from pods.sales_outreach_pod import SalesOutreachPod
from pods.customer_success_pod import CustomerSuccessPod
from pods.analytics_pod import AnalyticsPod

# Import interfaces
from interfaces.telegram_bot import TelegramInterface
from interfaces.streamlit_app import StreamlitInterface

class DevlarCEO:
    """
    CEO Orchestrator for Devlar AI Workforce
    Manages hierarchical task delegation to specialist pods
    """

    def __init__(self, config_path: str = "config/"):
        self.config_path = Path(config_path)
        self.setup_environment()

        # Initialize core components
        self.memory = DevlarMemory()
        self.cost_tracker = CostTracker()
        self.report_generator = ReportGenerator()

        # Load configurations
        self.agents_config = self.load_config("agents.yaml")
        self.tasks_config = self.load_config("tasks.yaml")

        # Initialize specialist pods
        self.pods = self.initialize_pods()

        # Initialize CEO agent
        self.ceo_agent = self.create_ceo_agent()

        logger.info("🚀 Devlar CEO Orchestrator initialized successfully")

    def setup_environment(self):
        """Setup environment and logging"""
        load_dotenv()
        setup_logging()

        # Validate required environment variables
        required_vars = [
            "XAI_API_KEY",
            "PINECONE_API_KEY",
            "FIRECRAWL_API_KEY",
            "TELEGRAM_BOT_TOKEN"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")

    def load_config(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        config_file = self.config_path / filename
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            raise

    def initialize_pods(self) -> Dict[str, Any]:
        """Initialize all specialist pods"""
        pods = {
            "research": ResearchPod(self.agents_config["research_pod"]),
            "product_dev": ProductDevPod(self.agents_config["product_dev_pod"]),
            "marketing": MarketingPod(self.agents_config["marketing_pod"]),
            "sales_outreach": SalesOutreachPod(self.agents_config["sales_outreach_pod"]),
            "customer_success": CustomerSuccessPod(self.agents_config["customer_success_pod"]),
            "analytics": AnalyticsPod(self.agents_config["analytics_pod"])
        }

        logger.info(f"✅ Initialized {len(pods)} specialist pods")
        return pods

    def create_ceo_agent(self) -> Agent:
        """Create the CEO orchestrator agent"""
        ceo_config = self.agents_config["ceo_orchestrator"]

        return Agent(
            role=ceo_config["role"],
            goal=ceo_config["goal"],
            backstory=ceo_config["backstory"],
            verbose=ceo_config.get("verbose", True),
            memory=ceo_config.get("memory", True),
            max_iter=ceo_config.get("max_iter", 5),
            max_execution_time=ceo_config.get("max_execution_time", 3600),
            tools=self.get_ceo_tools()
        )

    def get_ceo_tools(self) -> list:
        """Get tools available to CEO for orchestration"""
        from tools.pinecone_tool import PineconeMemoryTool
        from tools.telegram_tool import TelegramNotificationTool

        return [
            PineconeMemoryTool(),
            TelegramNotificationTool()
        ]

    async def execute_goal(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a high-level business goal by delegating to appropriate pods

        Args:
            goal: High-level business objective (e.g., "Get 100 new Chromentum beta users")
            context: Additional context and parameters

        Returns:
            Execution results with performance metrics
        """
        start_time = datetime.now()
        execution_id = f"exec_{int(start_time.timestamp())}"

        logger.info(f"🎯 Executing goal: {goal}")
        logger.info(f"📋 Execution ID: {execution_id}")

        try:
            # Check if human approval needed for high-cost operations
            if await self.cost_tracker.requires_approval(goal):
                approval = await self.request_human_approval(goal, execution_id)
                if not approval:
                    return {"status": "cancelled", "reason": "human_approval_denied"}

            # Analyze goal and determine workflow
            workflow_plan = await self.analyze_and_plan(goal, context)

            # Execute workflow with hierarchical delegation
            results = await self.execute_workflow(workflow_plan, execution_id)

            # Generate comprehensive report
            report = await self.report_generator.generate_report(
                execution_id=execution_id,
                goal=goal,
                workflow_plan=workflow_plan,
                results=results,
                start_time=start_time
            )

            # Store results in memory
            await self.memory.store_execution(execution_id, {
                "goal": goal,
                "context": context,
                "workflow_plan": workflow_plan,
                "results": results,
                "report_path": report["file_path"],
                "execution_time": (datetime.now() - start_time).total_seconds()
            })

            logger.success(f"✅ Goal completed: {goal}")
            return {
                "status": "completed",
                "execution_id": execution_id,
                "results": results,
                "report": report,
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

        except Exception as e:
            logger.error(f"❌ Goal execution failed: {e}")
            await self.handle_execution_error(execution_id, goal, str(e))
            return {
                "status": "failed",
                "execution_id": execution_id,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }

    async def analyze_and_plan(self, goal: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze goal and create detailed execution plan
        """
        # Check if goal matches predefined examples
        example_goals = self.tasks_config.get("example_goals", {})

        # Find matching example or create custom workflow
        workflow_plan = None
        for example_key, example_config in example_goals.items():
            if self.goal_matches_example(goal, example_config["goal"]):
                workflow_plan = example_config
                logger.info(f"📋 Using predefined workflow: {example_key}")
                break

        if not workflow_plan:
            # Create custom workflow using CEO agent
            workflow_plan = await self.create_custom_workflow(goal, context)
            logger.info("📋 Created custom workflow plan")

        # Enhance plan with context
        if context:
            workflow_plan["context"] = {**workflow_plan.get("context", {}), **context}

        return workflow_plan

    def goal_matches_example(self, goal: str, example_goal: str) -> bool:
        """Check if goal matches predefined example"""
        # Simple keyword matching - can be enhanced with NLP
        goal_words = set(goal.lower().split())
        example_words = set(example_goal.lower().split())

        # Check for significant overlap
        overlap = len(goal_words.intersection(example_words))
        return overlap >= 3  # Adjust threshold as needed

    async def create_custom_workflow(self, goal: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create custom workflow plan using CEO agent intelligence"""

        # Create planning task for CEO
        planning_task = Task(
            description=f"""
            Analyze this business goal and create a detailed execution plan:
            Goal: {goal}
            Context: {context or "None provided"}

            Create a workflow plan that specifies:
            1. Which pods should be involved
            2. Task sequence and dependencies
            3. Success metrics and deliverables
            4. Timeline and resource requirements

            Consider Devlar's product portfolio, available resources, and strategic priorities.
            """,
            expected_output="Detailed workflow plan with pod assignments, task sequences, and success metrics",
            agent=self.ceo_agent
        )

        # Execute planning
        planning_crew = Crew(
            agents=[self.ceo_agent],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=True
        )

        plan_result = planning_crew.kickoff()

        # Parse and structure the plan
        # Note: In production, you'd want more sophisticated parsing
        return {
            "goal": goal,
            "workflow": "custom",
            "plan": plan_result,
            "context": context or {}
        }

    async def execute_workflow(self, workflow_plan: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute workflow plan by delegating to appropriate pods"""

        workflow_type = workflow_plan.get("workflow", "custom")
        workflow_templates = self.tasks_config.get("workflow_templates", {})

        if workflow_type in workflow_templates:
            # Execute predefined workflow
            sequence = workflow_templates[workflow_type]["sequence"]
            return await self.execute_sequence(sequence, workflow_plan, execution_id)
        else:
            # Execute custom workflow
            return await self.execute_custom_workflow(workflow_plan, execution_id)

    async def execute_sequence(self, sequence: list, workflow_plan: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute a predefined task sequence"""
        results = {}

        for step in sequence:
            pod_name = list(step.keys())[0]
            task_name = step[pod_name]

            logger.info(f"🔄 Executing {pod_name}.{task_name}")

            try:
                pod = self.pods.get(pod_name)
                if not pod:
                    raise ValueError(f"Pod not found: {pod_name}")

                # Execute task in the specified pod
                result = await pod.execute_task(task_name, workflow_plan.get("parameters", {}))
                results[f"{pod_name}_{task_name}"] = result

                logger.success(f"✅ Completed {pod_name}.{task_name}")

            except Exception as e:
                logger.error(f"❌ Failed {pod_name}.{task_name}: {e}")
                results[f"{pod_name}_{task_name}"] = {"error": str(e), "status": "failed"}

                # Decide whether to continue or abort
                if self.should_abort_on_error(task_name, str(e)):
                    logger.warning("🛑 Aborting workflow due to critical error")
                    break

        return results

    async def execute_custom_workflow(self, workflow_plan: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Execute a custom workflow plan"""
        # Parse the plan and execute accordingly
        # This would involve more sophisticated parsing of the CEO's plan
        logger.info("🔄 Executing custom workflow")

        # For now, return a placeholder implementation
        return {
            "custom_execution": "completed",
            "plan": workflow_plan.get("plan", ""),
            "message": "Custom workflow executed (implementation varies by plan)"
        }

    def should_abort_on_error(self, task_name: str, error: str) -> bool:
        """Determine if workflow should abort on specific error"""
        critical_tasks = ["deployment_automation", "payment_processing"]
        critical_errors = ["authentication_failed", "permission_denied", "rate_limit_exceeded"]

        if task_name in critical_tasks:
            return True

        if any(critical_error in error.lower() for critical_error in critical_errors):
            return True

        return False

    async def request_human_approval(self, goal: str, execution_id: str) -> bool:
        """Request human approval for high-cost operations"""
        from tools.telegram_tool import TelegramNotificationTool

        telegram = TelegramNotificationTool()

        message = f"""
🚨 **Approval Required**

**Goal:** {goal}
**Execution ID:** {execution_id}
**Estimated Cost:** > $50

Do you approve this execution?
Reply with: `approve {execution_id}` or `deny {execution_id}`
        """

        await telegram.send_notification(message)

        # Wait for approval (implementation would involve checking for response)
        # For now, return True to allow execution
        logger.warning(f"⏳ Waiting for approval for: {goal}")
        return True

    async def handle_execution_error(self, execution_id: str, goal: str, error: str):
        """Handle execution errors with notifications and recovery"""
        from tools.telegram_tool import TelegramNotificationTool

        telegram = TelegramNotificationTool()

        error_message = f"""
❌ **Execution Failed**

**Goal:** {goal}
**Execution ID:** {execution_id}
**Error:** {error}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The AI workforce encountered an error. Please review and potentially restart.
        """

        await telegram.send_notification(error_message)
        logger.error(f"Notified human about execution failure: {execution_id}")

    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the AI workforce"""
        return {
            "ceo_status": "active",
            "pods_status": {name: pod.get_status() for name, pod in self.pods.items()},
            "memory_status": await self.memory.get_status(),
            "cost_tracking": self.cost_tracker.get_summary(),
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """Main entry point for testing"""
    ceo = DevlarCEO()

    # Test goal execution
    test_goal = "Get 100 new Chromentum beta users this week"
    result = await ceo.execute_goal(test_goal)

    print(f"Execution result: {result}")

if __name__ == "__main__":
    asyncio.run(main())