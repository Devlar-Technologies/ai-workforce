#!/usr/bin/env python3
"""
Example: Basic workflow demonstrating Devlar's agentic workforce.

This example shows how to:
1. Set up the orchestrator
2. Register agents
3. Create and execute a simple development workflow
"""

import asyncio
import logging
from datetime import datetime

from agents import AgentOrchestrator, TaskPriority
from agents.development import AIEngineerAgent, FullStackDeveloperAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Run the basic workflow example"""
    print("🚀 Starting Devlar Agentic Workforce Demo")
    print("=" * 50)

    # Initialize orchestrator
    orchestrator = AgentOrchestrator()

    # Register agents
    ai_engineer = AIEngineerAgent()
    fullstack_dev = FullStackDeveloperAgent()

    orchestrator.register_agent(ai_engineer)
    orchestrator.register_agent(fullstack_dev)

    print(f"✅ Registered {len(orchestrator.agents)} agents")

    # Create a development workflow
    workflow_definition = {
        "tasks": [
            {
                "type": "ai_architecture",
                "payload": {
                    "system_type": "recommendation_engine",
                    "scale": "medium",
                    "real_time": True
                },
                "priority": 2
            },
            {
                "type": "database_design",
                "payload": {
                    "db_type": "postgresql",
                    "entities": ["users", "products", "recommendations", "interactions"],
                    "scale": "medium"
                },
                "priority": 2
            },
            {
                "type": "api_development",
                "payload": {
                    "api_type": "rest",
                    "endpoints": ["users", "products", "recommendations"],
                    "authentication": "jwt"
                },
                "priority": 2
            },
            {
                "type": "frontend_development",
                "payload": {
                    "framework": "react",
                    "ui_library": "material_ui",
                    "features": ["user_dashboard", "product_catalog", "recommendations"]
                },
                "priority": 2
            }
        ],
        "dependencies": {
            # API development depends on database design
            "task_20231206_000002": ["task_20231206_000001"],
            # Frontend development depends on API development
            "task_20231206_000003": ["task_20231206_000002"]
        },
        "metadata": {
            "project_name": "AI Recommendation System",
            "client": "Demo Client",
            "deadline": "2024-01-15"
        }
    }

    # Create and execute workflow
    workflow = orchestrator.create_workflow(
        name="AI Recommendation System Development",
        description="End-to-end development of an AI-powered recommendation system",
        workflow_definition=workflow_definition
    )

    print(f"📋 Created workflow: {workflow.name}")
    print(f"   Tasks: {len(workflow.tasks)}")
    print(f"   Dependencies: {len(workflow.dependencies)}")

    # Execute the workflow
    print("\n🔄 Executing workflow...")
    try:
        result = await orchestrator.execute_workflow(workflow.id)
        print(f"✅ Workflow completed successfully!")
        print(f"   Status: {result['status']}")
        print(f"   Execution time: {result['execution_time_seconds']:.2f} seconds")
        print(f"   Tasks completed: {result['tasks_completed']}/{result['total_tasks']}")

        if result['tasks_failed'] > 0:
            print(f"   ⚠️  Tasks failed: {result['tasks_failed']}")

    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")

    # Display orchestrator status
    print("\n📊 Final Orchestrator Status:")
    status = orchestrator.get_orchestrator_status()
    print(f"   Registered agents: {status['registered_agents']}")
    print(f"   Active agents: {status['active_agents']}")
    print(f"   Total tasks processed: {status['total_tasks_processed']}")
    print(f"   Completed workflows: {status['completed_workflows']}")

    # Display individual agent statuses
    print("\n👥 Agent Performance:")
    for agent_id, agent_status in status['agents'].items():
        print(f"   {agent_status['name']}:")
        print(f"     Status: {agent_status['status']}")
        print(f"     Tasks completed: {agent_status['tasks_completed']}")
        print(f"     Success rate: {agent_status['success_rate']:.1%}")

    print("\n🎉 Demo completed!")

if __name__ == "__main__":
    asyncio.run(main())