"""
Telegram Notification Tool - Real-time notifications and human-in-the-loop approvals
Primary interface for Devlar AI Workforce communication and control
"""

import os
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

import requests
from loguru import logger
from crewai.tools import BaseTool

class TelegramNotificationTool(BaseTool):
    """
    Telegram notification tool for real-time communication and approvals.
    Handles notifications, status updates, and human-in-the-loop workflows.
    """

    name: str = "telegram_notification"
    description: str = (
        "Send notifications, status updates, and approval requests via Telegram. "
        "Primary communication channel for workforce updates and human oversight."
    )

    def __init__(self):
        super().__init__()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session = requests.Session()

    def _run(
        self,
        message: str,
        message_type: str = "info",
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
        reply_markup: Optional[Dict] = None
    ) -> str:
        """
        Send Telegram notification

        Args:
            message: Message content to send
            message_type: Type of message (info, warning, error, success, approval)
            parse_mode: Message parsing mode (Markdown, HTML, or None)
            disable_notification: Whether to disable notification sound
            reply_markup: Optional inline keyboard for interactive messages

        Returns:
            Delivery status and message info
        """
        try:
            logger.info(f"📱 Sending Telegram {message_type}: {message[:50]}...")

            # Format message based on type
            formatted_message = self._format_message(message, message_type)

            # Send message
            result = self._send_message(
                formatted_message,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                reply_markup=reply_markup
            )

            return f"✅ Telegram message sent successfully (Message ID: {result.get('message_id', 'unknown')})"

        except Exception as e:
            logger.error(f"❌ Telegram notification failed: {e}")
            return f"Failed to send Telegram notification: {str(e)}"

    def _send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
        disable_notification: bool = False,
        reply_markup: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Send message via Telegram Bot API"""

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_notification": disable_notification
        }

        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        response = self.session.post(
            f"{self.base_url}/sendMessage",
            data=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()["result"]

    def _format_message(self, message: str, message_type: str) -> str:
        """Format message with appropriate emoji and styling"""

        # Message type icons and formatting
        type_formats = {
            "info": {"icon": "ℹ️", "prefix": "**INFO**"},
            "warning": {"icon": "⚠️", "prefix": "**WARNING**"},
            "error": {"icon": "❌", "prefix": "**ERROR**"},
            "success": {"icon": "✅", "prefix": "**SUCCESS**"},
            "approval": {"icon": "🚨", "prefix": "**APPROVAL REQUIRED**"},
            "status": {"icon": "📊", "prefix": "**STATUS UPDATE**"},
            "task_start": {"icon": "🚀", "prefix": "**TASK STARTED**"},
            "task_complete": {"icon": "🎉", "prefix": "**TASK COMPLETED**"},
            "cost_alert": {"icon": "💰", "prefix": "**COST ALERT**"},
            "deployment": {"icon": "🚀", "prefix": "**DEPLOYMENT**"}
        }

        format_info = type_formats.get(message_type, {"icon": "💬", "prefix": "**MESSAGE**"})

        timestamp = datetime.now().strftime("%H:%M:%S")

        formatted = f"{format_info['icon']} {format_info['prefix']}\n"
        formatted += f"⏰ *{timestamp}*\n\n"
        formatted += f"{message}\n\n"
        formatted += "---\n"
        formatted += f"🤖 *Devlar AI Workforce*"

        return formatted

    async def send_notification(self, message: str, message_type: str = "info") -> str:
        """Async wrapper for sending notifications"""
        return self._run(message, message_type)

    async def send_approval_request(
        self,
        task: str,
        estimated_cost: float,
        details: Dict[str, Any],
        timeout_minutes: int = 30
    ) -> str:
        """Send approval request with interactive buttons"""

        approval_message = f"""
🚨 **APPROVAL REQUIRED**

**Task**: {task}
**Estimated Cost**: ${estimated_cost:.2f}
**Timeout**: {timeout_minutes} minutes

**Details**:
{self._format_details(details)}

**Decision Required**: This operation exceeds the automatic approval threshold of €50.

Please respond with:
• ✅ `approve` to proceed
• ❌ `deny` to cancel
• 📋 `details` for more information
"""

        # Create inline keyboard for quick responses
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve", "callback_data": f"approve_{task[:20]}"},
                    {"text": "❌ Deny", "callback_data": f"deny_{task[:20]}"}
                ],
                [
                    {"text": "📋 More Details", "callback_data": f"details_{task[:20]}"}
                ]
            ]
        }

        return self._run(
            approval_message,
            message_type="approval",
            reply_markup=reply_markup
        )

    async def send_task_status(
        self,
        execution_id: str,
        status: str,
        progress: Dict[str, Any],
        estimated_completion: Optional[str] = None
    ) -> str:
        """Send task status update"""

        status_message = f"""
📊 **TASK STATUS UPDATE**

**Execution ID**: `{execution_id}`
**Status**: {self._get_status_emoji(status)} {status.upper()}

**Progress**:
{self._format_progress(progress)}

{f"**Estimated Completion**: {estimated_completion}" if estimated_completion else ""}

**Pod Activity**:
{self._format_pod_activity(progress.get('pods', {}))}
"""

        return self._run(status_message, message_type="status")

    async def send_task_completion(
        self,
        execution_id: str,
        goal: str,
        results: Dict[str, Any],
        execution_time: float,
        report_path: Optional[str] = None
    ) -> str:
        """Send task completion notification"""

        completion_message = f"""
🎉 **TASK COMPLETED**

**Goal**: {goal}
**Execution ID**: `{execution_id}`
**Execution Time**: {self._format_execution_time(execution_time)}

**Results Summary**:
{self._format_results_summary(results)}

{f"**📋 Report**: {report_path}" if report_path else ""}

**Next Steps**: Review results and consider follow-up actions.
"""

        return self._run(completion_message, message_type="task_complete")

    async def send_error_alert(
        self,
        execution_id: str,
        error: str,
        context: Dict[str, Any],
        recovery_suggestions: List[str] = None
    ) -> str:
        """Send error alert with recovery suggestions"""

        error_message = f"""
❌ **ERROR ALERT**

**Execution ID**: `{execution_id}`
**Error**: {error}

**Context**:
{self._format_details(context)}

{self._format_recovery_suggestions(recovery_suggestions) if recovery_suggestions else ""}

**Action Required**: Manual intervention may be needed.
"""

        return self._run(error_message, message_type="error")

    async def send_cost_alert(
        self,
        current_spend: float,
        budget_limit: float,
        time_period: str,
        top_expenses: List[Dict[str, Any]]
    ) -> str:
        """Send cost monitoring alert"""

        cost_message = f"""
💰 **COST ALERT**

**Current Spend**: ${current_spend:.2f}
**Budget Limit**: ${budget_limit:.2f}
**Usage**: {(current_spend/budget_limit*100):.1f}%
**Period**: {time_period}

**Top Expenses**:
{self._format_expenses(top_expenses)}

**Recommendation**: {"🚨 Immediate attention required" if current_spend > budget_limit * 0.9 else "📊 Monitor closely"}
"""

        return self._run(cost_message, message_type="cost_alert")

    async def send_deployment_notification(
        self,
        service: str,
        environment: str,
        status: str,
        details: Dict[str, Any]
    ) -> str:
        """Send deployment status notification"""

        deployment_message = f"""
🚀 **DEPLOYMENT UPDATE**

**Service**: {service}
**Environment**: {environment.upper()}
**Status**: {self._get_deployment_emoji(status)} {status.upper()}

**Details**:
{self._format_deployment_details(details)}

**Monitoring**: {details.get('monitoring_url', 'Setup in progress')}
"""

        return self._run(deployment_message, message_type="deployment")

    # Helper methods for formatting

    def _format_details(self, details: Dict[str, Any]) -> str:
        """Format details dictionary for display"""
        if not details:
            return "No additional details"

        formatted = ""
        for key, value in details.items():
            if isinstance(value, dict):
                formatted += f"• **{key.title()}**:\n"
                for sub_key, sub_value in value.items():
                    formatted += f"  - {sub_key}: {sub_value}\n"
            else:
                formatted += f"• **{key.title()}**: {value}\n"

        return formatted

    def _format_progress(self, progress: Dict[str, Any]) -> str:
        """Format progress information"""
        if not progress:
            return "No progress data available"

        formatted = ""

        # Overall progress
        if 'overall_progress' in progress:
            formatted += f"• **Overall**: {progress['overall_progress']}%\n"

        # Current stage
        if 'current_stage' in progress:
            formatted += f"• **Current Stage**: {progress['current_stage']}\n"

        # Tasks completed/total
        if 'tasks_completed' in progress and 'total_tasks' in progress:
            formatted += f"• **Tasks**: {progress['tasks_completed']}/{progress['total_tasks']}\n"

        # Time elapsed
        if 'time_elapsed' in progress:
            formatted += f"• **Elapsed**: {self._format_execution_time(progress['time_elapsed'])}\n"

        return formatted

    def _format_pod_activity(self, pods: Dict[str, Any]) -> str:
        """Format pod activity status"""
        if not pods:
            return "No pod activity data"

        formatted = ""
        for pod_name, pod_status in pods.items():
            status_emoji = "🔄" if pod_status.get('status') == 'active' else "✅" if pod_status.get('status') == 'completed' else "⏸️"
            formatted += f"• {status_emoji} **{pod_name}**: {pod_status.get('current_task', 'idle')}\n"

        return formatted

    def _format_results_summary(self, results: Dict[str, Any]) -> str:
        """Format results summary"""
        if not results:
            return "No results data available"

        formatted = ""

        # Success/failure counts
        if 'successful_tasks' in results:
            formatted += f"• **Successful Tasks**: {results['successful_tasks']}\n"

        if 'failed_tasks' in results:
            formatted += f"• **Failed Tasks**: {results['failed_tasks']}\n"

        # Key deliverables
        if 'deliverables' in results:
            formatted += f"• **Deliverables**: {len(results['deliverables'])} items\n"

        # Quality score
        if 'quality_score' in results:
            formatted += f"• **Quality Score**: {results['quality_score']}/100\n"

        return formatted

    def _format_recovery_suggestions(self, suggestions: List[str]) -> str:
        """Format recovery suggestions"""
        if not suggestions:
            return ""

        formatted = "\n**Recovery Suggestions**:\n"
        for i, suggestion in enumerate(suggestions, 1):
            formatted += f"{i}. {suggestion}\n"

        return formatted

    def _format_expenses(self, expenses: List[Dict[str, Any]]) -> str:
        """Format expense list"""
        if not expenses:
            return "No expense data"

        formatted = ""
        for expense in expenses[:5]:  # Top 5
            formatted += f"• {expense.get('service', 'Unknown')}: ${expense.get('amount', 0):.2f}\n"

        return formatted

    def _format_deployment_details(self, details: Dict[str, Any]) -> str:
        """Format deployment details"""
        formatted = ""

        if 'commit' in details:
            formatted += f"• **Commit**: {details['commit'][:7]}\n"

        if 'branch' in details:
            formatted += f"• **Branch**: {details['branch']}\n"

        if 'deploy_time' in details:
            formatted += f"• **Deploy Time**: {details['deploy_time']}\n"

        if 'health_check' in details:
            formatted += f"• **Health Check**: {details['health_check']}\n"

        return formatted

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        status_emojis = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️",
            "cancelled": "🚫"
        }
        return status_emojis.get(status.lower(), "❓")

    def _get_deployment_emoji(self, status: str) -> str:
        """Get emoji for deployment status"""
        deployment_emojis = {
            "deploying": "🚀",
            "success": "✅",
            "failed": "❌",
            "rollback": "⏪",
            "pending": "⏳"
        }
        return deployment_emojis.get(status.lower(), "❓")

    def _format_execution_time(self, seconds: float) -> str:
        """Format execution time in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"

    # Bot management methods
    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information"""
        try:
            response = self.session.get(f"{self.base_url}/getMe", timeout=10)
            response.raise_for_status()
            return response.json()["result"]
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return {"error": str(e)}

    async def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook for receiving updates"""
        try:
            payload = {"url": webhook_url}
            response = self.session.post(
                f"{self.base_url}/setWebhook",
                data=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["ok"]
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
            return False

    async def delete_webhook(self) -> bool:
        """Delete webhook"""
        try:
            response = self.session.post(
                f"{self.base_url}/deleteWebhook",
                timeout=30
            )
            response.raise_for_status()
            return response.json()["ok"]
        except Exception as e:
            logger.error(f"Failed to delete webhook: {e}")
            return False