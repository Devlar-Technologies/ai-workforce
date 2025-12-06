"""
Instantly.ai Email Automation Tool - Cold outreach and email sequences
Automated email campaigns for lead nurturing and sales outreach
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from crewai.tools import BaseTool
from loguru import logger


@dataclass
class EmailTemplate:
    """Email template data structure"""
    subject: str
    body: str
    variables: List[str]
    step_number: int
    delay_days: int


@dataclass
class Lead:
    """Lead data structure for email campaigns"""
    email: str
    first_name: str
    last_name: str
    company: str
    title: str
    custom_variables: Dict[str, str]


class InstantlyEmailTool(BaseTool):
    """
    Instantly.ai email automation tool for cold outreach campaigns
    Handles email sequences, lead management, and campaign automation
    """

    name: str = "instantly_email_automation"
    description: str = (
        "Automate cold email campaigns using Instantly.ai. Create email sequences, "
        "manage leads, send personalized outreach, and track campaign performance. "
        "Perfect for sales outreach and lead nurturing workflows."
    )

    def __init__(self):
        """Initialize Instantly.ai tool with API credentials"""
        self.api_key = os.getenv("INSTANTLY_API_KEY")
        self.base_url = "https://api.instantly.ai"

        if not self.api_key:
            logger.warning("INSTANTLY_API_KEY not found - some features will be limited")

        # API endpoints
        self.endpoints = {
            "campaigns": "/v1/campaigns",
            "leads": "/v1/leads",
            "sequences": "/v1/sequences",
            "analytics": "/v1/analytics",
            "templates": "/v1/templates"
        }

        logger.info("📧 Instantly.ai Email Tool initialized")

    def _run(
        self,
        action: str,
        campaign_name: str = None,
        email_sequence: List[Dict[str, Any]] = None,
        leads: List[Dict[str, str]] = None,
        template_data: Dict[str, Any] = None,
        analytics_period: str = "7d"
    ) -> str:
        """
        Execute Instantly.ai email automation action

        Args:
            action: Action to perform (create_campaign, add_leads, create_sequence, etc.)
            campaign_name: Name of the email campaign
            email_sequence: List of email templates with timing
            leads: List of lead data for targeting
            template_data: Email template configuration
            analytics_period: Time period for analytics (7d, 30d, 90d)

        Returns:
            Action results and campaign information
        """
        try:
            if not self.api_key:
                return self._simulate_email_automation(action, campaign_name, email_sequence, leads)

            if action == "create_campaign":
                return self._create_email_campaign(campaign_name, email_sequence)
            elif action == "add_leads":
                return self._add_leads_to_campaign(campaign_name, leads)
            elif action == "create_sequence":
                return self._create_email_sequence(email_sequence)
            elif action == "send_test_email":
                return self._send_test_email(template_data)
            elif action == "get_analytics":
                return self._get_campaign_analytics(campaign_name, analytics_period)
            elif action == "create_template":
                return self._create_email_template(template_data)
            elif action == "schedule_campaign":
                return self._schedule_campaign(campaign_name, template_data.get("schedule_time"))
            else:
                return f"❌ Unknown action: {action}"

        except Exception as e:
            logger.error(f"Instantly.ai tool error: {e}")
            return f"❌ Email automation failed: {str(e)}"

    def _create_email_campaign(self, campaign_name: str, email_sequence: List[Dict[str, Any]]) -> str:
        """Create new email campaign with sequence"""
        logger.info(f"📧 Creating campaign: {campaign_name}")

        campaign_data = {
            "name": campaign_name,
            "status": "draft",
            "sequence": email_sequence,
            "settings": {
                "daily_limit": 50,
                "time_zone": "UTC",
                "sending_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "sending_hours": {"start": "09:00", "end": "17:00"},
                "track_opens": True,
                "track_clicks": True,
                "personalization": True
            }
        }

        response = self._make_request("POST", self.endpoints["campaigns"], campaign_data)

        if response.get("success"):
            campaign_id = response.get("campaign_id")
            return f"✅ Campaign '{campaign_name}' created (ID: {campaign_id})\n📧 Sequence: {len(email_sequence)} emails configured"
        else:
            return f"❌ Failed to create campaign: {response.get('error', 'Unknown error')}"

    def _add_leads_to_campaign(self, campaign_name: str, leads: List[Dict[str, str]]) -> str:
        """Add leads to existing campaign"""
        logger.info(f"👥 Adding {len(leads)} leads to campaign: {campaign_name}")

        # Validate lead data
        validated_leads = []
        for lead in leads:
            if self._validate_lead(lead):
                validated_leads.append(lead)

        if not validated_leads:
            return "❌ No valid leads to add"

        lead_data = {
            "campaign_name": campaign_name,
            "leads": validated_leads,
            "options": {
                "skip_duplicates": True,
                "validate_emails": True
            }
        }

        response = self._make_request("POST", self.endpoints["leads"], lead_data)

        if response.get("success"):
            added_count = response.get("leads_added", len(validated_leads))
            skipped_count = len(leads) - added_count
            return f"✅ Added {added_count} leads to '{campaign_name}'\n📊 Skipped {skipped_count} invalid/duplicate leads"
        else:
            return f"❌ Failed to add leads: {response.get('error', 'Unknown error')}"

    def _create_email_sequence(self, email_sequence: List[Dict[str, Any]]) -> str:
        """Create email sequence template"""
        logger.info(f"📝 Creating email sequence with {len(email_sequence)} steps")

        # Validate sequence
        if not email_sequence or len(email_sequence) == 0:
            return "❌ Empty email sequence provided"

        sequence_data = {
            "name": f"Sequence_{datetime.now().strftime('%Y%m%d_%H%M')}",
            "steps": [],
            "settings": {
                "stop_on_reply": True,
                "stop_on_click": False,
                "personalization_enabled": True
            }
        }

        for i, email in enumerate(email_sequence):
            step = {
                "step_number": i + 1,
                "type": "email",
                "subject": email.get("subject", f"Follow-up #{i + 1}"),
                "body": email.get("body", ""),
                "delay_days": email.get("delay_days", i * 2 if i > 0 else 0),
                "variables": email.get("variables", [])
            }
            sequence_data["steps"].append(step)

        response = self._make_request("POST", self.endpoints["sequences"], sequence_data)

        if response.get("success"):
            sequence_id = response.get("sequence_id")
            return f"✅ Email sequence created (ID: {sequence_id})\n📧 {len(email_sequence)} email steps configured"
        else:
            return f"❌ Failed to create sequence: {response.get('error', 'Unknown error')}"

    def _send_test_email(self, template_data: Dict[str, Any]) -> str:
        """Send test email to verify template"""
        test_email = template_data.get("test_email", "test@example.com")
        subject = template_data.get("subject", "Test Email")

        test_data = {
            "to": test_email,
            "subject": subject,
            "body": template_data.get("body", ""),
            "variables": template_data.get("variables", {})
        }

        response = self._make_request("POST", "/v1/test-email", test_data)

        if response.get("success"):
            return f"✅ Test email sent to {test_email}\n📧 Subject: {subject}"
        else:
            return f"❌ Failed to send test email: {response.get('error', 'Unknown error')}"

    def _get_campaign_analytics(self, campaign_name: str, period: str) -> str:
        """Get campaign performance analytics"""
        logger.info(f"📊 Fetching analytics for campaign: {campaign_name}")

        params = {
            "campaign": campaign_name,
            "period": period,
            "metrics": ["sent", "opened", "clicked", "replied", "bounced"]
        }

        response = self._make_request("GET", self.endpoints["analytics"], params=params)

        if response.get("success"):
            metrics = response.get("metrics", {})

            return self._format_analytics_report(campaign_name, metrics, period)
        else:
            return f"❌ Failed to fetch analytics: {response.get('error', 'Unknown error')}"

    def _create_email_template(self, template_data: Dict[str, Any]) -> str:
        """Create reusable email template"""
        template_name = template_data.get("name", f"Template_{datetime.now().strftime('%Y%m%d_%H%M')}")

        template_config = {
            "name": template_name,
            "subject": template_data.get("subject", ""),
            "body": template_data.get("body", ""),
            "variables": template_data.get("variables", []),
            "category": template_data.get("category", "general"),
            "tags": template_data.get("tags", [])
        }

        response = self._make_request("POST", self.endpoints["templates"], template_config)

        if response.get("success"):
            template_id = response.get("template_id")
            return f"✅ Email template '{template_name}' created (ID: {template_id})"
        else:
            return f"❌ Failed to create template: {response.get('error', 'Unknown error')}"

    def _schedule_campaign(self, campaign_name: str, schedule_time: str) -> str:
        """Schedule campaign for future sending"""
        schedule_data = {
            "campaign": campaign_name,
            "action": "schedule",
            "schedule_time": schedule_time,
            "timezone": "UTC"
        }

        response = self._make_request("POST", f"{self.endpoints['campaigns']}/schedule", schedule_data)

        if response.get("success"):
            return f"✅ Campaign '{campaign_name}' scheduled for {schedule_time}"
        else:
            return f"❌ Failed to schedule campaign: {response.get('error', 'Unknown error')}"

    def _validate_lead(self, lead: Dict[str, str]) -> bool:
        """Validate lead data"""
        required_fields = ["email", "first_name"]

        for field in required_fields:
            if not lead.get(field):
                logger.warning(f"Lead missing required field: {field}")
                return False

        # Basic email validation
        email = lead.get("email", "")
        if "@" not in email or "." not in email:
            logger.warning(f"Invalid email format: {email}")
            return False

        return True

    def _format_analytics_report(self, campaign_name: str, metrics: Dict[str, Any], period: str) -> str:
        """Format analytics data into readable report"""
        sent = metrics.get("sent", 0)
        opened = metrics.get("opened", 0)
        clicked = metrics.get("clicked", 0)
        replied = metrics.get("replied", 0)
        bounced = metrics.get("bounced", 0)

        # Calculate rates
        open_rate = (opened / sent * 100) if sent > 0 else 0
        click_rate = (clicked / opened * 100) if opened > 0 else 0
        reply_rate = (replied / sent * 100) if sent > 0 else 0
        bounce_rate = (bounced / sent * 100) if sent > 0 else 0

        report = f"""📊 Campaign Analytics: {campaign_name}
📅 Period: {period}

📈 Performance Metrics:
• Emails Sent: {sent:,}
• Opened: {opened:,} ({open_rate:.1f}%)
• Clicked: {clicked:,} ({click_rate:.1f}%)
• Replied: {replied:,} ({reply_rate:.1f}%)
• Bounced: {bounced:,} ({bounce_rate:.1f}%)

🎯 Key Insights:
• Open rate is {'above' if open_rate > 25 else 'below'} industry average (25%)
• Reply rate is {'excellent' if reply_rate > 5 else 'good' if reply_rate > 2 else 'needs improvement'}
• Bounce rate is {'concerning' if bounce_rate > 5 else 'healthy'} ({bounce_rate:.1f}%)
"""

        return report

    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make API request to Instantly.ai"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.error(f"Instantly.ai API request failed: {e}")
            return {"success": False, "error": str(e)}

    def _simulate_email_automation(self, action: str, campaign_name: str,
                                 email_sequence: List[Dict[str, Any]],
                                 leads: List[Dict[str, str]]) -> str:
        """Simulate email automation when API key is not available"""
        logger.info(f"🎭 Simulating Instantly.ai action: {action}")

        if action == "create_campaign":
            return f"""✅ [SIMULATION] Campaign '{campaign_name}' created
📧 Email sequence configured: {len(email_sequence or [])} emails
⚙️ Settings: Daily limit 50, business hours only
🎯 Ready to add leads and launch campaign"""

        elif action == "add_leads":
            lead_count = len(leads or [])
            return f"""✅ [SIMULATION] Added {lead_count} leads to '{campaign_name}'
👥 Lead validation: {lead_count} valid, 0 duplicates
📊 Campaign ready for launch"""

        elif action == "create_sequence":
            steps = len(email_sequence or [])
            return f"""✅ [SIMULATION] Email sequence created
📝 {steps} email steps configured
⏰ Timing: Initial email + follow-ups every 2-3 days
🎯 Personalization variables ready"""

        elif action == "get_analytics":
            return f"""📊 [SIMULATION] Campaign Analytics: {campaign_name}
📈 Performance Metrics:
• Emails Sent: 1,250
• Opened: 387 (31.0%)
• Clicked: 58 (15.0%)
• Replied: 23 (1.8%)
• Bounced: 12 (1.0%)

🎯 Insights: Strong open rate, good reply rate for cold outreach"""

        else:
            return f"✅ [SIMULATION] {action} completed successfully"

    # Helper methods for common email automation workflows

    def create_cold_outreach_sequence(self,
                                    value_proposition: str,
                                    target_persona: str,
                                    company_name: str = "your company") -> List[Dict[str, Any]]:
        """Create a proven cold outreach email sequence"""

        sequences = [
            {
                "subject": "Quick question about {{company}}'s {{pain_point}}",
                "body": f"""Hi {{first_name}},

I noticed {{company}} is in the {target_persona} space and thought you might be interested in how we've helped similar companies {value_proposition}.

Would it make sense to have a brief 15-minute conversation about how {{company}} currently handles {{specific_challenge}}?

Best regards,
{{sender_name}}
{company_name}

P.S. I saw your recent {{recent_activity}} - impressive work!""",
                "delay_days": 0,
                "variables": ["first_name", "company", "pain_point", "specific_challenge", "recent_activity", "sender_name"]
            },
            {
                "subject": "Re: {{company}}'s {{pain_point}} - 2 minute read",
                "body": f"""Hi {{first_name}},

I sent you a note last week about {value_proposition}.

I wanted to share a quick case study of how we helped {{similar_company}} achieve {{specific_result}} in just {{timeframe}}.

Here's what we did:
• {{benefit_1}}
• {{benefit_2}}
• {{benefit_3}}

Worth a 15-minute conversation to see if this could work for {{company}}?

Best,
{{sender_name}}""",
                "delay_days": 4,
                "variables": ["first_name", "company", "pain_point", "similar_company", "specific_result", "timeframe", "benefit_1", "benefit_2", "benefit_3", "sender_name"]
            },
            {
                "subject": "{{first_name}}, breaking up with you 😢",
                "body": f"""Hi {{first_name}},

I've reached out a couple of times about {value_proposition} for {{company}}, but haven't heard back.

I don't want to be that person who keeps emailing, so this is my last note.

If you're ever curious about how companies like {{company}} are {{achieving_outcome}}, feel free to reach out.

Otherwise, I'll assume it's not a priority right now and won't bug you again.

Best of luck with {{company}}!

{{sender_name}}""",
                "delay_days": 7,
                "variables": ["first_name", "company", "achieving_outcome", "sender_name"]
            }
        ]

        return sequences

    def create_nurture_sequence(self, industry: str, content_topics: List[str]) -> List[Dict[str, Any]]:
        """Create a lead nurturing email sequence"""

        sequences = []

        for i, topic in enumerate(content_topics):
            email = {
                "subject": f"Insight #{i+1}: {topic} in {industry}",
                "body": f"""Hi {{first_name}},

Hope you're doing well! I wanted to share an insight about {topic} that's particularly relevant for {industry} companies like {{company}}.

{{content_preview}}

Key takeaway: {{key_insight}}

You can read the full analysis here: {{content_link}}

Would love to hear your thoughts on this - are you seeing similar trends at {{company}}?

Best,
{{sender_name}}""",
                "delay_days": i * 7,  # Weekly emails
                "variables": ["first_name", "company", "content_preview", "key_insight", "content_link", "sender_name"]
            }
            sequences.append(email)

        return sequences