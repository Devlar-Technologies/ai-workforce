"""
Research Pod - Task Templates and Workflows
Predefined research tasks and workflows for market intelligence
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ResearchTaskTemplate:
    """Template for research tasks"""
    name: str
    description: str
    expected_output: str
    estimated_time: int  # minutes
    required_tools: List[str]
    success_criteria: List[str]

class ResearchTasks:
    """Research task templates and workflows for Devlar products"""

    def __init__(self):
        self.task_templates = self.create_task_templates()

    def create_task_templates(self) -> Dict[str, ResearchTaskTemplate]:
        """Create predefined research task templates"""

        templates = {
            "market_analysis": ResearchTaskTemplate(
                name="Market Analysis",
                description="Comprehensive market research and analysis for product positioning",
                expected_output="Market analysis report with size, trends, opportunities, and strategic recommendations",
                estimated_time=45,
                required_tools=["firecrawl_research", "apollo_prospecting"],
                success_criteria=[
                    "Market size and growth data identified",
                    "Key competitors and market share analyzed",
                    "User pain points and needs documented",
                    "Strategic opportunities identified",
                    "Actionable recommendations provided"
                ]
            ),

            "competitor_deep_dive": ResearchTaskTemplate(
                name="Competitive Deep Dive",
                description="In-depth analysis of competitors and competitive landscape",
                expected_output="Competitive intelligence matrix with feature gaps and positioning opportunities",
                estimated_time=60,
                required_tools=["firecrawl_research", "app_store_scraping"],
                success_criteria=[
                    "Top 10 competitors identified and analyzed",
                    "Feature comparison matrix created",
                    "Pricing and business model analysis completed",
                    "Differentiation opportunities identified",
                    "Competitive positioning recommendations provided"
                ]
            ),

            "user_research": ResearchTaskTemplate(
                name="User Research",
                description="Research target user personas and their workflows",
                expected_output="User persona profiles with pain points and feature requirements",
                estimated_time=40,
                required_tools=["firecrawl_research", "social_media_analysis"],
                success_criteria=[
                    "Detailed user personas created",
                    "User workflows and pain points mapped",
                    "Feature priorities identified",
                    "User decision-making processes understood",
                    "Actionable product insights generated"
                ]
            ),

            "trend_analysis": ResearchTaskTemplate(
                name="Trend Analysis",
                description="Identify and analyze emerging trends in target market",
                expected_output="Trend analysis report with implications for product strategy",
                estimated_time=30,
                required_tools=["firecrawl_research", "social_media_analysis"],
                success_criteria=[
                    "Emerging trends identified and validated",
                    "Trend impact on target market assessed",
                    "Opportunities and threats evaluated",
                    "Strategic implications analyzed",
                    "Trend-based recommendations provided"
                ]
            ),

            "chromentum_market_research": ResearchTaskTemplate(
                name="Chromentum Market Research",
                description="Specialized market research for Chrome extension productivity tools",
                expected_output="Chromentum-specific market analysis with user acquisition strategies",
                estimated_time=50,
                required_tools=["firecrawl_research", "chrome_web_store_analysis"],
                success_criteria=[
                    "Chrome extension market size and trends analyzed",
                    "Productivity extension user behavior studied",
                    "Momentum, Todoist, and similar tools analyzed",
                    "User acquisition channels for extensions identified",
                    "Feature differentiation opportunities found"
                ]
            ),

            "zeneural_meditation_research": ResearchTaskTemplate(
                name="Zeneural Meditation App Research",
                description="Research AI meditation and wellness app market for Zeneural positioning",
                expected_output="Meditation app market analysis with AI integration opportunities",
                estimated_time=45,
                required_tools=["firecrawl_research", "app_store_scraping"],
                success_criteria=[
                    "AI meditation app landscape mapped",
                    "Headspace, Calm, Insight Timer analyzed",
                    "AI personalization opportunities identified",
                    "Video-based meditation market assessed",
                    "Zeneural differentiation strategy developed"
                ]
            )
        }

        return templates

    def get_task_for_goal(self, goal: str) -> str:
        """Determine appropriate research task based on goal"""

        goal_lower = goal.lower()

        # Chromentum-related goals
        if "chromentum" in goal_lower or "chrome extension" in goal_lower:
            if "beta users" in goal_lower or "users" in goal_lower:
                return "chromentum_market_research"
            else:
                return "market_analysis"

        # Zeneural-related goals
        elif "zeneural" in goal_lower or "meditation" in goal_lower:
            return "zeneural_meditation_research"

        # General market research
        elif "research" in goal_lower and "competitor" in goal_lower:
            return "competitor_deep_dive"

        elif "user" in goal_lower and "research" in goal_lower:
            return "user_research"

        elif "trend" in goal_lower or "market trend" in goal_lower:
            return "trend_analysis"

        # Default to general market analysis
        else:
            return "market_analysis"

    def create_research_workflow(self, product: str, goal: str) -> Dict[str, Any]:
        """Create custom research workflow based on product and goal"""

        workflow = {
            "product": product,
            "goal": goal,
            "tasks": [],
            "estimated_time": 0
        }

        # Determine task sequence based on product and goal
        if "chromentum" in product.lower():
            if "beta users" in goal.lower():
                # User acquisition workflow
                workflow["tasks"] = [
                    "chromentum_market_research",
                    "user_research",
                    "competitor_deep_dive"
                ]
            else:
                # General product research
                workflow["tasks"] = [
                    "market_analysis",
                    "chromentum_market_research"
                ]

        elif "zeneural" in product.lower():
            workflow["tasks"] = [
                "zeneural_meditation_research",
                "trend_analysis",
                "user_research"
            ]

        else:
            # Default research workflow
            workflow["tasks"] = [
                "market_analysis",
                "competitor_deep_dive",
                "user_research"
            ]

        # Calculate estimated time
        for task_name in workflow["tasks"]:
            if task_name in self.task_templates:
                workflow["estimated_time"] += self.task_templates[task_name].estimated_time

        return workflow

    def get_research_parameters(self, product: str, goal: str) -> Dict[str, Any]:
        """Generate research parameters based on product and goal"""

        base_params = {
            "product": product,
            "goal": goal,
            "market_segment": "productivity tools",
            "audience": "professionals and creators"
        }

        # Product-specific parameters
        if "chromentum" in product.lower():
            base_params.update({
                "market_segment": "browser productivity extensions",
                "competitors": [
                    "Momentum",
                    "Todoist (Chrome extension)",
                    "StayFocused",
                    "Forest",
                    "RescueTime"
                ],
                "channels": ["Chrome Web Store", "Product Hunt", "Reddit", "LinkedIn"],
                "audience": "productivity-focused professionals",
                "features": ["new tab dashboard", "time tracking", "weather", "backgrounds"]
            })

        elif "zeneural" in product.lower():
            base_params.update({
                "market_segment": "AI meditation and wellness apps",
                "competitors": [
                    "Headspace",
                    "Calm",
                    "Insight Timer",
                    "Ten Percent Happier",
                    "Waking Up"
                ],
                "channels": ["App Store", "Google Play", "Wellness communities", "YouTube"],
                "audience": "wellness-focused professionals and creators",
                "features": ["AI-generated content", "personalized meditation", "video format", "affirmations"]
            })

        elif "timepost" in product.lower():
            base_params.update({
                "market_segment": "social media management tools",
                "competitors": ["Buffer", "Hootsuite", "Later", "Sprout Social"],
                "audience": "content creators and social media managers"
            })

        elif "aimstack" in product.lower():
            base_params.update({
                "market_segment": "AI development frameworks",
                "competitors": ["LangChain", "LlamaIndex", "AutoGen", "CrewAI"],
                "audience": "AI developers and engineers"
            })

        return base_params

    def validate_research_results(self, task_name: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research results against success criteria"""

        if task_name not in self.task_templates:
            return {"valid": False, "reason": "Unknown task template"}

        template = self.task_templates[task_name]
        validation = {
            "valid": True,
            "score": 0,
            "missing_criteria": [],
            "recommendations": []
        }

        # Check success criteria (simplified validation)
        results_text = str(results).lower()

        for criterion in template.success_criteria:
            criterion_keywords = criterion.lower().split()
            if any(keyword in results_text for keyword in criterion_keywords):
                validation["score"] += 1
            else:
                validation["missing_criteria"].append(criterion)

        # Calculate score percentage
        total_criteria = len(template.success_criteria)
        validation["score_percentage"] = (validation["score"] / total_criteria) * 100

        # Determine validity
        validation["valid"] = validation["score_percentage"] >= 70  # 70% threshold

        # Add recommendations if needed
        if validation["score_percentage"] < 100:
            validation["recommendations"].append("Consider gathering additional data for missing criteria")

        if validation["score_percentage"] < 70:
            validation["recommendations"].append("Results may need significant improvement before use")

        return validation