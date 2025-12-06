"""
Devlar AI Workforce - Marketing Pod Agents
Content creation, campaign management, SEO optimization, and growth hacking
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
from tools.flux_tool import FluxImageTool


class MarketingPod(CrewBase):
    """
    Marketing specialist pod for campaigns, content, and growth
    Handles user acquisition, brand building, and marketing automation
    """

    def __init__(self):
        """Initialize Marketing Pod with specialized agents"""
        super().__init__()
        self.firecrawl = FirecrawlTool()
        self.flux = FluxImageTool()

        # Initialize LLM
        self.llm = self._get_llm()

        logger.info("📈 Marketing Pod initialized with campaign and content specialists")

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
    def content_strategist(self) -> Agent:
        """Content strategy and planning agent"""
        return Agent(
            role="Content Marketing Strategist",
            goal="Create compelling content strategies that drive engagement and conversions",
            backstory="""You're a content marketing expert who understands how to create value-driven
            content that resonates with target audiences. You've managed content for successful SaaS
            companies and understand the balance between education and promotion. You know how to
            create content calendars, identify trending topics, and optimize for SEO while maintaining
            authentic brand voice.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def campaign_manager(self) -> Agent:
        """Marketing campaign planning and execution agent"""
        return Agent(
            role="Digital Campaign Manager",
            goal="Design and execute multi-channel marketing campaigns that drive measurable results",
            backstory="""You're a data-driven campaign manager who has launched successful marketing
            campaigns for tech startups. You understand funnel optimization, A/B testing, and how to
            coordinate campaigns across email, social, paid ads, and content marketing. You focus on
            ROI and can adapt strategies based on performance metrics.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def social_media_expert(self) -> Agent:
        """Social media marketing and community building agent"""
        return Agent(
            role="Social Media Growth Expert",
            goal="Build engaged communities and drive viral growth through social media",
            backstory="""You're a social media strategist who has grown multiple brands from zero to
            100K+ followers. You understand platform-specific best practices, viral content mechanics,
            and community engagement. You can create compelling social content, identify influencers,
            and build authentic relationships that drive organic growth.""",
            tools=[self.flux],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @agent
    def seo_specialist(self) -> Agent:
        """SEO and organic growth optimization agent"""
        return Agent(
            role="SEO and Organic Growth Specialist",
            goal="Optimize for search visibility and drive sustainable organic traffic",
            backstory="""You're an SEO expert who has helped startups achieve first-page rankings for
            competitive keywords. You understand technical SEO, content optimization, link building,
            and how to track and improve search performance. You stay current with algorithm updates
            and can identify quick wins alongside long-term strategies.""",
            tools=[self.firecrawl],
            llm=self.llm,
            max_iter=5,
            verbose=True
        )

    @task
    def create_content_strategy(self) -> Task:
        """Develop comprehensive content marketing strategy"""
        return Task(
            description="""Create a detailed content marketing strategy including:

            1. Target audience analysis and personas
            2. Content pillars and themes
            3. Content calendar for next 3 months
            4. Distribution channels and promotion tactics
            5. KPIs and success metrics
            6. SEO keyword opportunities
            7. Content formats (blog, video, podcast, etc.)

            Focus on {product} for {target_audience}.
            """,
            expected_output="Comprehensive content strategy document with calendar and guidelines",
            agent=self.content_strategist()
        )

    @task
    def design_acquisition_campaign(self) -> Task:
        """Design user acquisition campaign"""
        return Task(
            description="""Design a multi-channel user acquisition campaign including:

            1. Campaign objectives and target metrics
            2. Channel strategy (paid, organic, referral)
            3. Messaging and creative concepts
            4. Landing page optimization recommendations
            5. Email nurture sequences
            6. Budget allocation across channels
            7. A/B testing framework
            8. Performance tracking setup

            Goal: Acquire {user_goal} for {product}.
            """,
            expected_output="Complete campaign plan with assets, timelines, and budgets",
            agent=self.campaign_manager()
        )

    @task
    def create_social_strategy(self) -> Task:
        """Develop social media growth strategy"""
        return Task(
            description="""Create a social media strategy to build community and drive growth:

            1. Platform selection and prioritization
            2. Content themes and posting schedule
            3. Community engagement tactics
            4. Influencer partnership opportunities
            5. Viral content ideas and hooks
            6. User-generated content campaigns
            7. Social listening and response protocols
            8. Growth hacking tactics

            Focus on growing {product} presence on {platforms}.
            """,
            expected_output="Social media playbook with content calendar and growth tactics",
            agent=self.social_media_expert()
        )

    @task
    def optimize_seo_performance(self) -> Task:
        """Optimize SEO and organic search performance"""
        return Task(
            description="""Conduct SEO audit and create optimization plan:

            1. Technical SEO audit and fixes
            2. Keyword research and opportunity analysis
            3. Content gap analysis vs competitors
            4. On-page optimization recommendations
            5. Link building strategy
            6. Local SEO optimization (if applicable)
            7. Schema markup implementation
            8. Performance tracking setup

            Optimize {website} for target keywords: {keywords}.
            """,
            expected_output="SEO audit report with prioritized optimization roadmap",
            agent=self.seo_specialist()
        )

    @crew
    def crew(self) -> Crew:
        """Create the Marketing Pod crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

    def execute_marketing_goal(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute marketing-related goal with wave-based approach

        Args:
            goal: Marketing objective to achieve
            context: Additional context (product, audience, budget, etc.)

        Returns:
            Marketing campaign results and deliverables
        """
        logger.info(f"📈 Marketing Pod executing: {goal}")

        start_time = datetime.now()

        try:
            # Determine campaign type
            campaign_type = self._determine_campaign_type(goal, context)

            # Wave 1: Research and Analysis
            wave1_results = self._execute_wave1_research(goal, campaign_type, context)

            # Wave 2: Strategy and Planning
            wave2_results = self._execute_wave2_strategy(wave1_results, campaign_type, context)

            # Wave 3: Content Creation and Launch Prep
            wave3_results = self._execute_wave3_creation(wave2_results, campaign_type, context)

            # Compile final results
            execution_time = (datetime.now() - start_time).total_seconds()

            results = {
                "success": True,
                "campaign_type": campaign_type,
                "deliverables": {
                    "research": wave1_results,
                    "strategy": wave2_results,
                    "assets": wave3_results
                },
                "execution_time": execution_time,
                "next_steps": self._generate_next_steps(wave3_results)
            }

            logger.info(f"✅ Marketing campaign completed in {execution_time:.2f}s")
            return results

        except Exception as e:
            logger.error(f"❌ Marketing Pod execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "partial_results": locals().get("wave1_results", {})
            }

    def _determine_campaign_type(self, goal: str, context: Dict[str, Any]) -> str:
        """Determine the type of marketing campaign needed"""
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["acquire", "users", "signups", "beta"]):
            return "user_acquisition"
        elif any(word in goal_lower for word in ["content", "blog", "seo"]):
            return "content_marketing"
        elif any(word in goal_lower for word in ["social", "twitter", "linkedin"]):
            return "social_media"
        elif any(word in goal_lower for word in ["launch", "product", "release"]):
            return "product_launch"
        elif any(word in goal_lower for word in ["brand", "awareness", "recognition"]):
            return "brand_awareness"
        else:
            return "integrated_campaign"

    def _execute_wave1_research(self, goal: str, campaign_type: str,
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 1: Market research and competitive analysis"""
        logger.info("🌊 Wave 1: Marketing research and analysis")

        research_tasks = []

        # Market research
        market_task = Task(
            description=f"""Research the market for {context.get('product', 'product')}:
            1. Identify target audience segments
            2. Analyze competitor marketing strategies
            3. Find successful campaign examples
            4. Identify key messaging themes
            5. Discover channel preferences
            Goal context: {goal}
            """,
            expected_output="Market research report with insights",
            agent=self.content_strategist()
        )
        research_tasks.append(market_task)

        # SEO research
        if campaign_type in ["content_marketing", "integrated_campaign"]:
            seo_task = Task(
                description=f"""Conduct SEO research for {context.get('product', 'product')}:
                1. Identify high-value keywords
                2. Analyze search intent
                3. Find content gaps
                4. Assess competition difficulty
                """,
                expected_output="SEO opportunity analysis",
                agent=self.seo_specialist()
            )
            research_tasks.append(seo_task)

        # Execute research tasks
        research_crew = Crew(
            agents=[self.content_strategist(), self.seo_specialist()],
            tasks=research_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = research_crew.kickoff()

        return {
            "market_insights": results,
            "campaign_type": campaign_type,
            "timestamp": datetime.now().isoformat()
        }

    def _execute_wave2_strategy(self, wave1_results: Dict[str, Any],
                               campaign_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 2: Strategy development and planning"""
        logger.info("🌊 Wave 2: Marketing strategy development")

        strategy_tasks = []

        # Campaign strategy
        campaign_task = Task(
            description=f"""Design marketing campaign based on research:
            Research insights: {wave1_results.get('market_insights')}

            Create:
            1. Campaign objectives and KPIs
            2. Channel strategy and budget allocation
            3. Content calendar (3 months)
            4. Messaging framework
            5. Creative concepts
            6. Launch timeline

            Product: {context.get('product', 'product')}
            Budget: {context.get('budget', 'flexible')}
            """,
            expected_output="Complete campaign strategy document",
            agent=self.campaign_manager()
        )
        strategy_tasks.append(campaign_task)

        # Social media strategy
        if campaign_type in ["social_media", "integrated_campaign", "user_acquisition"]:
            social_task = Task(
                description=f"""Create social media strategy:
                1. Platform-specific content plans
                2. Posting schedule and frequency
                3. Engagement tactics
                4. Influencer outreach list
                5. Community building approach

                Product: {context.get('product')}
                Target platforms: {context.get('platforms', ['Twitter', 'LinkedIn'])}
                """,
                expected_output="Social media playbook",
                agent=self.social_media_expert()
            )
            strategy_tasks.append(social_task)

        # Execute strategy tasks
        strategy_crew = Crew(
            agents=[self.campaign_manager(), self.social_media_expert()],
            tasks=strategy_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = strategy_crew.kickoff()

        return {
            "campaign_strategy": results,
            "channels": self._identify_channels(campaign_type),
            "timeline": self._generate_timeline(campaign_type),
            "timestamp": datetime.now().isoformat()
        }

    def _execute_wave3_creation(self, wave2_results: Dict[str, Any],
                               campaign_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Wave 3: Content creation and asset development"""
        logger.info("🌊 Wave 3: Marketing asset creation")

        creation_tasks = []

        # Content creation
        content_task = Task(
            description=f"""Create marketing content based on strategy:
            Strategy: {wave2_results.get('campaign_strategy')}

            Deliverables:
            1. 5 blog post outlines with SEO optimization
            2. 10 social media post templates
            3. 3 email sequences (welcome, nurture, conversion)
            4. Landing page copy and structure
            5. Ad copy variations (5 headlines, 5 descriptions)

            Brand voice: {context.get('brand_voice', 'professional and approachable')}
            """,
            expected_output="Marketing content package",
            agent=self.content_strategist()
        )
        creation_tasks.append(content_task)

        # Visual assets
        if context.get('create_visuals', True):
            visual_task = Task(
                description=f"""Design visual content concepts:
                1. Social media image templates (5 designs)
                2. Blog post hero images (3 concepts)
                3. Ad creative concepts (3 variations)
                4. Infographic ideas (2 concepts)

                Brand: {context.get('product')}
                Style: {context.get('visual_style', 'modern and clean')}
                """,
                expected_output="Visual content specifications",
                agent=self.social_media_expert()
            )
            creation_tasks.append(visual_task)

        # Execute creation tasks
        creation_crew = Crew(
            agents=[self.content_strategist(), self.social_media_expert()],
            tasks=creation_tasks,
            process=Process.parallel,
            verbose=True
        )

        results = creation_crew.kickoff()

        return {
            "content_assets": results,
            "ready_to_launch": True,
            "implementation_checklist": self._generate_checklist(campaign_type),
            "timestamp": datetime.now().isoformat()
        }

    def _identify_channels(self, campaign_type: str) -> List[str]:
        """Identify marketing channels for campaign"""
        channels_map = {
            "user_acquisition": ["paid_search", "social_ads", "content", "email", "referral"],
            "content_marketing": ["blog", "seo", "social_organic", "email", "youtube"],
            "social_media": ["twitter", "linkedin", "instagram", "tiktok", "community"],
            "product_launch": ["email", "social", "pr", "influencers", "paid_ads"],
            "brand_awareness": ["social", "content", "pr", "partnerships", "events"],
            "integrated_campaign": ["paid_ads", "social", "content", "email", "seo", "pr"]
        }
        return channels_map.get(campaign_type, ["social", "content", "email"])

    def _generate_timeline(self, campaign_type: str) -> Dict[str, Any]:
        """Generate campaign timeline"""
        return {
            "week_1": ["Campaign setup", "Asset creation", "Platform configuration"],
            "week_2": ["Soft launch", "A/B testing", "Initial outreach"],
            "week_3-4": ["Full launch", "Optimization", "Scaling"],
            "month_2": ["Expansion", "Iteration", "Community building"],
            "month_3": ["Analysis", "Optimization", "Planning next phase"]
        }

    def _generate_checklist(self, campaign_type: str) -> List[str]:
        """Generate implementation checklist"""
        return [
            "✅ Set up tracking and analytics",
            "✅ Configure marketing automation tools",
            "✅ Create landing pages and forms",
            "✅ Schedule social media posts",
            "✅ Set up email sequences",
            "✅ Launch paid ad campaigns",
            "✅ Brief team on campaign goals",
            "✅ Set up monitoring dashboards",
            "✅ Prepare crisis management plan",
            "✅ Schedule review meetings"
        ]

    def _generate_next_steps(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps"""
        return [
            "1. Review and approve campaign strategy",
            "2. Allocate budget across channels",
            "3. Set up marketing tools and platforms",
            "4. Create visual assets based on specs",
            "5. Launch pilot campaign for testing",
            "6. Monitor initial performance metrics",
            "7. Optimize based on early results",
            "8. Scale successful channels",
            "9. Build community engagement",
            "10. Plan follow-up campaigns"
        ]