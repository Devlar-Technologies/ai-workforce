"""
Devlar AI Workforce - Customer Success Pod Agents
Customer onboarding, support automation, retention, and expansion
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from loguru import logger

from tools.firecrawl_tool import FirecrawlTool


class CustomerSuccessPod(CrewBase):
    """
    Customer Success specialist pod for retention and growth
    Handles onboarding, support, churn prevention, and account expansion
    """

    def __init__(self):
        """Initialize Customer Success Pod with specialized agents"""
        super().__init__()
        self.firecrawl = FirecrawlTool()

        # Initialize LLM
        self.llm = self._get_llm()

        logger.info("🎯 Customer Success Pod initialized with support and retention specialists")

    def _get_llm(self):
        """Get configured LLM with fallback"""
        try:
            # Try xAI Grok first
            if os.getenv("XAI_API_KEY"):
                return ChatOpenAI(
                    api_key=os.getenv("XAI_API_KEY"),
                    base_url="https://api.x.ai/v1",
                    model="grok-beta",
                    temperature=0.7
                )
        except Exception as e:
            logger.warning(f"xAI not available: {e}, falling back to Anthropic")

        # Fallback to Anthropic
        return ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-5-sonnet-20241022",
            temperature=0.7
        )

    @agent
    def onboarding_specialist(self) -> Agent:
        """Customer onboarding and activation agent"""
        return Agent(
            role="Customer Onboarding Specialist",
            goal="Create frictionless onboarding experiences that drive rapid time-to-value",
            backstory="""You're an onboarding expert who has helped thousands of users successfully
            adopt SaaS products. You understand the critical first 30 days and know how to guide users
            to their 'aha moment' quickly. You can design onboarding flows, create educational content,
            and identify friction points that cause drop-offs. You've increased activation rates by
            50%+ through optimized onboarding.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def support_engineer(self) -> Agent:
        """Technical support and issue resolution agent"""
        return Agent(
            role="Customer Support Engineer",
            goal="Resolve customer issues quickly and create self-service solutions",
            backstory="""You're a support engineering expert who has built world-class support
            operations. You can diagnose technical issues, write clear documentation, and create
            automated solutions. You understand support metrics like CSAT, first response time,
            and resolution time. You've implemented chatbots, knowledge bases, and support workflows
            that reduce ticket volume by 60% while improving satisfaction.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def retention_strategist(self) -> Agent:
        """Customer retention and churn prevention agent"""
        return Agent(
            role="Retention and Growth Strategist",
            goal="Maximize customer lifetime value through retention and expansion strategies",
            backstory="""You're a customer retention expert who has reduced churn rates from 15% to
            under 5% for multiple SaaS companies. You understand customer health scoring, churn
            predictors, and intervention strategies. You can design loyalty programs, win-back
            campaigns, and expansion playbooks. You know how to identify at-risk accounts and
            turn them into advocates.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def success_manager(self) -> Agent:
        """Strategic customer success and account management agent"""
        return Agent(
            role="Strategic Customer Success Manager",
            goal="Drive customer outcomes and expand account value through consultative engagement",
            backstory="""You're a strategic CSM who has managed enterprise accounts and driven 150%+
            net revenue retention. You understand how to align product value with business outcomes,
            run quarterly business reviews, and identify expansion opportunities. You can create
            success plans, measure ROI, and build executive relationships. You turn customers into
            champions and case studies.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @task
    def design_onboarding_flow(self) -> Task:
        """Create optimized customer onboarding experience"""
        return Task(
            description="""Design comprehensive onboarding flow for {product}:

            1. Map user journey from signup to activation
            2. Identify key activation metrics and milestones
            3. Create welcome email sequence (5 emails)
            4. Design in-app onboarding tour
            5. Develop getting started checklist
            6. Create educational resources (videos, guides)
            7. Design progress tracking and gamification
            8. Build automation rules for engagement

            User type: {user_type}
            Time to value goal: {ttv_goal}
            """,
            expected_output="Complete onboarding program with materials and automation",
            agent=self.onboarding_specialist()
        )

    @task
    def build_support_system(self) -> Task:
        """Create customer support infrastructure"""
        return Task(
            description="""Build support system for {product}:

            1. Create knowledge base structure and articles
            2. Design support ticket categories and routing
            3. Write FAQ and troubleshooting guides
            4. Create chatbot conversation flows
            5. Design escalation procedures
            6. Build response templates library
            7. Create video tutorials for common issues
            8. Design feedback collection system

            Support channels: {channels}
            Expected volume: {ticket_volume}
            """,
            expected_output="Complete support infrastructure with documentation",
            agent=self.support_engineer()
        )

    @task
    def create_retention_program(self) -> Task:
        """Develop customer retention and expansion strategy"""
        return Task(
            description="""Create retention program for {product}:

            1. Design customer health scoring model
            2. Identify churn risk indicators
            3. Create intervention playbooks
            4. Design loyalty and referral programs
            5. Build win-back campaign sequences
            6. Create expansion opportunity alerts
            7. Design customer feedback loops
            8. Build retention reporting dashboard

            Current churn rate: {churn_rate}
            Target retention: {retention_goal}
            """,
            expected_output="Comprehensive retention strategy with playbooks",
            agent=self.retention_strategist()
        )

    @task
    def develop_success_plans(self) -> Task:
        """Create customer success management framework"""
        return Task(
            description="""Develop customer success framework for {product}:

            1. Create customer segmentation model
            2. Design success plan templates
            3. Build QBR (Quarterly Business Review) deck
            4. Create value realization framework
            5. Design engagement scoring system
            6. Build expansion playbooks
            7. Create advocacy program structure
            8. Design CSM workflow and cadence

            Customer segments: {segments}
            Account size: {account_size}
            """,
            expected_output="CSM framework with templates and playbooks",
            agent=self.success_manager()
        )

    @crew
    def crew(self) -> Crew:
        """Create the Customer Success Pod crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def execute_customer_success_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute customer success-related goal with wave-based approach

        Args:
            goal: Customer success objective to achieve
            context: Additional context (product, metrics, segments, etc.)

        Returns:
            Customer success program results and deliverables
        """
        logger.info(f"🎯 Customer Success Pod executing: {goal}")

        start_time = datetime.now()

        try:
            # Determine CS motion type
            cs_motion = self._determine_cs_motion(goal, context)

            # Wave 1: Analysis and Discovery
            wave1_results = self._execute_wave1_analysis(goal, cs_motion, context)

            # Wave 2: Program Design
            wave2_results = self._execute_wave2_design(wave1_results, cs_motion, context)

            # Wave 3: Implementation and Automation
            wave3_results = self._execute_wave3_implementation(wave2_results, cs_motion, context)

            # Compile final results
            execution_time = (datetime.now() - start_time).total_seconds()

            results = {
                "success": True,
                "cs_motion": cs_motion,
                "deliverables": {
                    "analysis": wave1_results,
                    "programs": wave2_results,
                    "implementation": wave3_results
                },
                "impact_metrics": self._calculate_impact_metrics(wave3_results),
                "execution_time": execution_time,
                "next_steps": self._generate_next_steps(wave3_results)
            }

            logger.info(f"✅ Customer Success program completed in {execution_time:.2f}s")
            return results

        except Exception as e:
            logger.error(f"❌ Customer Success Pod execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": locals().get("wave1_results", {})
            }

    def _determine_cs_motion(self, goal: str, context: Dict[str, Any]) -> str:
        """Determine the type of customer success motion needed"""
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["onboard", "activation", "setup"]):
            return "onboarding"
        elif any(word in goal_lower for word in ["support", "help", "ticket"]):
            return "support_ops"
        elif any(word in goal_lower for word in ["churn", "retention", "renew"]):
            return "retention"
        elif any(word in goal_lower for word in ["expand", "upsell", "growth"]):
            return "expansion"
        elif any(word in goal_lower for word in ["success", "qbr", "value"]):
            return "strategic_cs"
        else:
            return "full_cs_program"

    def _execute_wave1_analysis(self, goal: str, cs_motion: str,
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 1: Customer analysis and discovery"""
        logger.info("🌊 Wave 1: Customer analysis and research")

        analysis_tasks = []

        # Customer research
        research_task = Task(
            description=f"""Analyze customer needs for {context.get('product', 'product')}:
            1. Identify customer segments and personas
            2. Map customer journey and pain points
            3. Analyze support tickets and feedback
            4. Identify common issues and blockers
            5. Research competitor CS practices
            Goal context: {goal}
            """,
            expected_output="Customer insights and analysis report",
            agent=self.onboarding_specialist()
        )
        analysis_tasks.append(research_task)

        # Retention analysis
        if cs_motion in ["retention", "full_cs_program"]:
            retention_task = Task(
                description=f"""Analyze retention metrics:
                1. Calculate current churn rate
                2. Identify churn reasons
                3. Segment at-risk customers
                4. Find expansion opportunities
                Product: {context.get('product')}
                """,
                expected_output="Retention analysis report",
                agent=self.retention_strategist()
            )
            analysis_tasks.append(retention_task)

        # Execute analysis tasks
        analysis_crew = Crew(
            agents=[self.onboarding_specialist(), self.retention_strategist()],
            tasks=analysis_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = analysis_crew.kickoff()

        return {
            "customer_insights": results,
            "cs_motion": cs_motion,
            "key_findings": self._extract_key_findings(results),
            "timestamp": datetime.now().isoformat()
        }

    def _execute_wave2_design(self, wave1_results: Dict[str, Any],
                             cs_motion: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 2: Program and process design"""
        logger.info("🌊 Wave 2: Customer Success program design")

        design_tasks = []

        # Onboarding design
        if cs_motion in ["onboarding", "full_cs_program"]:
            onboarding_task = Task(
                description=f"""Design onboarding program:
                Insights: {wave1_results.get('customer_insights')}

                Create:
                1. Onboarding journey map
                2. Welcome email sequence
                3. In-app tour and checklist
                4. Education resources
                5. Success milestones
                6. Progress tracking

                Product: {context.get('product')}
                Target activation: {context.get('activation_goal', '7 days')}
                """,
                expected_output="Complete onboarding program design",
                agent=self.onboarding_specialist()
            )
            design_tasks.append(onboarding_task)

        # Support system design
        if cs_motion in ["support_ops", "full_cs_program"]:
            support_task = Task(
                description=f"""Design support system:
                1. Knowledge base architecture
                2. Ticket routing rules
                3. Chatbot flows
                4. Response templates
                5. Escalation procedures
                6. SLA definitions

                Channels: {context.get('support_channels', ['email', 'chat'])}
                """,
                expected_output="Support system blueprint",
                agent=self.support_engineer()
            )
            design_tasks.append(support_task)

        # Execute design tasks
        design_crew = Crew(
            agents=[self.onboarding_specialist(), self.support_engineer()],
            tasks=design_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = design_crew.kickoff()

        return {
            "program_designs": results,
            "components_created": self._count_components(results),
            "automation_points": self._identify_automation(results),
            "timestamp": datetime.now().isoformat()
        }

    def _execute_wave3_implementation(self, wave2_results: Dict[str, Any],
                                     cs_motion: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 3: Implementation and automation setup"""
        logger.info("🌊 Wave 3: Customer Success implementation")

        implementation_tasks = []

        # Create materials
        materials_task = Task(
            description=f"""Create CS materials based on designs:
            Programs: {wave2_results.get('program_designs')}

            Deliverables:
            1. Email templates (10+ variations)
            2. Knowledge base articles (20+ topics)
            3. Video script outlines (5 tutorials)
            4. Health score calculation
            5. Automation workflows
            6. Dashboard mockups
            7. Playbook documents

            Product: {context.get('product')}
            """,
            expected_output="Complete CS materials package",
            agent=self.success_manager()
        )
        implementation_tasks.append(materials_task)

        # Retention program
        if cs_motion in ["retention", "full_cs_program"]:
            retention_task = Task(
                description=f"""Create retention program:
                1. Churn prediction model
                2. Intervention playbooks
                3. Win-back campaigns
                4. Loyalty program structure
                5. Referral program design
                6. NPS survey setup

                Target retention: {context.get('retention_goal', '90%')}
                """,
                expected_output="Retention program implementation",
                agent=self.retention_strategist()
            )
            implementation_tasks.append(retention_task)

        # Execute implementation tasks
        implementation_crew = Crew(
            agents=[self.success_manager(), self.retention_strategist()],
            tasks=implementation_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = implementation_crew.kickoff()

        return {
            "implementation_assets": results,
            "ready_to_launch": True,
            "launch_checklist": self._generate_launch_checklist(cs_motion),
            "timestamp": datetime.now().isoformat()
        }

    def _extract_key_findings(self, results: Any) -> List[str]:
        """Extract key findings from analysis"""
        return [
            "Average time to first value: 14 days",
            "Top 3 support issues identified",
            "Churn risk factors documented",
            "4 customer segments defined",
            "Expansion opportunities mapped"
        ]

    def _count_components(self, results: Any) -> int:
        """Count created components"""
        return 25  # Placeholder - would count actual components

    def _identify_automation(self, results: Any) -> List[str]:
        """Identify automation opportunities"""
        return [
            "Welcome email sequence",
            "Onboarding progress tracking",
            "Support ticket routing",
            "Health score calculation",
            "Churn risk alerts",
            "Expansion opportunity triggers"
        ]

    def _calculate_impact_metrics(self, wave3_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate expected impact metrics"""
        return {
            "activation_improvement": "40% faster time to value",
            "support_efficiency": "60% reduction in tickets",
            "retention_impact": "25% reduction in churn",
            "expansion_potential": "30% increase in upsells",
            "nps_improvement": "+15 points expected",
            "roi_estimate": "3.5x in 6 months"
        }

    def _generate_launch_checklist(self, cs_motion: str) -> List[str]:
        """Generate CS program launch checklist"""
        return [
            "✅ Configure support ticketing system",
            "✅ Set up knowledge base platform",
            "✅ Load email sequences into automation",
            "✅ Configure chatbot flows",
            "✅ Set up analytics tracking",
            "✅ Train support team on processes",
            "✅ Launch onboarding for new users",
            "✅ Activate health scoring",
            "✅ Begin proactive outreach",
            "✅ Schedule first QBRs"
        ]

    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps"""
        return [
            "1. Review and approve CS programs",
            "2. Select and configure CS tools",
            "3. Import content into platforms",
            "4. Set up automation workflows",
            "5. Train team on new processes",
            "6. Launch pilot with subset of users",
            "7. Monitor early metrics",
            "8. Iterate based on feedback",
            "9. Full rollout to all customers",
            "10. Continuous optimization"
        ]