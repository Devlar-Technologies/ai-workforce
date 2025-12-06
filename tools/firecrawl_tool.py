"""
Firecrawl Research Tool - Web scraping and content research
Optimized for Devlar's market research and competitive analysis needs
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin

import requests
from firecrawl import FirecrawlApp
from loguru import logger
from crewai.tools import BaseTool

class FirecrawlResearchTool(BaseTool):
    """
    Firecrawl-powered research tool for web scraping and content analysis.
    Optimized for market research, competitor analysis, and trend monitoring.
    """

    name: str = "firecrawl_research"
    description: str = (
        "Scrape and analyze web content for market research. "
        "Can extract structured data from websites, analyze competitor content, "
        "and gather market intelligence from various sources."
    )

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")

        self.firecrawl = FirecrawlApp(api_key=self.api_key)
        self.rate_limit_delay = 1.0  # seconds between requests

    def _run(
        self,
        url: str,
        research_type: str = "general",
        extract_contacts: bool = False,
        analyze_competitors: bool = False,
        extract_pricing: bool = False,
        max_pages: int = 5
    ) -> str:
        """
        Execute Firecrawl research operation

        Args:
            url: Target URL to scrape and analyze
            research_type: Type of research (general, competitor, market, pricing)
            extract_contacts: Whether to extract contact information
            analyze_competitors: Whether to perform competitor analysis
            extract_pricing: Whether to extract pricing information
            max_pages: Maximum pages to crawl (for site crawling)

        Returns:
            Formatted research results
        """
        try:
            logger.info(f"🔍 Starting Firecrawl research on: {url}")

            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return f"Error: Invalid URL format: {url}"

            # Choose research strategy based on type
            if research_type == "competitor":
                return self._analyze_competitor_site(url, extract_pricing)
            elif research_type == "market":
                return self._conduct_market_research(url, max_pages)
            elif research_type == "pricing":
                return self._extract_pricing_info(url)
            elif research_type == "content":
                return self._analyze_content(url)
            else:
                return self._general_research(url, extract_contacts)

        except Exception as e:
            logger.error(f"❌ Firecrawl research failed: {e}")
            return f"Research failed: {str(e)}"

    def _general_research(self, url: str, extract_contacts: bool = False) -> str:
        """Conduct general web research and content extraction"""

        try:
            # Scrape the page
            scraped_data = self.firecrawl.scrape_url(
                url,
                params={
                    'formats': ['markdown', 'html'],
                    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'a'],
                    'excludeTags': ['script', 'style', 'nav', 'footer'],
                    'waitFor': 2000,
                    'timeout': 30000
                }
            )

            if not scraped_data or 'markdown' not in scraped_data:
                return f"Failed to extract content from {url}"

            # Extract key information
            content = scraped_data['markdown']
            metadata = scraped_data.get('metadata', {})

            # Structure the research results
            research_results = {
                "url": url,
                "title": metadata.get('title', 'Unknown'),
                "description": metadata.get('description', 'No description'),
                "content_length": len(content),
                "key_findings": self._extract_key_findings(content),
                "contact_info": self._extract_contacts(content) if extract_contacts else None,
                "technologies": self._identify_technologies(content, scraped_data.get('html', '')),
                "content_summary": content[:1000] + "..." if len(content) > 1000 else content
            }

            return self._format_research_results(research_results)

        except Exception as e:
            return f"General research failed: {str(e)}"

    def _analyze_competitor_site(self, url: str, extract_pricing: bool = False) -> str:
        """Analyze competitor website for strategic intelligence"""

        try:
            # Enhanced scraping for competitor analysis
            scraped_data = self.firecrawl.scrape_url(
                url,
                params={
                    'formats': ['markdown', 'html'],
                    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'a', 'img'],
                    'excludeTags': ['script', 'style', 'nav', 'footer'],
                    'waitFor': 3000,
                    'timeout': 45000
                }
            )

            if not scraped_data:
                return f"Failed to analyze competitor site: {url}"

            content = scraped_data.get('markdown', '')
            html_content = scraped_data.get('html', '')
            metadata = scraped_data.get('metadata', {})

            # Competitor-specific analysis
            competitor_analysis = {
                "company_info": {
                    "name": self._extract_company_name(content, metadata),
                    "tagline": self._extract_tagline(content, metadata),
                    "description": metadata.get('description', ''),
                    "url": url
                },
                "value_proposition": self._extract_value_proposition(content),
                "features": self._extract_features(content),
                "pricing": self._extract_pricing_info(url) if extract_pricing else None,
                "technology_stack": self._identify_technologies(content, html_content),
                "target_audience": self._identify_target_audience(content),
                "competitive_advantages": self._extract_competitive_advantages(content),
                "weaknesses": self._identify_potential_weaknesses(content),
                "content_strategy": self._analyze_content_strategy(content)
            }

            return self._format_competitor_analysis(competitor_analysis)

        except Exception as e:
            return f"Competitor analysis failed: {str(e)}"

    def _conduct_market_research(self, base_url: str, max_pages: int = 5) -> str:
        """Conduct broader market research by crawling related pages"""

        try:
            # Use Firecrawl's crawling capability for market research
            crawl_result = self.firecrawl.crawl_url(
                base_url,
                params={
                    'limit': max_pages,
                    'scrapeOptions': {
                        'formats': ['markdown'],
                        'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p'],
                        'excludeTags': ['script', 'style', 'nav', 'footer']
                    }
                }
            )

            if not crawl_result or 'data' not in crawl_result:
                return f"Failed to crawl site for market research: {base_url}"

            # Analyze crawled data
            market_insights = {
                "base_url": base_url,
                "pages_analyzed": len(crawl_result['data']),
                "market_themes": self._extract_market_themes(crawl_result['data']),
                "common_features": self._identify_common_features(crawl_result['data']),
                "pricing_patterns": self._analyze_pricing_patterns(crawl_result['data']),
                "technology_trends": self._identify_tech_trends(crawl_result['data']),
                "content_gaps": self._identify_content_gaps(crawl_result['data']),
                "opportunities": self._identify_market_opportunities(crawl_result['data'])
            }

            return self._format_market_research(market_insights)

        except Exception as e:
            return f"Market research failed: {str(e)}"

    def _extract_pricing_info(self, url: str) -> Dict[str, Any]:
        """Extract pricing information from a website"""

        try:
            scraped_data = self.firecrawl.scrape_url(
                url,
                params={
                    'formats': ['markdown'],
                    'includeTags': ['div', 'section', 'span', 'p', 'h1', 'h2', 'h3'],
                    'waitFor': 2000
                }
            )

            content = scraped_data.get('markdown', '')

            pricing_info = {
                "pricing_model": self._identify_pricing_model(content),
                "price_points": self._extract_price_points(content),
                "plans": self._extract_pricing_plans(content),
                "free_tier": self._check_free_tier(content),
                "enterprise_pricing": self._check_enterprise_pricing(content)
            }

            return pricing_info

        except Exception as e:
            logger.error(f"Pricing extraction failed: {e}")
            return {"error": str(e)}

    def _analyze_content(self, url: str) -> str:
        """Analyze content quality and strategy"""

        try:
            scraped_data = self.firecrawl.scrape_url(url)
            content = scraped_data.get('markdown', '')

            content_analysis = {
                "content_length": len(content),
                "readability_score": self._calculate_readability(content),
                "keyword_density": self._analyze_keywords(content),
                "content_structure": self._analyze_structure(content),
                "call_to_actions": self._extract_ctas(content),
                "social_proof": self._extract_social_proof(content)
            }

            return self._format_content_analysis(content_analysis)

        except Exception as e:
            return f"Content analysis failed: {str(e)}"

    # Helper methods for data extraction and analysis

    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key findings from content"""
        findings = []

        # Look for important sections
        if "about" in content.lower():
            findings.append("Company information available")

        if any(word in content.lower() for word in ["pricing", "price", "cost"]):
            findings.append("Pricing information present")

        if any(word in content.lower() for word in ["feature", "solution", "product"]):
            findings.append("Product features described")

        if any(word in content.lower() for word in ["contact", "email", "phone"]):
            findings.append("Contact information available")

        return findings

    def _extract_contacts(self, content: str) -> Dict[str, List[str]]:
        """Extract contact information"""
        import re

        contacts = {
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content),
            "phones": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content),
            "social_links": []
        }

        # Look for social media links
        social_patterns = [
            r'twitter\.com/\w+',
            r'linkedin\.com/\w+',
            r'facebook\.com/\w+',
            r'instagram\.com/\w+'
        ]

        for pattern in social_patterns:
            matches = re.findall(pattern, content.lower())
            contacts["social_links"].extend(matches)

        return contacts

    def _identify_technologies(self, content: str, html_content: str) -> List[str]:
        """Identify technologies used"""
        technologies = []

        tech_indicators = {
            "React": ["react", "jsx", "_next"],
            "Vue": ["vue", "nuxt"],
            "Angular": ["angular", "ng-"],
            "WordPress": ["wp-content", "wordpress"],
            "Shopify": ["shopify", "myshopify"],
            "Stripe": ["stripe", "payment"],
            "Google Analytics": ["gtag", "google-analytics"]
        }

        content_lower = (content + html_content).lower()

        for tech, indicators in tech_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                technologies.append(tech)

        return technologies

    def _extract_company_name(self, content: str, metadata: Dict[str, Any]) -> str:
        """Extract company name"""
        title = metadata.get('title', '')
        if title:
            # Extract company name from title
            parts = title.split(' - ')
            return parts[-1] if len(parts) > 1 else title.split(' | ')[-1]
        return "Unknown"

    def _extract_tagline(self, content: str, metadata: Dict[str, Any]) -> str:
        """Extract company tagline or main value proposition"""
        description = metadata.get('description', '')
        if description:
            return description

        # Look for common tagline patterns in content
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if len(line) > 20 and len(line) < 200:
                if any(word in line.lower() for word in ["we", "our", "platform", "solution"]):
                    return line.strip()

        return "No tagline found"

    def _extract_value_proposition(self, content: str) -> str:
        """Extract main value proposition"""
        # Look for value prop indicators
        value_indicators = [
            "why choose",
            "benefits",
            "value proposition",
            "what makes us",
            "our advantage"
        ]

        content_lower = content.lower()
        lines = content.split('\n')

        for i, line in enumerate(lines):
            if any(indicator in line.lower() for indicator in value_indicators):
                # Return next few lines as value prop
                return '\n'.join(lines[i:i+3])

        # Fallback: return first substantial paragraph
        for line in lines:
            if len(line) > 100:
                return line[:300] + "..."

        return "Value proposition not clearly identified"

    def _extract_features(self, content: str) -> List[str]:
        """Extract product features"""
        features = []
        lines = content.split('\n')

        for line in lines:
            # Look for bullet points or numbered features
            if any(marker in line for marker in ['•', '*', '-', '1.', '2.', '3.']):
                clean_line = line.strip('•*- ').strip()
                if len(clean_line) > 10:  # Meaningful feature description
                    features.append(clean_line)

        return features[:10]  # Return top 10 features

    def _identify_target_audience(self, content: str) -> str:
        """Identify target audience"""
        audience_indicators = {
            "developers": ["developer", "API", "code", "technical", "engineer"],
            "businesses": ["business", "enterprise", "company", "organization"],
            "consumers": ["personal", "individual", "family", "home"],
            "creators": ["creator", "content", "artist", "designer"],
            "professionals": ["professional", "workplace", "career", "team"]
        }

        content_lower = content.lower()
        audience_scores = {}

        for audience, indicators in audience_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            if score > 0:
                audience_scores[audience] = score

        if audience_scores:
            primary_audience = max(audience_scores, key=audience_scores.get)
            return f"{primary_audience} (confidence: {audience_scores[primary_audience]})"

        return "Target audience unclear"

    def _extract_competitive_advantages(self, content: str) -> List[str]:
        """Extract competitive advantages"""
        advantage_keywords = [
            "unique", "only", "first", "best", "leading", "exclusive",
            "proprietary", "patented", "award-winning", "industry-leading"
        ]

        advantages = []
        lines = content.split('.')

        for line in lines:
            if any(keyword in line.lower() for keyword in advantage_keywords):
                clean_line = line.strip()
                if len(clean_line) > 20:
                    advantages.append(clean_line)

        return advantages[:5]  # Top 5 advantages

    def _identify_potential_weaknesses(self, content: str) -> List[str]:
        """Identify potential weaknesses or gaps"""
        weaknesses = []

        # Check for missing common elements
        if "pricing" not in content.lower():
            weaknesses.append("Pricing information not prominently displayed")

        if not any(word in content.lower() for word in ["testimonial", "review", "customer"]):
            weaknesses.append("Limited social proof or customer testimonials")

        if len(content) < 1000:
            weaknesses.append("Limited content depth")

        if not any(word in content.lower() for word in ["contact", "support", "help"]):
            weaknesses.append("Contact/support information not easily accessible")

        return weaknesses

    def _analyze_content_strategy(self, content: str) -> Dict[str, Any]:
        """Analyze content strategy"""
        return {
            "content_length": len(content),
            "heading_structure": len([line for line in content.split('\n') if line.startswith('#')]),
            "call_to_actions": len([line for line in content.split('\n') if any(cta in line.lower() for cta in ["sign up", "get started", "try", "buy"])]),
            "external_links": len([line for line in content.split('\n') if 'http' in line])
        }

    def _format_research_results(self, results: Dict[str, Any]) -> str:
        """Format research results for agent consumption"""
        formatted = f"""
# Research Results: {results['title']}

**URL**: {results['url']}
**Description**: {results['description']}

## Key Findings
{chr(10).join(f"• {finding}" for finding in results['key_findings'])}

## Technologies Identified
{chr(10).join(f"• {tech}" for tech in results['technologies'])}

## Content Summary
{results['content_summary']}
"""

        if results.get('contact_info'):
            formatted += f"""
## Contact Information
**Emails**: {', '.join(results['contact_info']['emails'])}
**Phones**: {', '.join(results['contact_info']['phones'])}
**Social**: {', '.join(results['contact_info']['social_links'])}
"""

        return formatted

    def _format_competitor_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format competitor analysis results"""
        return f"""
# Competitor Analysis: {analysis['company_info']['name']}

## Company Overview
**URL**: {analysis['company_info']['url']}
**Tagline**: {analysis['company_info']['tagline']}
**Description**: {analysis['company_info']['description']}

## Value Proposition
{analysis['value_proposition']}

## Key Features
{chr(10).join(f"• {feature}" for feature in analysis['features'])}

## Technology Stack
{chr(10).join(f"• {tech}" for tech in analysis['technology_stack'])}

## Target Audience
{analysis['target_audience']}

## Competitive Advantages
{chr(10).join(f"• {advantage}" for advantage in analysis['competitive_advantages'])}

## Potential Weaknesses
{chr(10).join(f"• {weakness}" for weakness in analysis['weaknesses'])}

## Content Strategy Analysis
**Content Length**: {analysis['content_strategy']['content_length']} characters
**Heading Structure**: {analysis['content_strategy']['heading_structure']} sections
**Call-to-Actions**: {analysis['content_strategy']['call_to_actions']} CTAs identified

{f"## Pricing Information{chr(10)}{json.dumps(analysis['pricing'], indent=2)}" if analysis.get('pricing') else ""}
"""

    def _format_market_research(self, insights: Dict[str, Any]) -> str:
        """Format market research results"""
        return f"""
# Market Research Results

**Base URL**: {insights['base_url']}
**Pages Analyzed**: {insights['pages_analyzed']}

## Market Themes
{chr(10).join(f"• {theme}" for theme in insights['market_themes'])}

## Common Features Across Market
{chr(10).join(f"• {feature}" for feature in insights['common_features'])}

## Technology Trends
{chr(10).join(f"• {trend}" for trend in insights['technology_trends'])}

## Market Opportunities
{chr(10).join(f"• {opportunity}" for opportunity in insights['opportunities'])}

## Content Gaps Identified
{chr(10).join(f"• {gap}" for gap in insights['content_gaps'])}
"""

    # Additional helper methods for market analysis
    def _extract_market_themes(self, crawl_data: List[Dict]) -> List[str]:
        """Extract common themes across crawled pages"""
        themes = []
        all_content = ' '.join([page.get('markdown', '') for page in crawl_data])

        theme_keywords = {
            "AI/Machine Learning": ["ai", "artificial intelligence", "machine learning", "automation"],
            "Productivity": ["productivity", "efficiency", "workflow", "collaboration"],
            "Security": ["security", "privacy", "encryption", "compliance"],
            "Analytics": ["analytics", "insights", "data", "metrics"],
            "Mobile-First": ["mobile", "responsive", "app", "ios", "android"]
        }

        for theme, keywords in theme_keywords.items():
            if sum(1 for keyword in keywords if keyword in all_content.lower()) >= 3:
                themes.append(theme)

        return themes

    def _identify_common_features(self, crawl_data: List[Dict]) -> List[str]:
        """Identify features common across multiple sites"""
        feature_counts = {}
        common_features = [
            "dashboard", "analytics", "integration", "api", "mobile app",
            "real-time", "automation", "collaboration", "security", "reporting"
        ]

        for page in crawl_data:
            content = page.get('markdown', '').lower()
            for feature in common_features:
                if feature in content:
                    feature_counts[feature] = feature_counts.get(feature, 0) + 1

        # Return features that appear in multiple pages
        threshold = max(1, len(crawl_data) // 3)  # At least 1/3 of pages
        return [feature for feature, count in feature_counts.items() if count >= threshold]

    def _analyze_pricing_patterns(self, crawl_data: List[Dict]) -> Dict[str, Any]:
        """Analyze pricing patterns across sites"""
        pricing_models = []
        price_ranges = []

        for page in crawl_data:
            content = page.get('markdown', '')
            if 'pricing' in content.lower():
                # Extract pricing model indicators
                if 'subscription' in content.lower() or 'monthly' in content.lower():
                    pricing_models.append('subscription')
                if 'free' in content.lower():
                    pricing_models.append('freemium')
                if 'usage' in content.lower() or 'pay-as-you' in content.lower():
                    pricing_models.append('usage-based')

        return {
            "common_models": list(set(pricing_models)),
            "model_frequency": {model: pricing_models.count(model) for model in set(pricing_models)}
        }

    def _identify_tech_trends(self, crawl_data: List[Dict]) -> List[str]:
        """Identify technology trends"""
        tech_mentions = {}
        technologies = [
            "React", "Vue", "Angular", "Node.js", "Python", "AI", "ML",
            "API", "REST", "GraphQL", "microservices", "cloud", "AWS", "Docker"
        ]

        for page in crawl_data:
            content = page.get('markdown', '').lower()
            for tech in technologies:
                if tech.lower() in content:
                    tech_mentions[tech] = tech_mentions.get(tech, 0) + 1

        # Return top mentioned technologies
        sorted_techs = sorted(tech_mentions.items(), key=lambda x: x[1], reverse=True)
        return [tech for tech, count in sorted_techs[:5]]

    def _identify_content_gaps(self, crawl_data: List[Dict]) -> List[str]:
        """Identify content gaps in the market"""
        gaps = []
        expected_content = [
            "getting started guide", "api documentation", "case studies",
            "integration examples", "security documentation", "pricing calculator",
            "customer testimonials", "feature comparison"
        ]

        content_found = {}
        for page in crawl_data:
            content = page.get('markdown', '').lower()
            for expected in expected_content:
                if any(word in content for word in expected.split()):
                    content_found[expected] = content_found.get(expected, 0) + 1

        # Identify missing or underrepresented content
        total_pages = len(crawl_data)
        for expected in expected_content:
            if content_found.get(expected, 0) < total_pages * 0.3:  # Less than 30% coverage
                gaps.append(f"Lacking sufficient {expected}")

        return gaps

    def _identify_market_opportunities(self, crawl_data: List[Dict]) -> List[str]:
        """Identify market opportunities based on analysis"""
        opportunities = []

        # Analyze for opportunities based on gaps and patterns
        all_content = ' '.join([page.get('markdown', '') for page in crawl_data])

        # Look for pain points mentioned
        pain_indicators = ["difficult", "complex", "expensive", "time-consuming", "manual"]
        for indicator in pain_indicators:
            if indicator in all_content.lower():
                opportunities.append(f"Opportunity to simplify/automate {indicator} processes")

        # Look for emerging trends
        trend_indicators = ["new", "innovative", "cutting-edge", "next-generation"]
        for indicator in trend_indicators:
            if indicator in all_content.lower():
                opportunities.append(f"Market moving toward {indicator} solutions")

        return opportunities[:3]  # Top 3 opportunities

    # Pricing analysis helper methods
    def _identify_pricing_model(self, content: str) -> str:
        """Identify the pricing model"""
        content_lower = content.lower()

        if 'free' in content_lower and ('trial' in content_lower or 'plan' in content_lower):
            return "Freemium"
        elif 'subscription' in content_lower or 'monthly' in content_lower:
            return "Subscription"
        elif 'usage' in content_lower or 'pay-as-you' in content_lower:
            return "Usage-based"
        elif 'one-time' in content_lower or 'lifetime' in content_lower:
            return "One-time purchase"
        else:
            return "Pricing model unclear"

    def _extract_price_points(self, content: str) -> List[str]:
        """Extract price points from content"""
        import re
        price_pattern = r'\$[\d,]+(?:\.\d{2})?'
        prices = re.findall(price_pattern, content)
        return list(set(prices))  # Remove duplicates

    def _extract_pricing_plans(self, content: str) -> List[str]:
        """Extract pricing plan names"""
        plan_indicators = ['plan', 'tier', 'package']
        lines = content.split('\n')
        plans = []

        for line in lines:
            if any(indicator in line.lower() for indicator in plan_indicators):
                # Extract plan names (basic heuristic)
                words = line.split()
                for i, word in enumerate(words):
                    if any(indicator in word.lower() for indicator in plan_indicators):
                        if i > 0:
                            plans.append(words[i-1])
                        if i < len(words) - 1:
                            plans.append(words[i+1])

        return list(set(plans))[:5]  # Top 5 unique plans

    def _check_free_tier(self, content: str) -> bool:
        """Check if there's a free tier"""
        return 'free' in content.lower() and ('tier' in content.lower() or 'plan' in content.lower())

    def _check_enterprise_pricing(self, content: str) -> bool:
        """Check if enterprise pricing is mentioned"""
        return 'enterprise' in content.lower() and ('pricing' in content.lower() or 'contact' in content.lower())

    # Content analysis helper methods
    def _calculate_readability(self, content: str) -> str:
        """Calculate basic readability score"""
        words = len(content.split())
        sentences = content.count('.') + content.count('!') + content.count('?')

        if sentences == 0:
            return "Unable to calculate"

        avg_words_per_sentence = words / sentences

        if avg_words_per_sentence < 15:
            return "Easy"
        elif avg_words_per_sentence < 20:
            return "Moderate"
        else:
            return "Difficult"

    def _analyze_keywords(self, content: str) -> Dict[str, int]:
        """Analyze keyword density"""
        words = content.lower().split()
        word_count = {}

        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}

        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1

        # Return top 10 keywords
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_words[:10])

    def _analyze_structure(self, content: str) -> Dict[str, int]:
        """Analyze content structure"""
        lines = content.split('\n')
        return {
            "headings": len([line for line in lines if line.startswith('#')]),
            "paragraphs": len([line for line in lines if len(line) > 50 and not line.startswith('#')]),
            "lists": len([line for line in lines if line.strip().startswith(('-', '*', '•'))]),
            "links": content.count('http')
        }

    def _extract_ctas(self, content: str) -> List[str]:
        """Extract call-to-action phrases"""
        cta_patterns = [
            'sign up', 'get started', 'try now', 'download', 'buy now',
            'learn more', 'contact us', 'request demo', 'start free trial'
        ]

        ctas = []
        content_lower = content.lower()

        for pattern in cta_patterns:
            if pattern in content_lower:
                ctas.append(pattern)

        return ctas

    def _extract_social_proof(self, content: str) -> List[str]:
        """Extract social proof elements"""
        social_proof = []
        content_lower = content.lower()

        proof_indicators = [
            'testimonial', 'review', 'customer story', 'case study',
            'trusted by', 'used by', 'customers', 'rating'
        ]

        for indicator in proof_indicators:
            if indicator in content_lower:
                social_proof.append(indicator)

        return social_proof

    def _format_content_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format content analysis results"""
        return f"""
# Content Analysis Results

## Content Metrics
**Length**: {analysis['content_length']} characters
**Readability**: {analysis['readability_score']}

## Structure Analysis
**Headings**: {analysis['content_structure']['headings']}
**Paragraphs**: {analysis['content_structure']['paragraphs']}
**Lists**: {analysis['content_structure']['lists']}
**External Links**: {analysis['content_structure']['links']}

## Keyword Density (Top Keywords)
{chr(10).join(f"• {keyword}: {count}" for keyword, count in analysis['keyword_density'].items())}

## Call-to-Actions Found
{chr(10).join(f"• {cta}" for cta in analysis['call_to_actions'])}

## Social Proof Elements
{chr(10).join(f"• {proof}" for proof in analysis['social_proof'])}
"""