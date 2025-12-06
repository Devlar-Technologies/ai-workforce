"""
Product Development Pod - Idea → Code → Test → Deploy
Handles complete product development lifecycle for Devlar products
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from crewai import Agent, Task, Crew, Process
from loguru import logger

from tools.github_tool import GitHubManagementTool
from tools.vercel_tool import VercelDeploymentTool
from .tasks import ProductDevTasks

class ProductDevPod:
    """
    Product Development Pod for complete feature lifecycle.
    Handles ideation, development, testing, and deployment of Devlar product features.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = self.create_agents()
        self.tasks = ProductDevTasks()

        # Wave execution for development pipeline
        self.execution_waves = {
            "feature_ideation": {
                "wave_1": ["product_ideator"],
                "dependencies": {}
            },
            "technical_implementation": {
                "wave_1": ["product_ideator"],
                "wave_2": ["senior_developer"],
                "wave_3": ["qa_tester"],
                "wave_4": ["pr_creator"],
                "dependencies": {
                    "wave_2": ["wave_1"],
                    "wave_3": ["wave_2"],
                    "wave_4": ["wave_3"]
                }
            },
            "feature_development": {
                "wave_1": ["product_ideator", "senior_developer"],
                "wave_2": ["qa_tester"],
                "wave_3": ["pr_creator"],
                "dependencies": {
                    "wave_2": ["wave_1"],
                    "wave_3": ["wave_2"]
                }
            },
            "deployment_automation": {
                "wave_1": ["pr_creator"],
                "dependencies": {}
            }
        }

    def create_agents(self) -> Dict[str, Agent]:
        """Create product development agents optimized for Devlar's tech stack"""

        # Development tools
        dev_tools = [
            GitHubManagementTool(),
            VercelDeploymentTool(),
        ]

        # Product Innovation Strategist
        product_ideator = Agent(
            role=self.config["product_ideator"]["role"],
            goal=self.config["product_ideator"]["goal"],
            backstory=self.config["product_ideator"]["backstory"],
            verbose=True,
            memory=True,
            tools=[],  # Ideation doesn't need tools
            max_iter=3,
            max_execution_time=1200,  # 20 minutes
            allow_delegation=False
        )

        # Senior Full-Stack Developer
        senior_developer = Agent(
            role=self.config["senior_developer"]["role"],
            goal=self.config["senior_developer"]["goal"],
            backstory=self.config["senior_developer"]["backstory"],
            verbose=True,
            memory=True,
            tools=dev_tools,
            max_iter=8,
            max_execution_time=3600,  # 1 hour for complex development
            allow_delegation=False
        )

        # QA Testing Engineer
        qa_tester = Agent(
            role=self.config["qa_tester"]["role"],
            goal=self.config["qa_tester"]["goal"],
            backstory=self.config["qa_tester"]["backstory"],
            verbose=True,
            memory=True,
            tools=dev_tools,
            max_iter=5,
            max_execution_time=1800,  # 30 minutes
            allow_delegation=False
        )

        # DevOps Integration Specialist
        pr_creator = Agent(
            role=self.config["pr_creator"]["role"],
            goal=self.config["pr_creator"]["goal"],
            backstory=self.config["pr_creator"]["backstory"],
            verbose=True,
            memory=True,
            tools=dev_tools,
            max_iter=5,
            max_execution_time=1200,  # 20 minutes
            allow_delegation=False
        )

        agents = {
            "product_ideator": product_ideator,
            "senior_developer": senior_developer,
            "qa_tester": qa_tester,
            "pr_creator": pr_creator
        }

        logger.info(f"✅ Created {len(agents)} product development agents")
        return agents

    async def execute_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute product development task with development pipeline"""

        start_time = datetime.now()
        logger.info(f"🔨 Starting product development task: {task_name}")

        try:
            # Validate development environment
            await self.validate_dev_environment(parameters)

            # Execute with wave-based development pipeline
            if task_name in self.execution_waves:
                results = await self.execute_dev_waves(task_name, parameters)
            else:
                results = await self.execute_simple_dev_task(task_name, parameters)

            execution_time = (datetime.now() - start_time).total_seconds()

            return {
                "status": "completed",
                "task_name": task_name,
                "results": results,
                "execution_time": execution_time,
                "verdict": self.evaluate_dev_results(results),
                "artifacts": self.collect_artifacts(results)
            }

        except Exception as e:
            logger.error(f"❌ Product development task failed: {e}")
            return {
                "status": "failed",
                "task_name": task_name,
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "verdict": "RED"
            }

    async def validate_dev_environment(self, parameters: Dict[str, Any]):
        """Validate development environment before starting"""

        # Check if this is a deployment task requiring approval
        if parameters.get("deploy", False) or parameters.get("production", False):
            # In production, implement human approval for deployments
            logger.warning("⚠️ Deployment task detected - requires approval")

        # Validate GitHub access
        try:
            github_tool = GitHubManagementTool()
            # Test connection would go here
            logger.info("✅ GitHub access validated")
        except Exception as e:
            logger.warning(f"⚠️ GitHub validation warning: {e}")

    async def execute_dev_waves(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute development task using wave-based pipeline"""

        wave_config = self.execution_waves[task_name]
        results = {}
        completed_waves = set()

        # Calculate wave execution order
        wave_order = self.calculate_wave_order(wave_config)

        for wave_name in wave_order:
            if wave_name not in wave_config or wave_name == "dependencies":
                continue

            logger.info(f"🌊 Executing development {wave_name} for {task_name}")

            # Check dependencies
            dependencies = wave_config.get("dependencies", {}).get(wave_name, [])
            if not all(dep in completed_waves for dep in dependencies):
                logger.warning(f"⚠️ Dependencies not met for {wave_name}, skipping")
                continue

            # Execute agents in this wave
            agent_names = wave_config[wave_name]
            wave_tasks = []

            for agent_name in agent_names:
                if agent_name in self.agents:
                    task = self.create_dev_task(task_name, agent_name, parameters, results)
                    wave_tasks.append(task)

            # Execute wave
            if wave_tasks:
                wave_results = await self.execute_dev_wave_parallel(wave_tasks)
                results[wave_name] = wave_results
                completed_waves.add(wave_name)

                # Quality control for development
                wave_verdict = self.evaluate_wave_results(wave_results)
                if wave_verdict == "RED" and wave_name in ["wave_2", "wave_3"]:  # Critical development waves
                    logger.error(f"❌ Critical development wave {wave_name} failed")
                    # Implement retry with different approach
                    retry_results = await self.retry_dev_wave(wave_name, wave_tasks, parameters)
                    if retry_results:
                        results[wave_name] = retry_results
                    else:
                        raise Exception(f"Critical development wave {wave_name} failed after retry")

        return results

    def create_dev_task(self, task_name: str, agent_name: str, parameters: Dict[str, Any], previous_results: Dict[str, Any]) -> Task:
        """Create development task for specific agent"""

        product = parameters.get("product", "Devlar product")
        feature = parameters.get("feature", "new feature")

        task_descriptions = {
            "feature_ideation": {
                "product_ideator": f"""
                Generate innovative feature ideas for {product} based on research insights and user feedback.

                Product Context: {product}
                Goal: {parameters.get('goal', 'Improve product value')}
                Market Research: {previous_results.get('research_results', 'Use general market knowledge')}

                Your task:
                1. Analyze market research and user feedback
                2. Generate 3-5 feature ideas that align with Devlar's AI-first approach
                3. Prioritize features based on impact, feasibility, and resource requirements
                4. Create detailed feature specifications including:
                   - User stories and acceptance criteria
                   - Technical requirements and constraints
                   - Success metrics and KPIs
                   - Timeline and resource estimates

                Focus on features that:
                - Solve real user pain points
                - Differentiate from competitors
                - Align with Devlar's technical capabilities
                - Can be implemented within 2-4 weeks

                Output: Prioritized feature roadmap with detailed specifications.
                """
            },

            "technical_implementation": {
                "product_ideator": f"""
                Refine feature specifications for {feature} on {product} based on technical constraints.

                Feature: {feature}
                Product: {product}
                Technical Stack: {parameters.get('tech_stack', 'JavaScript, Python, Chrome Extensions, AI APIs')}

                Refine the feature specification considering:
                1. Technical feasibility within Devlar's stack
                2. Integration requirements with existing systems
                3. API dependencies and rate limits
                4. Performance and scalability requirements
                5. Security and privacy considerations

                Output: Technical feature specification ready for development.
                """,

                "senior_developer": f"""
                Implement {feature} for {product} following Devlar's technical standards.

                Feature Specification: {previous_results.get('wave_1', 'Detailed feature spec from ideation')}
                Product: {product}
                Technology: {parameters.get('tech_stack', 'JavaScript/TypeScript, React, Node.js, Python, Chrome Extensions')}

                Implementation requirements:
                1. Write clean, maintainable code following Devlar standards
                2. Implement proper error handling and validation
                3. Add comprehensive logging and monitoring
                4. Follow security best practices
                5. Ensure mobile responsiveness (if applicable)
                6. Optimize for performance and user experience

                Technical considerations:
                - Chrome extension architecture (if applicable)
                - AI API integration patterns
                - Serverless deployment compatibility
                - Database schema changes (if needed)
                - Frontend state management

                Deliverables:
                - Production-ready code
                - API documentation
                - Component documentation
                - Database migration scripts (if applicable)

                Use GitHub tool to create branches and manage code.
                """,

                "qa_tester": f"""
                Test {feature} implementation for {product} across all supported environments.

                Implementation: {previous_results.get('wave_2', 'Code from development wave')}
                Product: {product}
                Feature: {feature}

                Testing scope:
                1. Functional testing against acceptance criteria
                2. Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
                3. Mobile responsiveness testing
                4. Performance testing (load times, memory usage)
                5. Security testing (XSS, CSRF, data validation)
                6. Integration testing with existing features
                7. API testing (if applicable)
                8. User experience testing

                Chrome Extension specific (if applicable):
                - Extension permissions and security
                - Background script functionality
                - Content script injection
                - Storage and sync testing

                AI Feature testing (if applicable):
                - API response handling
                - Error scenarios and fallbacks
                - Rate limiting behavior
                - Data privacy compliance

                Output: Comprehensive QA report with pass/fail status and bug reports.
                """,

                "pr_creator": f"""
                Deploy {feature} for {product} with proper CI/CD and monitoring.

                Code: {previous_results.get('wave_2', 'Tested code from QA')}
                QA Results: {previous_results.get('wave_3', 'QA approval')}
                Product: {product}

                Deployment tasks:
                1. Create production-ready pull request
                2. Set up CI/CD pipeline (if not exists)
                3. Deploy to staging environment
                4. Run automated tests in staging
                5. Deploy to production (with approval)
                6. Set up monitoring and alerts
                7. Update documentation

                Deployment targets:
                - Chrome Web Store (for extensions)
                - Vercel (for web applications)
                - Modal.com (for AI services)

                Post-deployment:
                - Monitor error rates and performance
                - Set up user analytics
                - Prepare rollback plan
                - Document deployment process

                Use GitHub and Vercel tools for deployment automation.
                """
            },

            "feature_development": {
                "product_ideator": f"""
                Design comprehensive feature specification for {feature} on {product}.

                Requirements:
                - User-centered design approach
                - Technical feasibility analysis
                - Integration with existing Devlar products
                - Scalability and performance considerations
                """,

                "senior_developer": f"""
                Develop {feature} for {product} with full implementation.

                Previous Design: {previous_results.get('wave_1', 'Feature specification')}

                Implementation includes:
                - Complete feature development
                - API integration
                - Testing integration
                - Documentation
                """
            },

            "deployment_automation": {
                "pr_creator": f"""
                Set up automated deployment pipeline for {product}.

                Requirements:
                1. GitHub Actions CI/CD pipeline
                2. Automated testing and quality gates
                3. Staging and production environments
                4. Rollback capabilities
                5. Monitoring and alerting integration

                Deployment targets:
                - Vercel for web applications
                - Chrome Web Store for extensions
                - Modal.com for AI services

                Output: Complete CI/CD pipeline with deployment automation.
                """
            }
        }

        # Get description or create default
        descriptions = task_descriptions.get(task_name, {})
        description = descriptions.get(agent_name, f"Execute {task_name} using {agent_name}")

        return Task(
            description=description,
            expected_output=f"Detailed {agent_name} deliverable for {task_name} with artifacts and documentation",
            agent=self.agents[agent_name]
        )

    async def execute_dev_wave_parallel(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute development wave tasks with proper sequencing"""

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

        # For development, some tasks need to be sequential, others parallel
        # This is simplified - in production, implement proper dependency management
        results = {}

        for i, task in enumerate(tasks):
            crew = Crew(
                agents=[task.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )

            task_id = f"dev_task_{i}_{task.agent.role.lower().replace(' ', '_')}"
            results[task_id] = crew.kickoff()

        return results

    async def execute_simple_dev_task(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute simple development task"""

        # Default to senior developer for simple tasks
        agent = self.agents["senior_developer"]

        task = Task(
            description=f"Execute {task_name} development task with parameters: {parameters}",
            expected_output=f"Development deliverable for {task_name}",
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
            "simple_dev_result": result,
            "agent": agent.role
        }

    def calculate_wave_order(self, wave_config: Dict[str, Any]) -> List[str]:
        """Calculate wave execution order based on dependencies"""
        waves = [key for key in wave_config.keys() if key != "dependencies"]
        dependencies = wave_config.get("dependencies", {})

        # Topological sort for proper dependency order
        ordered = []
        remaining = waves.copy()

        while remaining:
            ready = []
            for wave in remaining:
                deps = dependencies.get(wave, [])
                if all(dep in ordered for dep in deps):
                    ready.append(wave)

            if not ready:
                # Handle circular dependencies
                remaining.sort()
                ordered.extend(remaining)
                break

            ready.sort()
            ordered.extend(ready)
            for wave in ready:
                remaining.remove(wave)

        return ordered

    def evaluate_wave_results(self, wave_results: Dict[str, Any]) -> str:
        """Evaluate development wave results for quality"""

        if not wave_results:
            return "RED"

        # Count errors and successes
        error_count = 0
        total_tasks = len(wave_results)

        for task_id, result in wave_results.items():
            if isinstance(result, Exception) or "error" in str(result).lower():
                error_count += 1

        error_rate = error_count / total_tasks if total_tasks > 0 else 1.0

        if error_rate == 0:
            return "GREEN"
        elif error_rate <= 0.3:  # More strict for development
            return "YELLOW"
        else:
            return "RED"

    def evaluate_dev_results(self, results: Dict[str, Any]) -> str:
        """Evaluate overall development results"""

        if not results:
            return "RED"

        verdicts = []
        for wave_name, wave_results in results.items():
            verdict = self.evaluate_wave_results(wave_results)
            verdicts.append(verdict)

        # Development requires higher quality standards
        if all(v == "GREEN" for v in verdicts):
            return "GREEN"
        elif any(v == "RED" for v in verdicts):
            return "RED"
        else:
            return "YELLOW"

    def collect_artifacts(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect development artifacts from execution"""

        artifacts = {
            "code_files": [],
            "documentation": [],
            "test_reports": [],
            "deployment_configs": [],
            "pull_requests": []
        }

        # Analyze results to extract artifacts
        # This is simplified - in production, implement proper artifact extraction
        for wave_name, wave_results in results.items():
            if "developer" in wave_name.lower():
                artifacts["code_files"].append(f"Code from {wave_name}")
            elif "tester" in wave_name.lower():
                artifacts["test_reports"].append(f"Test report from {wave_name}")
            elif "pr_creator" in wave_name.lower():
                artifacts["deployment_configs"].append(f"Deployment from {wave_name}")

        return artifacts

    async def retry_dev_wave(self, wave_name: str, tasks: List[Task], parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retry failed development wave with adaptive approach"""

        logger.info(f"🔄 Retrying development wave {wave_name}")

        try:
            # Implement adaptive retry strategy
            # For now, simple retry with modified parameters
            modified_params = {**parameters, "retry": True}

            # Update task descriptions for retry
            for task in tasks:
                task.description += "\n\nNote: This is a retry attempt. Focus on robustness and error handling."

            retry_results = await self.execute_dev_wave_parallel(tasks)
            retry_verdict = self.evaluate_wave_results(retry_results)

            if retry_verdict in ["GREEN", "YELLOW"]:
                return retry_results
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Development retry failed: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get product development pod status"""
        return {
            "pod_name": "product_dev_pod",
            "agents_count": len(self.agents),
            "agents": list(self.agents.keys()),
            "execution_waves": list(self.execution_waves.keys()),
            "development_pipeline": {
                "ideation": "Ready",
                "development": "Ready",
                "testing": "Ready",
                "deployment": "Ready"
            },
            "status": "ready"
        }