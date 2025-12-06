"""
Product Development Pod - Task Templates and Development Workflows
Complete development pipeline from ideation to deployment
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class DevTaskTemplate:
    """Template for development tasks"""
    name: str
    description: str
    expected_output: str
    estimated_time: int  # minutes
    required_tools: List[str]
    success_criteria: List[str]
    agents_involved: List[str]
    wave_structure: Dict[str, Any]

class ProductDevTasks:
    """Product development task templates for Devlar's tech stack"""

    def __init__(self):
        self.task_templates = self.create_dev_templates()

    def create_dev_templates(self) -> Dict[str, DevTaskTemplate]:
        """Create development task templates for Devlar products"""

        templates = {
            "feature_ideation": DevTaskTemplate(
                name="Feature Ideation",
                description="Generate and prioritize innovative features based on market research",
                expected_output="Prioritized feature roadmap with detailed specifications and success metrics",
                estimated_time=60,
                required_tools=[],
                success_criteria=[
                    "3-5 feature ideas generated",
                    "Features prioritized by impact and feasibility",
                    "Detailed specifications with user stories",
                    "Technical requirements defined",
                    "Success metrics established",
                    "Timeline estimates provided"
                ],
                agents_involved=["product_ideator"],
                wave_structure={
                    "wave_1": ["product_ideator"],
                    "dependencies": {}
                }
            ),

            "technical_implementation": DevTaskTemplate(
                name="Technical Implementation",
                description="Complete development pipeline from specification to deployment",
                expected_output="Production-ready feature with tests, documentation, and deployment",
                estimated_time=180,
                required_tools=["github_management", "vercel_deployment"],
                success_criteria=[
                    "Feature specification refined and approved",
                    "Production-ready code implemented",
                    "Comprehensive testing completed",
                    "QA approval obtained",
                    "Deployment pipeline configured",
                    "Feature successfully deployed",
                    "Monitoring and alerts configured"
                ],
                agents_involved=["product_ideator", "senior_developer", "qa_tester", "pr_creator"],
                wave_structure={
                    "wave_1": ["product_ideator"],
                    "wave_2": ["senior_developer"],
                    "wave_3": ["qa_tester"],
                    "wave_4": ["pr_creator"],
                    "dependencies": {
                        "wave_2": ["wave_1"],
                        "wave_3": ["wave_2"],
                        "wave_4": ["wave_3"]
                    }
                }
            ),

            "feature_development": DevTaskTemplate(
                name="Feature Development",
                description="Develop complete feature with parallel ideation and coding",
                expected_output="Complete feature implementation with documentation and deployment",
                estimated_time=150,
                required_tools=["github_management", "vercel_deployment"],
                success_criteria=[
                    "Feature designed and specified",
                    "Code implemented and tested",
                    "QA verification completed",
                    "Feature deployed successfully",
                    "User documentation created"
                ],
                agents_involved=["product_ideator", "senior_developer", "qa_tester", "pr_creator"],
                wave_structure={
                    "wave_1": ["product_ideator", "senior_developer"],
                    "wave_2": ["qa_tester"],
                    "wave_3": ["pr_creator"],
                    "dependencies": {
                        "wave_2": ["wave_1"],
                        "wave_3": ["wave_2"]
                    }
                }
            ),

            "deployment_automation": DevTaskTemplate(
                name="Deployment Automation",
                description="Set up automated CI/CD pipeline for product deployment",
                expected_output="Complete CI/CD pipeline with automated testing and deployment",
                estimated_time=90,
                required_tools=["github_management", "vercel_deployment"],
                success_criteria=[
                    "GitHub Actions CI/CD configured",
                    "Automated testing pipeline setup",
                    "Staging environment configured",
                    "Production deployment automated",
                    "Monitoring and alerting configured",
                    "Rollback procedures documented"
                ],
                agents_involved=["pr_creator"],
                wave_structure={
                    "wave_1": ["pr_creator"],
                    "dependencies": {}
                }
            ),

            "chrome_extension_feature": DevTaskTemplate(
                name="Chrome Extension Feature",
                description="Develop feature specifically for Chrome extensions (Chromentum)",
                expected_output="Chrome extension feature with Web Store deployment",
                estimated_time=200,
                required_tools=["github_management", "chrome_web_store"],
                success_criteria=[
                    "Chrome extension architecture designed",
                    "Manifest v3 compliance ensured",
                    "Background/content scripts implemented",
                    "Extension permissions optimized",
                    "Cross-browser testing completed",
                    "Web Store deployment successful"
                ],
                agents_involved=["product_ideator", "senior_developer", "qa_tester", "pr_creator"],
                wave_structure={
                    "wave_1": ["product_ideator"],
                    "wave_2": ["senior_developer"],
                    "wave_3": ["qa_tester"],
                    "wave_4": ["pr_creator"],
                    "dependencies": {
                        "wave_2": ["wave_1"],
                        "wave_3": ["wave_2"],
                        "wave_4": ["wave_3"]
                    }
                }
            ),

            "ai_integration_feature": DevTaskTemplate(
                name="AI Integration Feature",
                description="Develop AI-powered features for Devlar products",
                expected_output="AI feature with model integration and fallback handling",
                estimated_time=160,
                required_tools=["github_management", "ai_apis"],
                success_criteria=[
                    "AI model integration designed",
                    "API rate limiting implemented",
                    "Error handling and fallbacks configured",
                    "Cost optimization implemented",
                    "Privacy compliance ensured",
                    "Performance monitoring setup"
                ],
                agents_involved=["product_ideator", "senior_developer", "qa_tester", "pr_creator"],
                wave_structure={
                    "wave_1": ["product_ideator"],
                    "wave_2": ["senior_developer"],
                    "wave_3": ["qa_tester"],
                    "wave_4": ["pr_creator"],
                    "dependencies": {
                        "wave_2": ["wave_1"],
                        "wave_3": ["wave_2"],
                        "wave_4": ["wave_3"]
                    }
                }
            )
        }

        return templates

    def get_task_for_goal(self, goal: str, product: str = "") -> str:
        """Determine appropriate development task based on goal and product"""

        goal_lower = goal.lower()
        product_lower = product.lower()

        # Chrome extension specific
        if "chromentum" in goal_lower or "chrome extension" in goal_lower:
            if "feature" in goal_lower or "ship" in goal_lower:
                return "chrome_extension_feature"
            else:
                return "feature_development"

        # AI feature specific
        elif any(ai_term in goal_lower for ai_term in ["ai", "affirmation", "generator", "intelligent"]):
            return "ai_integration_feature"

        # Deployment specific
        elif any(deploy_term in goal_lower for deploy_term in ["deploy", "ci/cd", "pipeline", "automation"]):
            return "deployment_automation"

        # Feature development
        elif "feature" in goal_lower or "ship" in goal_lower or "build" in goal_lower:
            if "prototype" in goal_lower or "mvp" in goal_lower:
                return "feature_development"
            else:
                return "technical_implementation"

        # Ideation only
        elif "idea" in goal_lower or "brainstorm" in goal_lower:
            return "feature_ideation"

        # Default to full implementation
        else:
            return "technical_implementation"

    def create_dev_workflow(self, product: str, feature: str, goal: str) -> Dict[str, Any]:
        """Create custom development workflow for specific product and feature"""

        workflow = {
            "product": product,
            "feature": feature,
            "goal": goal,
            "tasks": [],
            "estimated_time": 0,
            "tech_stack": self.get_tech_stack(product),
            "deployment_target": self.get_deployment_target(product)
        }

        # Determine workflow based on product type
        if "chromentum" in product.lower():
            workflow["tasks"] = [
                "feature_ideation",
                "chrome_extension_feature"
            ]
            workflow["special_requirements"] = [
                "Manifest v3 compliance",
                "Chrome Web Store guidelines",
                "Browser compatibility",
                "Extension security"
            ]

        elif any(ai_product in product.lower() for ai_product in ["zeneural", "aimstack"]):
            workflow["tasks"] = [
                "feature_ideation",
                "ai_integration_feature"
            ]
            workflow["special_requirements"] = [
                "AI model integration",
                "Rate limiting and costs",
                "Privacy compliance",
                "Fallback strategies"
            ]

        elif "timepost" in product.lower():
            workflow["tasks"] = [
                "feature_ideation",
                "technical_implementation"
            ]
            workflow["special_requirements"] = [
                "Social media API integration",
                "Scheduling accuracy",
                "Multi-platform support"
            ]

        else:
            # Default workflow for other products
            workflow["tasks"] = [
                "feature_ideation",
                "technical_implementation"
            ]

        # Add deployment automation if needed
        if "deploy" in goal.lower() or "production" in goal.lower():
            workflow["tasks"].append("deployment_automation")

        # Calculate total estimated time
        for task_name in workflow["tasks"]:
            if task_name in self.task_templates:
                workflow["estimated_time"] += self.task_templates[task_name].estimated_time

        return workflow

    def get_tech_stack(self, product: str) -> Dict[str, Any]:
        """Get appropriate tech stack for product"""

        stacks = {
            "chromentum": {
                "frontend": "Vanilla JavaScript, HTML5, CSS3",
                "backend": "Node.js, Express",
                "database": "Chrome Storage API, Supabase",
                "deployment": "Chrome Web Store",
                "special": "Chrome Extension APIs, Manifest v3"
            },
            "zeneural": {
                "frontend": "React, Next.js",
                "backend": "Python, FastAPI",
                "database": "Supabase, PostgreSQL",
                "deployment": "Vercel, Modal.com",
                "ai": "OpenAI API, Anthropic, Video generation APIs"
            },
            "timepost": {
                "frontend": "React, TypeScript",
                "backend": "Node.js, Express",
                "database": "PostgreSQL, Redis",
                "deployment": "Vercel",
                "integrations": "Social media APIs"
            },
            "aimstack": {
                "core": "Python, TypeScript",
                "framework": "LangChain-style architecture",
                "deployment": "PyPI, npm",
                "ai": "Multi-model support, Agent frameworks"
            },
            "elephant_desktop": {
                "frontend": "React, TypeScript",
                "backend": "Tauri, Rust",
                "platform": "Cross-platform desktop",
                "deployment": "Native app stores"
            }
        }

        # Find matching stack or default
        for product_key, stack in stacks.items():
            if product_key in product.lower():
                return stack

        # Default modern web stack
        return {
            "frontend": "React, TypeScript",
            "backend": "Node.js, Python",
            "database": "PostgreSQL",
            "deployment": "Vercel, Modal.com"
        }

    def get_deployment_target(self, product: str) -> str:
        """Get deployment target for product"""

        targets = {
            "chromentum": "Chrome Web Store",
            "zeneural": "Vercel + Modal.com",
            "timepost": "Vercel",
            "aimstack": "PyPI + npm",
            "elephant_desktop": "Desktop app stores"
        }

        for product_key, target in targets.items():
            if product_key in product.lower():
                return target

        return "Vercel"

    def get_development_parameters(self, product: str, feature: str, goal: str) -> Dict[str, Any]:
        """Generate development parameters for specific product and feature"""

        base_params = {
            "product": product,
            "feature": feature,
            "goal": goal,
            "tech_stack": self.get_tech_stack(product),
            "deployment_target": self.get_deployment_target(product)
        }

        # Product-specific parameters
        if "chromentum" in product.lower():
            base_params.update({
                "browser_targets": ["Chrome", "Firefox", "Safari", "Edge"],
                "extension_permissions": ["activeTab", "storage", "background"],
                "chrome_apis": ["chrome.storage", "chrome.tabs", "chrome.runtime"],
                "security_requirements": ["CSP compliance", "secure origins only"],
                "performance_targets": {
                    "load_time": "< 100ms",
                    "memory_usage": "< 50MB",
                    "cpu_usage": "< 5%"
                }
            })

        elif "zeneural" in product.lower():
            base_params.update({
                "ai_features": ["content generation", "personalization", "voice synthesis"],
                "content_types": ["meditation", "affirmations", "guided sessions"],
                "platforms": ["web", "mobile responsive"],
                "privacy_requirements": ["GDPR compliance", "data minimization"],
                "cost_optimization": {
                    "ai_calls": "optimize for cost per user",
                    "storage": "efficient media storage"
                }
            })

        elif "aimstack" in product.lower():
            base_params.update({
                "framework_type": "AI agent development",
                "target_users": ["developers", "AI engineers"],
                "compatibility": ["Python 3.9+", "TypeScript 5+"],
                "integration_targets": ["Elephant Desktop", "other Devlar products"],
                "documentation_requirements": ["API docs", "examples", "tutorials"]
            })

        return base_params

    def validate_dev_results(self, task_name: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate development results against success criteria"""

        if task_name not in self.task_templates:
            return {"valid": False, "reason": "Unknown development task"}

        template = self.task_templates[task_name]
        validation = {
            "valid": True,
            "score": 0,
            "missing_criteria": [],
            "recommendations": [],
            "quality_gate": "YELLOW"  # Default
        }

        # Check success criteria
        results_text = str(results).lower()

        for criterion in template.success_criteria:
            criterion_keywords = criterion.lower().split()
            if any(keyword in results_text for keyword in criterion_keywords[:3]):  # Check first 3 keywords
                validation["score"] += 1
            else:
                validation["missing_criteria"].append(criterion)

        # Calculate score percentage
        total_criteria = len(template.success_criteria)
        validation["score_percentage"] = (validation["score"] / total_criteria) * 100

        # Determine quality gate (higher standards for development)
        if validation["score_percentage"] >= 90:
            validation["quality_gate"] = "GREEN"
        elif validation["score_percentage"] >= 70:
            validation["quality_gate"] = "YELLOW"
        else:
            validation["quality_gate"] = "RED"

        # Development-specific validation
        validation["valid"] = validation["score_percentage"] >= 70

        # Add development-specific recommendations
        if validation["score_percentage"] < 100:
            validation["recommendations"].append("Consider additional testing and validation")

        if validation["score_percentage"] < 80:
            validation["recommendations"].append("Review implementation against all success criteria")

        if "deployment" in task_name and validation["score_percentage"] < 90:
            validation["recommendations"].append("Deployment tasks require high quality standards")

        return validation

    def estimate_development_cost(self, task_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate development costs (time, resources, API calls)"""

        if task_name not in self.task_templates:
            return {"error": "Unknown task"}

        template = self.task_templates[task_name]

        cost_estimate = {
            "time_minutes": template.estimated_time,
            "agent_hours": len(template.agents_involved) * (template.estimated_time / 60),
            "api_calls_estimated": 0,
            "cost_breakdown": {}
        }

        # Estimate API costs based on task type
        if "ai_integration" in task_name:
            cost_estimate["api_calls_estimated"] = 100  # AI development testing
            cost_estimate["estimated_ai_cost"] = "$5-15"

        elif "chrome_extension" in task_name:
            cost_estimate["api_calls_estimated"] = 50   # Web scraping for testing
            cost_estimate["estimated_web_cost"] = "$2-5"

        else:
            cost_estimate["api_calls_estimated"] = 30   # Basic testing
            cost_estimate["estimated_cost"] = "$1-3"

        # Factor in complexity
        complexity_multiplier = len(parameters.get("features", [])) * 0.2 + 1.0
        cost_estimate["time_minutes"] = int(cost_estimate["time_minutes"] * complexity_multiplier)

        cost_estimate["human_approval_required"] = cost_estimate.get("estimated_cost", "$1").replace("$", "").split("-")[1] > "10"

        return cost_estimate