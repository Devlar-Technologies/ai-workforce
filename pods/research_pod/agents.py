"""
Research Pod - Market Research and Competitive Intelligence Agents
Conducts market analysis and competitive research for Devlar products
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from crewai import Agent, Task, Crew, Process
from loguru import logger

from tools.firecrawl_tool import FirecrawlResearchTool
from tools.apollo_tool import ApolloProspectingTool
from .tasks import ResearchTasks

class ResearchPod:
    """
    Research Pod for market intelligence and competitive analysis.
    Handles market research, competitor analysis, and user research for Devlar products.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = self.create_agents()
        self.tasks = ResearchTasks()

        # Wave execution inspired by Conductor
        self.execution_waves = {
            "market_analysis": {
                "wave_1": ["market_researcher"],
                "wave_2": ["competitor_analyst"],
                "dependencies": {"wave_2": ["wave_1"]}
            },
            "competitor_deep_dive": {
                "wave_1": ["competitor_analyst", "market_researcher"],
                "dependencies": {}
            },
            "user_research": {
                "wave_1": ["market_researcher"],
                "dependencies": {}
            }
        }

    def create_agents(self) -> Dict[str, Agent]:
        """Create research agents with Devlar-optimized configurations"""

        # Get tools
        research_tools = [
            FirecrawlResearchTool(),
            ApolloProspectingTool(),
        ]

        # Market Researcher Agent
        market_researcher = Agent(
            role=self.config["market_researcher"]["role"],
            goal=self.config["market_researcher"]["goal"],
            backstory=self.config["market_researcher"]["backstory"],
            verbose=True,
            memory=True,
            tools=research_tools,
            max_iter=5,
            max_execution_time=1800,  # 30 minutes
            allow_delegation=False
        )

        # Competitive Intelligence Agent
        competitor_analyst = Agent(
            role=self.config["competitor_analyst"]["role"],
            goal=self.config["competitor_analyst"]["goal"],
            backstory=self.config["competitor_analyst"]["backstory"],
            verbose=True,
            memory=True,
            tools=research_tools,
            max_iter=5,
            max_execution_time=1800,
            allow_delegation=False
        )

        agents = {
            "market_researcher": market_researcher,
            "competitor_analyst": competitor_analyst
        }

        logger.info(f"✅ Created {len(agents)} research agents")
        return agents

    async def execute_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research task with wave-based parallel execution

        Args:
            task_name: Name of the research task to execute
            parameters: Task parameters and context

        Returns:
            Research results and analysis
        """
        start_time = datetime.now()
        logger.info(f"🔬 Starting research task: {task_name}")

        try:
            # Get task configuration
            if task_name not in self.execution_waves:
                return await self.execute_simple_task(task_name, parameters)

            # Execute with wave-based approach (inspired by Conductor)
            wave_config = self.execution_waves[task_name]
            results = await self.execute_waves(task_name, wave_config, parameters)

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "status": "completed",
                "task_name": task_name,
                "results": results,
                "execution_time": execution_time,
                "verdict": self.evaluate_results(results)
            }

        except Exception as e:
            logger.error(f"❌ Research task failed: {e}")
            return {
                "status": "failed",
                "task_name": task_name,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "verdict": "RED"
            }

    async def execute_waves(self, task_name: str, wave_config: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using wave-based approach with parallel and sequential execution"""
        results = {}
        completed_waves = set()

        # Sort waves by dependency order
        wave_order = self.calculate_wave_order(wave_config)

        for wave_name in wave_order:
            if wave_name not in wave_config or wave_name == "dependencies":
                continue

            logger.info(f"🌊 Executing {wave_name} for {task_name}")

            # Check if dependencies are met
            dependencies = wave_config.get("dependencies", {}).get(wave_name, [])
            if not all(dep in completed_waves for dep in dependencies):
                logger.warning(f"⚠️ Dependencies not met for {wave_name}, skipping")
                continue

            # Execute agents in this wave in parallel
            agent_names = wave_config[wave_name]
            wave_tasks = []

            for agent_name in agent_names:
                if agent_name in self.agents:
                    task = self.create_task_for_agent(task_name, agent_name, parameters, results)
                    wave_tasks.append(task)

            # Execute wave tasks in parallel
            if wave_tasks:
                wave_results = await self.execute_parallel_tasks(wave_tasks)
                results[wave_name] = wave_results
                completed_waves.add(wave_name)

                # Quality control check (inspired by Conductor's GREEN/RED/YELLOW verdicts)
                wave_verdict = self.evaluate_wave_results(wave_results)
                if wave_verdict == "RED":
                    logger.error(f"❌ Wave {wave_name} failed quality control")
                    # Implement retry logic here
                    retry_results = await self.retry_wave(wave_name, wave_tasks)
                    if retry_results:
                        results[wave_name] = retry_results
                    else:
                        raise Exception(f"Wave {wave_name} failed after retry")

        return results

    def calculate_wave_order(self, wave_config: Dict[str, Any]) -> List[str]:
        """Calculate execution order based on dependencies"""
        waves = [key for key in wave_config.keys() if key != "dependencies"]
        dependencies = wave_config.get("dependencies", {})

        # Simple topological sort
        ordered = []
        remaining = waves.copy()

        while remaining:
            ready = []
            for wave in remaining:
                deps = dependencies.get(wave, [])
                if all(dep in ordered for dep in deps):
                    ready.append(wave)

            if not ready:
                # Circular dependency or error
                remaining.sort()  # Fallback to alphabetical
                ordered.extend(remaining)
                break

            # Add ready waves (maintain original order for parallel waves)
            ready.sort()
            ordered.extend(ready)
            for wave in ready:
                remaining.remove(wave)

        return ordered

    def create_task_for_agent(self, task_name: str, agent_name: str, parameters: Dict[str, Any], previous_results: Dict[str, Any]) -> Task:
        """Create specific task for an agent"""

        task_descriptions = {
            "market_analysis": {
                "market_researcher": f"""
                Conduct comprehensive market analysis for {parameters.get('product', 'Devlar products')} in the {parameters.get('market_segment', 'productivity tools')} market.

                Research focus areas:
                1. Market size and growth trends
                2. Key players and market share
                3. Pricing strategies and business models
                4. User demographics and behavior patterns
                5. Technology trends and innovation opportunities
                6. Regulatory and competitive landscape

                Use Firecrawl to gather data from:
                - Industry reports and market research sites
                - Competitor websites and product pages
                - User review platforms and forums
                - Industry news and analysis sites

                Provide actionable insights for Devlar's product strategy.
                """,
                "competitor_analyst": f"""
                Analyze top competitors for {parameters.get('product', 'Devlar products')} and identify strategic advantages.

                Focus on competitors like: {', '.join(parameters.get('competitors', ['industry leaders']))}

                Analysis areas:
                1. Feature comparison and gap analysis
                2. Pricing and business model analysis
                3. User acquisition and marketing strategies
                4. Technical architecture and capabilities
                5. User feedback and satisfaction levels
                6. Differentiation opportunities for Devlar

                Previous market research: {previous_results.get('wave_1', 'None available')}

                Provide competitive positioning recommendations.
                """
            },
            "competitor_deep_dive": {
                "competitor_analyst": f"""
                Conduct deep competitive analysis of the top 10 competitors in {parameters.get('product_category', 'productivity tools')}.

                For each competitor, analyze:
                1. Core value proposition and positioning
                2. Feature set and product roadmap
                3. Pricing tiers and monetization strategy
                4. User acquisition channels and marketing
                5. Technical implementation and architecture
                6. User reviews and satisfaction metrics
                7. Strengths, weaknesses, and vulnerabilities

                Deliverable: Competitive intelligence matrix with actionable insights for Devlar.
                """,
                "market_researcher": f"""
                Research market dynamics and user behavior patterns for {parameters.get('product_category', 'productivity tools')}.

                Research areas:
                1. User journey and pain points
                2. Feature adoption patterns
                3. Switching behaviors and triggers
                4. Emerging trends and technologies
                5. Unmet needs and market gaps
                6. User personas and segmentation

                Focus on insights that can inform Devlar's product strategy and positioning.
                """
            },
            "user_research": {
                "market_researcher": f"""
                Conduct comprehensive user research for {parameters.get('product', 'Devlar products')} targeting {parameters.get('audience', 'professionals')}.

                Research objectives:
                1. Define detailed user personas
                2. Map user workflows and pain points
                3. Identify feature requirements and priorities
                4. Understand decision-making processes
                5. Analyze user feedback and satisfaction drivers
                6. Discover unmet needs and opportunities

                Use multiple research methods:
                - User interview analysis from forums and reviews
                - Workflow analysis from productivity communities
                - Feature request analysis from competitor platforms
                - Social media sentiment analysis

                Provide actionable user insights for product development.
                """
            }
        }

        # Get task description or create generic one
        descriptions = task_descriptions.get(task_name, {})
        description = descriptions.get(agent_name, f"Execute {task_name} research using {agent_name}")

        return Task(
            description=description,
            expected_output=f"Detailed research report with actionable insights and recommendations for {task_name}",
            agent=self.agents[agent_name]
        )

    async def execute_parallel_tasks(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute multiple tasks in parallel"""
        if len(tasks) == 1:
            # Single task execution
            crew = Crew(
                agents=[tasks[0].agent],
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            result = crew.kickoff()
            return {"single_task_result": result}

        # Parallel execution for multiple tasks
        results = {}

        # Create separate crews for each task to enable parallel execution
        async def execute_single_task(task: Task, task_id: str):
            crew = Crew(
                agents=[task.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            return {task_id: crew.kickoff()}

        # Execute all tasks concurrently
        task_futures = []
        for i, task in enumerate(tasks):
            task_id = f"task_{i}_{task.agent.role.lower().replace(' ', '_')}"
            task_futures.append(execute_single_task(task, task_id))

        # Wait for all tasks to complete
        parallel_results = await asyncio.gather(*task_futures, return_exceptions=True)

        # Combine results
        for result in parallel_results:
            if isinstance(result, dict):
                results.update(result)
            else:
                logger.error(f"Task execution error: {result}")

        return results

    async def execute_simple_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple task without wave-based approach"""

        # Default to market researcher for simple tasks
        agent = self.agents["market_researcher"]

        task = Task(
            description=f"Execute {task_name} research with parameters: {parameters}",
            expected_output=f"Research results and analysis for {task_name}",
            agent=agent
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        return {
            "simple_task_result": result,
            "agent": agent.role
        }

    def evaluate_wave_results(self, wave_results: Dict[str, Any]) -> str:
        """
        Evaluate wave results quality (inspired by Conductor's verdict system)

        Returns: GREEN (success), YELLOW (warning), RED (failure)
        """
        if not wave_results:
            return "RED"

        # Check for errors
        error_count = 0
        total_tasks = len(wave_results)

        for task_id, result in wave_results.items():
            if isinstance(result, Exception) or "error" in str(result).lower():
                error_count += 1

        # Calculate verdict
        error_rate = error_count / total_tasks if total_tasks > 0 else 1.0

        if error_rate == 0:
            return "GREEN"
        elif error_rate <= 0.5:
            return "YELLOW"
        else:
            return "RED"

    def evaluate_results(self, results: Dict[str, Any]) -> str:
        """Evaluate overall task results"""
        if not results:
            return "RED"

        # Evaluate each wave
        verdicts = []
        for wave_name, wave_results in results.items():
            verdict = self.evaluate_wave_results(wave_results)
            verdicts.append(verdict)

        # Overall verdict
        if all(v == "GREEN" for v in verdicts):
            return "GREEN"
        elif any(v == "RED" for v in verdicts):
            return "RED"
        else:
            return "YELLOW"

    async def retry_wave(self, wave_name: str, tasks: List[Task]) -> Optional[Dict[str, Any]]:
        """Retry failed wave with adaptive agent selection"""
        logger.info(f"🔄 Retrying wave {wave_name}")

        try:
            # Simple retry - in production, implement adaptive agent selection
            retry_results = await self.execute_parallel_tasks(tasks)
            retry_verdict = self.evaluate_wave_results(retry_results)

            if retry_verdict in ["GREEN", "YELLOW"]:
                return retry_results
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Retry failed: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get research pod status"""
        return {
            "pod_name": "research_pod",
            "agents_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "execution_waves": list(self.execution_waves.keys()),
            "status": "ready"
        }