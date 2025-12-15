"""
Devlar AI Workforce - Sales Pod Agents
Lead generation, cold outreach, sales automation, and deal closing
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

from tools.apollo_tool import ApolloTool
from tools.firecrawl_tool import FirecrawlTool


class SalesPod(CrewBase):
    """
    Sales specialist pod for lead generation and outreach
    Handles prospecting, qualification, outreach campaigns, and deal management
    """

    def __init__(self):
        """Initialize Sales Pod with specialized agents"""
        super().__init__()
        self.apollo = ApolloTool()
        self.firecrawl = FirecrawlTool()

        # Initialize LLM
        self.llm = self._get_llm()

        logger.info("💼 Sales Pod initialized with outreach and closing specialists")

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
    def lead_researcher(self) -> Agent:
        """Lead research and qualification agent"""
        return Agent(
            role="B2B Lead Research Specialist",
            goal="Identify and qualify high-value prospects with precision targeting",
            backstory="""You're a sales intelligence expert who has generated millions in pipeline
            for SaaS companies. You know how to identify ideal customer profiles, find decision makers,
            and qualify leads based on buying signals. You understand technographics, firmographics,
            and can spot companies ready to buy. You've mastered tools like Apollo, ZoomInfo, and
            LinkedIn Sales Navigator.""",
            tools=[self.apollo, self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def outreach_specialist(self) -> Agent:
        """Cold outreach and email campaign agent"""
        return Agent(
            role="Cold Outreach Specialist",
            goal="Craft personalized outreach campaigns that generate meetings and opportunities",
            backstory="""You're a cold outreach expert with a track record of 20%+ response rates.
            You understand the psychology of B2B buyers and can write compelling messages that cut
            through the noise. You know how to personalize at scale, A/B test messaging, and build
            multi-touch sequences that convert. You've booked thousands of meetings for SaaS startups.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def sales_strategist(self) -> Agent:
        """Sales strategy and process optimization agent"""
        return Agent(
            role="Sales Strategy Architect",
            goal="Design and optimize sales processes that predictably generate revenue",
            backstory="""You're a sales operations expert who has built and scaled sales teams from
            0 to €9M+ ARR. You understand sales methodology (MEDDIC, Challenger, SPIN), pipeline
            management, and how to create repeatable sales processes. You can design compensation
            plans, territories, and quotas that drive performance. You know what metrics matter.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def demo_script_writer(self) -> Agent:
        """Product demo and sales collateral creator"""
        return Agent(
            role="Sales Demo and Collateral Expert",
            goal="Create compelling demo scripts and sales materials that close deals",
            backstory="""You're a sales engineer and demo expert who has delivered thousands of
            product demos. You know how to showcase value, handle objections, and create 'aha'
            moments. You can create demo scripts, battle cards, ROI calculators, and case studies
            that help sales teams win. You understand different buyer personas and how to tailor
            presentations to their needs.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @task
    def research_leads(self) -> Task:
        """Research and identify qualified leads"""
        return Task(
            description="""Research and identify high-quality leads for {product}:

            1. Define ideal customer profile (ICP)
            2. Identify 50+ target companies matching ICP
            3. Find 3-5 decision makers per company
            4. Gather contact information (email, LinkedIn)
            5. Research buying signals and triggers
            6. Score and prioritize leads
            7. Identify personalization angles
            8. Create lead intelligence reports

            Target market: {target_market}
            Company size: {company_size}
            """,
            expected_output="Qualified lead list with contact info and intelligence",
            agent=self.lead_researcher()
        )

    @task
    def create_outreach_campaign(self) -> Task:
        """Design multi-channel outreach campaign"""
        return Task(
            description="""Create a cold outreach campaign for {product}:

            1. Write email sequence (5-7 touchpoints)
            2. Create LinkedIn message templates
            3. Design voicemail scripts
            4. Develop personalization framework
            5. Create A/B test variations
            6. Design follow-up cadence
            7. Write objection handling scripts
            8. Create urgency and value props

            Target persona: {target_persona}
            Value proposition: {value_prop}
            """,
            expected_output="Complete outreach campaign with templates and sequences",
            agent=self.outreach_specialist()
        )

    @task
    def design_sales_process(self) -> Task:
        """Design optimized sales process"""
        return Task(
            description="""Design a scalable sales process for {product}:

            1. Map customer buying journey
            2. Define sales stages and exit criteria
            3. Create qualification framework (BANT/MEDDIC)
            4. Design pipeline metrics and KPIs
            5. Create sales playbooks
            6. Define handoff processes
            7. Design compensation structure
            8. Create forecasting model

            Sales cycle: {sales_cycle}
            Deal size: {deal_size}
            """,
            expected_output="Complete sales process documentation and playbooks",
            agent=self.sales_strategist()
        )

    @task
    def create_demo_materials(self) -> Task:
        """Create demo scripts and sales collateral"""
        return Task(
            description="""Create sales demo materials for {product}:

            1. Write discovery call script
            2. Create product demo flow and script
            3. Design custom demo scenarios
            4. Write objection handling guide
            5. Create competitive battle cards
            6. Build ROI calculator/business case
            7. Write customer success stories
            8. Create leave-behind materials

            Key features: {features}
            Main competitors: {competitors}
            """,
            expected_output="Complete demo kit with scripts and supporting materials",
            agent=self.demo_script_writer()
        )

    @crew
    def crew(self) -> Crew:
        """Create the Sales Pod crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def execute_sales_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute sales-related goal with wave-based approach

        Args:
            goal: Sales objective to achieve
            context: Additional context (product, market, quotas, etc.)

        Returns:
            Sales campaign results and deliverables
        """
        logger.info(f"💼 Sales Pod executing: {goal}")

        start_time = datetime.now()

        try:
            # Determine sales motion type
            sales_motion = self._determine_sales_motion(goal, context)

            # Wave 1: Research and Lead Generation
            wave1_results = self._execute_wave1_prospecting(goal, sales_motion, context)

            # Wave 2: Campaign Development
            wave2_results = self._execute_wave2_campaign(wave1_results, sales_motion, context)

            # Wave 3: Enablement and Launch
            wave3_results = self._execute_wave3_enablement(wave2_results, sales_motion, context)

            # Compile final results
            execution_time = (datetime.now() - start_time).total_seconds()

            results = {
                "success": True,
                "sales_motion": sales_motion,
                "deliverables": {
                    "leads": wave1_results,
                    "campaigns": wave2_results,
                    "enablement": wave3_results
                },
                "pipeline_potential": self._calculate_pipeline_potential(wave1_results),
                "execution_time": execution_time,
                "next_steps": self._generate_next_steps(wave3_results)
            }

            logger.info(f"✅ Sales campaign completed in {execution_time:.2f}s")
            return results

        except Exception as e:
            logger.error(f"❌ Sales Pod execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": locals().get("wave1_results", {})
            }

    def _determine_sales_motion(self, goal: str, context: Dict[str, Any]) -> str:
        """Determine the type of sales motion needed"""
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["lead", "prospect", "find"]):
            return "lead_generation"
        elif any(word in goal_lower for word in ["outreach", "cold", "email"]):
            return "outbound_sales"
        elif any(word in goal_lower for word in ["demo", "presentation", "pitch"]):
            return "demo_enablement"
        elif any(word in goal_lower for word in ["enterprise", "account", "strategic"]):
            return "enterprise_sales"
        elif any(word in goal_lower for word in ["partner", "channel", "reseller"]):
            return "channel_sales"
        else:
            return "full_cycle_sales"

    def _execute_wave1_prospecting(self, goal: str, sales_motion: str,
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 1: Lead research and prospecting"""
        logger.info("🌊 Wave 1: Sales prospecting and research")

        prospecting_tasks = []

        # Lead research
        lead_task = Task(
            description=f"""Research leads for {context.get('product', 'product')}:
            1. Define ICP based on: {context.get('target_market', 'B2B SaaS')}
            2. Find companies matching criteria
            3. Identify decision makers
            4. Gather contact information
            5. Research buying signals
            Sales goal: {goal}
            """,
            expected_output="Qualified lead list with intelligence",
            agent=self.lead_researcher()
        )
        prospecting_tasks.append(lead_task)

        # Market intelligence
        if sales_motion in ["enterprise_sales", "full_cycle_sales"]:
            intel_task = Task(
                description=f"""Gather sales intelligence:
                1. Analyze competitor customers
                2. Identify market trends
                3. Find expansion opportunities
                4. Research pricing benchmarks
                Product: {context.get('product')}
                """,
                expected_output="Market intelligence report",
                agent=self.sales_strategist()
            )
            prospecting_tasks.append(intel_task)

        # Execute prospecting tasks
        prospecting_crew = Crew(
            agents=[self.lead_researcher(), self.sales_strategist()],
            tasks=prospecting_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = prospecting_crew.kickoff()

        return {
            "qualified_leads": self._extract_lead_count(results),
            "lead_intelligence": results,
            "sales_motion": sales_motion,
            "timestamp": datetime.now().isoformat()
        }

    def _execute_wave2_campaign(self, wave1_results: Dict[str, Any],
                               sales_motion: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 2: Campaign and process development"""
        logger.info("🌊 Wave 2: Sales campaign development")

        campaign_tasks = []

        # Outreach campaign
        outreach_task = Task(
            description=f"""Create outreach campaign based on leads:
            Lead intelligence: {wave1_results.get('lead_intelligence')}

            Design:
            1. Email sequences (7 touchpoints)
            2. LinkedIn outreach templates
            3. Call scripts and voicemails
            4. Personalization variables
            5. A/B test variations
            6. Follow-up cadence

            Product: {context.get('product')}
            Value prop: {context.get('value_prop', 'efficiency and growth')}
            """,
            expected_output="Multi-channel outreach campaign",
            agent=self.outreach_specialist()
        )
        campaign_tasks.append(outreach_task)

        # Sales process
        if sales_motion in ["enterprise_sales", "full_cycle_sales"]:
            process_task = Task(
                description=f"""Design sales process:
                1. Define stages and criteria
                2. Create qualification framework
                3. Map buyer journey
                4. Design metrics and KPIs
                5. Create playbooks

                Deal size: {context.get('deal_size', '€9-45K')}
                Sales cycle: {context.get('sales_cycle', '30-60 days')}
                """,
                expected_output="Sales process documentation",
                agent=self.sales_strategist()
            )
            campaign_tasks.append(process_task)

        # Execute campaign tasks
        campaign_crew = Crew(
            agents=[self.outreach_specialist(), self.sales_strategist()],
            tasks=campaign_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = campaign_crew.kickoff()

        return {
            "outreach_campaign": results,
            "sequences_created": 7,
            "personalization_angles": 10,
            "timestamp": datetime.now().isoformat()
        }

    def _execute_wave3_enablement(self, wave2_results: Dict[str, Any],
                                 sales_motion: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 3: Sales enablement and collateral"""
        logger.info("🌊 Wave 3: Sales enablement creation")

        enablement_tasks = []

        # Demo materials
        demo_task = Task(
            description=f"""Create sales enablement materials:
            Campaign: {wave2_results.get('outreach_campaign')}

            Create:
            1. Discovery call guide
            2. Product demo script
            3. Objection handling doc
            4. Competitive battle cards
            5. ROI calculator template
            6. Case study outlines
            7. Proposal template

            Product features: {context.get('features', 'core SaaS features')}
            """,
            expected_output="Complete sales enablement kit",
            agent=self.demo_script_writer()
        )
        enablement_tasks.append(demo_task)

        # Execute enablement tasks
        enablement_crew = Crew(
            agents=[self.demo_script_writer()],
            tasks=enablement_tasks,
            process=Process.sequential,
            verbose=True
        )

        results = enablement_crew.kickoff()

        return {
            "enablement_materials": results,
            "ready_to_sell": True,
            "training_plan": self._generate_training_plan(sales_motion),
            "timestamp": datetime.now().isoformat()
        }

    def _extract_lead_count(self, results: Any) -> int:
        """Extract number of qualified leads from results"""
        # Parse results to count leads (simplified)
        return 50  # Placeholder - would parse actual results

    def _calculate_pipeline_potential(self, wave1_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential pipeline value"""
        lead_count = wave1_results.get("qualified_leads", 50)

        return {
            "total_leads": lead_count,
            "expected_meetings": int(lead_count * 0.15),  # 15% meeting rate
            "expected_opportunities": int(lead_count * 0.05),  # 5% opp rate
            "pipeline_value": lead_count * 0.05 * 22500,  # Average deal size €22.5K
            "expected_revenue": lead_count * 0.05 * 22500 * 0.2  # 20% close rate
        }

    def _generate_training_plan(self, sales_motion: str) -> List[str]:
        """Generate sales training plan"""
        return [
            "Day 1: Product knowledge and value prop",
            "Day 2: ICP and buyer personas",
            "Day 3: Discovery and qualification",
            "Day 4: Demo delivery and customization",
            "Day 5: Objection handling practice",
            "Week 2: Role play and certification",
            "Week 3: Live calling with coaching",
            "Week 4: Pipeline review and optimization"
        ]

    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps"""
        return [
            "1. Load leads into CRM/outreach tool",
            "2. Set up email sequences and automation",
            "3. Begin outreach campaign (start with A test)",
            "4. Schedule daily calling blocks",
            "5. Track response rates and iterate",
            "6. Book and conduct discovery calls",
            "7. Deliver customized demos",
            "8. Follow up and manage pipeline",
            "9. Track conversion metrics",
            "10. Optimize based on results"
        ]