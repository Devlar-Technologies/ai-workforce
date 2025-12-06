"""
Apollo.io Lead Generation Tool - B2B prospecting and lead qualification
Optimized for finding decision-makers and prospects for Devlar products
"""

import os
import json
from typing import Dict, Any, List, Optional

import requests
from loguru import logger
from crewai.tools import BaseTool

class ApolloProspectingTool(BaseTool):
    """
    Apollo.io lead generation tool for B2B prospecting.
    Finds qualified leads, decision-makers, and contact information.
    """

    name: str = "apollo_prospecting"
    description: str = (
        "Search for qualified B2B leads and prospects using Apollo.io. "
        "Find decision-makers, contact information, and company insights."
    )

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("APOLLO_API_KEY")
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY environment variable is required")

        self.base_url = "https://api.apollo.io/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        })

    def _run(
        self,
        search_type: str = "people",
        company_size: str = "1-50",
        job_titles: List[str] = None,
        industries: List[str] = None,
        locations: List[str] = None,
        technologies: List[str] = None,
        company_keywords: List[str] = None,
        limit: int = 25
    ) -> str:
        """
        Search for prospects using Apollo.io

        Args:
            search_type: Type of search (people, companies)
            company_size: Company size range
            job_titles: Target job titles
            industries: Target industries
            locations: Geographic locations
            technologies: Technologies used by target companies
            company_keywords: Keywords to search in company descriptions
            limit: Maximum number of results

        Returns:
            Formatted list of qualified prospects
        """
        try:
            if search_type == "people":
                return self._search_people(
                    company_size=company_size,
                    job_titles=job_titles or [],
                    industries=industries or [],
                    locations=locations or [],
                    technologies=technologies or [],
                    limit=limit
                )
            elif search_type == "companies":
                return self._search_companies(
                    company_size=company_size,
                    industries=industries or [],
                    technologies=technologies or [],
                    keywords=company_keywords or [],
                    limit=limit
                )
            else:
                return f"Unknown search type: {search_type}"

        except Exception as e:
            logger.error(f"❌ Apollo prospecting failed: {e}")
            return f"Prospecting failed: {str(e)}"

    def _search_people(
        self,
        company_size: str,
        job_titles: List[str],
        industries: List[str],
        locations: List[str],
        technologies: List[str],
        limit: int
    ) -> str:
        """Search for people/prospects"""

        # Build search criteria
        search_params = {
            "per_page": min(limit, 100),  # Apollo limit
            "person_titles": job_titles,
            "organization_industry_tag_ids": self._get_industry_ids(industries),
            "organization_locations": locations,
            "organization_num_employees_ranges": [self._parse_company_size(company_size)],
            "prospected_by_current_team": False
        }

        # Add technology filters if specified
        if technologies:
            search_params["organization_technology_tag_ids"] = self._get_technology_ids(technologies)

        # Remove empty parameters
        search_params = {k: v for k, v in search_params.items() if v}

        response = self.session.post(
            f"{self.base_url}/mixed_people/search",
            json=search_params
        )

        if response.status_code != 200:
            return f"Apollo API error: {response.status_code} - {response.text}"

        data = response.json()
        prospects = data.get('people', [])

        if not prospects:
            return "No prospects found matching the criteria"

        return self._format_people_results(prospects)

    def _search_companies(
        self,
        company_size: str,
        industries: List[str],
        technologies: List[str],
        keywords: List[str],
        limit: int
    ) -> str:
        """Search for companies"""

        search_params = {
            "per_page": min(limit, 100),
            "organization_industry_tag_ids": self._get_industry_ids(industries),
            "organization_num_employees_ranges": [self._parse_company_size(company_size)],
            "prospected_by_current_team": False
        }

        # Add technology and keyword filters
        if technologies:
            search_params["technology_tag_ids"] = self._get_technology_ids(technologies)

        if keywords:
            search_params["keywords"] = " ".join(keywords)

        response = self.session.post(
            f"{self.base_url}/organizations/search",
            json=search_params
        )

        if response.status_code != 200:
            return f"Apollo API error: {response.status_code} - {response.text}"

        data = response.json()
        companies = data.get('organizations', [])

        if not companies:
            return "No companies found matching the criteria"

        return self._format_company_results(companies)

    def _get_industry_ids(self, industries: List[str]) -> List[str]:
        """Map industry names to Apollo IDs"""
        # Simplified mapping - in production, use Apollo's industry endpoint
        industry_mapping = {
            "software": "5f4d57fc7f8e5b001f5e4b1a",
            "technology": "5f4d57fc7f8e5b001f5e4b1a",
            "saas": "5f4d57fc7f8e5b001f5e4b1b",
            "startups": "5f4d57fc7f8e5b001f5e4b1c",
            "productivity": "5f4d57fc7f8e5b001f5e4b1d",
            "ai": "5f4d57fc7f8e5b001f5e4b1e",
            "wellness": "5f4d57fc7f8e5b001f5e4b1f"
        }

        return [industry_mapping.get(industry.lower()) for industry in industries if industry.lower() in industry_mapping]

    def _get_technology_ids(self, technologies: List[str]) -> List[str]:
        """Map technology names to Apollo IDs"""
        # Simplified mapping
        tech_mapping = {
            "react": "5f4d57fc7f8e5b001f5e4c1a",
            "python": "5f4d57fc7f8e5b001f5e4c1b",
            "javascript": "5f4d57fc7f8e5b001f5e4c1c",
            "node.js": "5f4d57fc7f8e5b001f5e4c1d",
            "chrome": "5f4d57fc7f8e5b001f5e4c1e"
        }

        return [tech_mapping.get(tech.lower()) for tech in technologies if tech.lower() in tech_mapping]

    def _parse_company_size(self, size_range: str) -> str:
        """Convert size range to Apollo format"""
        size_mapping = {
            "1-10": "1-10",
            "1-50": "1-50",
            "11-50": "11-50",
            "51-200": "51-200",
            "201-500": "201-500",
            "501-1000": "501-1000",
            "1000+": "1001+"
        }
        return size_mapping.get(size_range, "1-50")

    def _format_people_results(self, prospects: List[Dict[str, Any]]) -> str:
        """Format people search results"""

        formatted = f"""
# 🎯 Prospect Search Results ({len(prospects)} found)

"""

        for i, prospect in enumerate(prospects[:25], 1):
            name = f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip()
            title = prospect.get('title', 'Unknown Title')
            company = prospect.get('organization', {}).get('name', 'Unknown Company')
            industry = prospect.get('organization', {}).get('industry', 'Unknown Industry')
            company_size = prospect.get('organization', {}).get('estimated_num_employees', 'Unknown')
            location = self._get_location_string(prospect.get('organization', {}))

            # Contact info
            email = prospect.get('email', 'Email not available')
            linkedin = prospect.get('linkedin_url', 'LinkedIn not available')

            formatted += f"""
## {i}. {name}
**Title**: {title}
**Company**: {company} ({company_size} employees)
**Industry**: {industry}
**Location**: {location}
**Email**: {email}
**LinkedIn**: {linkedin}

"""

        formatted += "\n---\n*Results generated by Apollo.io*"
        return formatted

    def _format_company_results(self, companies: List[Dict[str, Any]]) -> str:
        """Format company search results"""

        formatted = f"""
# 🏢 Company Search Results ({len(companies)} found)

"""

        for i, company in enumerate(companies[:25], 1):
            name = company.get('name', 'Unknown Company')
            industry = company.get('industry', 'Unknown Industry')
            size = company.get('estimated_num_employees', 'Unknown')
            website = company.get('website_url', 'Website not available')
            location = self._get_location_string(company)
            description = company.get('short_description', 'No description available')

            # Technologies
            technologies = company.get('technologies', [])
            tech_list = ', '.join([tech.get('name', '') for tech in technologies[:5]])

            formatted += f"""
## {i}. {name}
**Industry**: {industry}
**Size**: {size} employees
**Website**: {website}
**Location**: {location}
**Technologies**: {tech_list or 'Not specified'}

**Description**: {description[:200]}...

"""

        formatted += "\n---\n*Results generated by Apollo.io*"
        return formatted

    def _get_location_string(self, org_data: Dict[str, Any]) -> str:
        """Extract location string from organization data"""
        city = org_data.get('primary_city', '')
        state = org_data.get('primary_state', '')
        country = org_data.get('primary_country', '')

        location_parts = [part for part in [city, state, country] if part]
        return ', '.join(location_parts) if location_parts else 'Location not specified'

# Devlar-specific search presets
def get_devlar_search_presets():
    """Get predefined search configurations for Devlar products"""

    return {
        "chromentum_prospects": {
            "job_titles": ["Product Manager", "VP Product", "Head of Product", "CTO", "Engineering Manager"],
            "industries": ["Software", "Technology", "SaaS", "Startups"],
            "company_size": "11-200",
            "technologies": ["React", "JavaScript", "Chrome"],
            "description": "Decision-makers at tech companies who might need productivity tools like Chromentum"
        },

        "zeneural_prospects": {
            "job_titles": ["Chief Wellness Officer", "HR Director", "People Operations", "Founder", "CEO"],
            "industries": ["Technology", "SaaS", "Wellness", "Healthcare"],
            "company_size": "51-500",
            "description": "Leaders focused on employee wellness and mental health solutions"
        },

        "enterprise_prospects": {
            "job_titles": ["CTO", "VP Engineering", "Director of IT", "Chief Digital Officer"],
            "industries": ["Enterprise Software", "Financial Services", "Healthcare", "Manufacturing"],
            "company_size": "501-1000",
            "description": "Enterprise decision-makers for larger Devlar product implementations"
        },

        "developer_prospects": {
            "job_titles": ["Lead Developer", "Senior Engineer", "Technical Lead", "Engineering Manager"],
            "industries": ["Software", "Technology", "Gaming", "Fintech"],
            "company_size": "11-200",
            "technologies": ["Python", "React", "Node.js"],
            "description": "Technical decision-makers who might be interested in AimStack or developer tools"
        }
    }