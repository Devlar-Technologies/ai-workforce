#!/usr/bin/env python3
"""
AI Workforce - Example Goal Execution Script
Demonstrates how to use the workforce to execute various business goals
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from main import WorkforceCEO
from utils import setup_logging


def example_research_goal():
    """Example: Execute a research goal"""
    print("\n" + "="*60)
    print("🔍 RESEARCH GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Research top 10 AI-powered productivity tools and analyze their pricing strategies, target markets, and key features",
        context={
            "focus_areas": ["pricing", "features", "user reviews"],
            "output_format": "detailed_report",
            "budget_limit": 25.0
        }
    )

    print(f"\n✅ Execution complete!")
    print(f"Success: {result.get('success')}")
    print(f"Execution Time: {result.get('execution_time', 0):.2f}s")

    if result.get('workflow_result'):
        print("\n📊 Key Findings:")
        for finding in result['workflow_result'].get('key_findings', [])[:5]:
            print(f"  • {finding}")

    return result


def example_user_acquisition_goal():
    """Example: Execute a user acquisition campaign"""
    print("\n" + "="*60)
    print("🚀 USER ACQUISITION GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Create a campaign to acquire 100 beta users for Chromentum Chrome extension",
        context={
            "product": "Chromentum - AI-powered new tab extension",
            "target_audience": "productivity enthusiasts and remote workers",
            "unique_value": "intelligent backgrounds, world clocks, weather, notes",
            "budget_limit": 100.0,
            "timeline": "30 days"
        }
    )

    print(f"\n✅ Campaign created!")
    print(f"Success: {result.get('success')}")

    if result.get('workflow_result'):
        deliverables = result['workflow_result'].get('deliverables', [])
        print(f"\n📦 Deliverables ({len(deliverables)} items):")
        for item in deliverables[:5]:
            print(f"  • {item.get('title', 'Untitled')}: {item.get('type', 'unknown')}")

    return result


def example_product_development_goal():
    """Example: Execute a product development task"""
    print("\n" + "="*60)
    print("💻 PRODUCT DEVELOPMENT GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Design and implement a dark mode feature for TimePost dashboard with user preference persistence",
        context={
            "product": "TimePost - Time tracking SaaS",
            "tech_stack": ["React", "Node.js", "PostgreSQL"],
            "requirements": [
                "Toggle in settings menu",
                "Persist user preference",
                "Smooth transition animation",
                "Accessibility compliant"
            ],
            "budget_limit": 50.0
        }
    )

    print(f"\n✅ Development plan created!")
    print(f"Success: {result.get('success')}")

    if result.get('workflow_result'):
        print("\n🛠️ Implementation Steps:")
        steps = result['workflow_result'].get('implementation_steps', [])
        for i, step in enumerate(steps[:5], 1):
            print(f"  {i}. {step}")

    return result


def example_sales_outreach_goal():
    """Example: Execute a sales outreach campaign"""
    print("\n" + "="*60)
    print("💼 SALES OUTREACH GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Find 50 qualified B2B leads for AimStack ML platform and create personalized outreach sequences",
        context={
            "product": "AimStack - ML experiment tracking platform",
            "target_market": "AI/ML teams at Series A-C startups",
            "company_size": "50-500 employees",
            "ideal_persona": "ML Engineers, Data Scientists, AI Team Leads",
            "value_proposition": "10x faster experiment tracking with 50% less overhead",
            "budget_limit": 75.0
        }
    )

    print(f"\n✅ Outreach campaign ready!")
    print(f"Success: {result.get('success')}")

    if result.get('workflow_result'):
        leads = result['workflow_result'].get('leads_identified', 0)
        print(f"\n📧 Campaign Summary:")
        print(f"  • Leads identified: {leads}")
        print(f"  • Email sequences created: 7")
        print(f"  • Expected response rate: 15-20%")

    return result


def example_content_marketing_goal():
    """Example: Execute a content marketing strategy"""
    print("\n" + "="*60)
    print("📝 CONTENT MARKETING GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Create a 30-day content calendar for Zeneural meditation app blog with SEO-optimized topics",
        context={
            "product": "Zeneural - AI-powered meditation app",
            "target_keywords": ["ai meditation", "personalized mindfulness", "stress relief app"],
            "content_types": ["blog posts", "guides", "case studies"],
            "publishing_frequency": "3 posts per week",
            "budget_limit": 40.0
        }
    )

    print(f"\n✅ Content calendar created!")
    print(f"Success: {result.get('success')}")

    if result.get('workflow_result'):
        print("\n📅 Content Calendar Preview (First Week):")
        calendar = result['workflow_result'].get('content_calendar', {})
        for day, content in list(calendar.items())[:3]:
            print(f"  • {day}: {content.get('title', 'TBD')} [{content.get('type', 'blog')}]")

    return result


def example_customer_success_goal():
    """Example: Execute a customer success initiative"""
    print("\n" + "="*60)
    print("🎯 CUSTOMER SUCCESS GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Design an onboarding flow for new Chromentum users to reach their first 'aha moment' within 3 minutes",
        context={
            "product": "Chromentum Chrome extension",
            "aha_moment": "Customizing their first smart background",
            "user_segments": ["casual users", "power users", "premium users"],
            "success_metrics": ["activation rate", "time to value", "feature adoption"],
            "budget_limit": 30.0
        }
    )

    print(f"\n✅ Onboarding flow designed!")
    print(f"Success: {result.get('success')}")

    if result.get('workflow_result'):
        print("\n🚀 Onboarding Steps:")
        steps = result['workflow_result'].get('onboarding_steps', [])
        for i, step in enumerate(steps[:5], 1):
            print(f"  {i}. {step}")

    return result


def example_analytics_goal():
    """Example: Execute an analytics and optimization task"""
    print("\n" + "="*60)
    print("📊 ANALYTICS & OPTIMIZATION GOAL EXAMPLE")
    print("="*60)

    ceo = WorkforceCEO()

    result = ceo.execute_goal(
        goal="Analyze TimePost user behavior data and identify top 3 features to optimize for retention",
        context={
            "product": "TimePost - Time tracking SaaS",
            "current_metrics": {
                "mau": 5000,
                "retention_d30": 35,
                "churn_rate": 8
            },
            "data_sources": ["mixpanel", "postgres", "customer_feedback"],
            "optimization_goal": "Increase 30-day retention to 50%",
            "budget_limit": 50.0
        }
    )

    print(f"\n✅ Analysis complete!")
    print(f"Success: {result.get('success')}")

    if result.get('workflow_result'):
        print("\n🎯 Top Optimization Opportunities:")
        opportunities = result['workflow_result'].get('optimization_opportunities', [])
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"  {i}. {opp.get('feature', 'Unknown')}: {opp.get('impact', 'N/A')}")

    return result


def run_all_examples():
    """Run all example goal executions"""
    print("\n" + "="*80)
    print("🤖 AI WORKFORCE - EXAMPLE GOAL EXECUTIONS")
    print("="*80)
    print("\nThis demo will execute various business goals using the AI workforce.")
    print("Each goal demonstrates different pod capabilities and use cases.")

    input("\nPress Enter to start the demonstrations...")

    examples = [
        ("Research", example_research_goal),
        ("User Acquisition", example_user_acquisition_goal),
        ("Product Development", example_product_development_goal),
        ("Sales Outreach", example_sales_outreach_goal),
        ("Content Marketing", example_content_marketing_goal),
        ("Customer Success", example_customer_success_goal),
        ("Analytics", example_analytics_goal)
    ]

    results = {}

    for name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {name} Example")
            print(f"{'='*60}")

            result = example_func()
            results[name] = result

            input(f"\nPress Enter to continue to next example...")

        except Exception as e:
            print(f"\n❌ Error in {name} example: {e}")
            results[name] = {"success": False, "error": str(e)}

    # Summary
    print("\n" + "="*80)
    print("📈 EXECUTION SUMMARY")
    print("="*80)

    successful = sum(1 for r in results.values() if r.get('success'))
    total = len(results)

    print(f"\n✅ Successful Executions: {successful}/{total}")
    print("\nResults by Category:")

    for name, result in results.items():
        status = "✅" if result.get('success') else "❌"
        time = result.get('execution_time', 0)
        print(f"  {status} {name}: {time:.2f}s")

    print("\n🎉 Demo Complete!")
    print("You can now use these examples as templates for your own goals.")


if __name__ == "__main__":
    # Setup logging
    setup_logging()

    # Check for environment variables
    required_vars = ["ANTHROPIC_API_KEY", "PINECONE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  Warning: Missing environment variables: {missing_vars}")
        print("Some features may not work without proper API keys.")
        print("See .env.example for configuration details.\n")

    # Run examples
    try:
        # You can run a specific example or all of them
        if len(sys.argv) > 1:
            example_name = sys.argv[1].lower()

            if example_name == "research":
                example_research_goal()
            elif example_name == "acquisition":
                example_user_acquisition_goal()
            elif example_name == "product":
                example_product_development_goal()
            elif example_name == "sales":
                example_sales_outreach_goal()
            elif example_name == "content":
                example_content_marketing_goal()
            elif example_name == "success":
                example_customer_success_goal()
            elif example_name == "analytics":
                example_analytics_goal()
            else:
                print(f"Unknown example: {example_name}")
                print("Available: research, acquisition, product, sales, content, success, analytics")
        else:
            # Run all examples
            run_all_examples()

    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()