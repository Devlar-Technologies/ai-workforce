"""
Devlar AI Workforce - Telegram Bot Interface
Primary interface for interacting with the AI workforce through Telegram
"""

import os
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

from main import DevlarWorkforceCEO
from memory import WorkforceMemory
from utils import setup_logging

# Configure logging
logger = logging.getLogger(__name__)

class TelegramInterface:
    """
    Telegram bot interface for Devlar AI Workforce
    Provides conversational interface for task execution and monitoring
    """

    def __init__(self):
        """Initialize Telegram bot interface"""
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.authorized_users = self._load_authorized_users()
        self.ceo = DevlarWorkforceCEO()
        self.memory = WorkforceMemory()
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    def _load_authorized_users(self) -> List[int]:
        """Load authorized user IDs from environment or config"""
        users_str = os.getenv("TELEGRAM_AUTHORIZED_USERS", "")
        if users_str:
            try:
                return [int(user_id.strip()) for user_id in users_str.split(",")]
            except ValueError:
                logger.error("Invalid TELEGRAM_AUTHORIZED_USERS format")
                return []
        return []

    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        if not self.authorized_users:
            logger.warning("No authorized users configured - allowing all users")
            return True
        return user_id in self.authorized_users

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user_id = update.effective_user.id

        if not self._is_authorized(user_id):
            await update.message.reply_text(
                "❌ Unauthorized access. Contact admin for access."
            )
            return

        welcome_message = """
🤖 **Devlar AI Workforce - CEO Interface**

Welcome to your AI workforce command center! I'm your CEO orchestrator, ready to execute high-level business goals.

**What I can do:**
• 🔍 Market research and competitor analysis
• 🚀 Product development and feature implementation
• 📈 Marketing campaigns and user acquisition
• 💼 Sales outreach and lead generation
• 🎯 Customer success and support automation
• 📊 Analytics and performance optimization

**Commands:**
• `/execute <goal>` - Execute a business goal
• `/status` - Check active executions
• `/history` - View recent executions
• `/cancel <execution_id>` - Cancel execution
• `/help` - Show detailed help

**Examples:**
• `/execute Get 100 new Chromentum beta users`
• `/execute Research top 10 AI meditation apps and their pricing`
• `/execute Implement dark mode for TimePost dashboard`

Ready to scale your business? 🚀
        """

        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        if not self._is_authorized(update.effective_user.id):
            return

        help_message = """
📚 **Devlar AI Workforce - Detailed Help**

**Core Commands:**
• `/start` - Initialize bot interface
• `/execute <goal>` - Execute business goal
• `/status` - Check execution status
• `/history` - View execution history
• `/cancel <id>` - Cancel execution
• `/approve <id>` - Approve pending operation
• `/deny <id>` - Deny pending operation

**Execution Examples:**

**🔍 Research & Analysis:**
• `Research competitor pricing for Chrome extension market`
• `Analyze top 20 meditation apps features and user reviews`
• `Find potential integration partners for Zeneural`

**🚀 Product Development:**
• `Implement user authentication for TimePost`
• `Add dark mode toggle to Chromentum extension`
• `Create API documentation for AimStack`

**📈 Marketing & Growth:**
• `Launch beta user campaign for Chromentum with 100 signups`
• `Create content marketing strategy for Zeneural`
• `Set up email drip campaign for new users`

**💼 Sales & Outreach:**
• `Find 50 potential enterprise customers for AimStack`
• `Create personalized outreach sequence for SaaS prospects`
• `Research decision makers at target companies`

**🎯 Customer Success:**
• `Analyze user churn patterns in Chromentum`
• `Create onboarding flow optimization plan`
• `Set up automated support ticket classification`

**📊 Analytics & Optimization:**
• `Optimize TimePost landing page conversion rate`
• `Analyze user behavior in Zeneural meditation sessions`
• `Create performance monitoring dashboard`

**Approval System:**
Operations over €50 require approval. You'll receive notifications with:
• ✅ Approve - Proceed with operation
• ❌ Deny - Cancel operation
• 📋 Details - Get more information

**Status Monitoring:**
Real-time updates on execution progress, pod activity, and results.
        """

        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )

    async def execute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /execute command"""
        if not self._is_authorized(update.effective_user.id):
            return

        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a goal to execute.\n\n"
                "Example: `/execute Get 100 new Chromentum beta users`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        goal = " ".join(context.args)
        execution_id = str(uuid.uuid4())[:8]
        user_id = update.effective_user.id

        # Store execution info
        self.active_executions[execution_id] = {
            "goal": goal,
            "user_id": user_id,
            "chat_id": update.effective_chat.id,
            "status": "starting",
            "start_time": datetime.now(),
            "progress": {}
        }

        # Send initial confirmation
        keyboard = [
            [InlineKeyboardButton("📊 Check Status", callback_data=f"status_{execution_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{execution_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🚀 **Execution Started**\n\n"
            f"**Goal:** {goal}\n"
            f"**Execution ID:** `{execution_id}`\n"
            f"**Status:** Initializing workforce...\n\n"
            f"I'll keep you updated on progress. This may take several minutes for complex goals.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

        # Execute goal asynchronously
        asyncio.create_task(self._execute_goal_async(execution_id, goal))

    async def _execute_goal_async(self, execution_id: str, goal: str) -> None:
        """Execute goal asynchronously and send updates"""
        try:
            execution_info = self.active_executions[execution_id]
            chat_id = execution_info["chat_id"]

            # Update status
            execution_info["status"] = "analyzing"
            await self._send_status_update(chat_id, execution_id, "🔍 Analyzing goal and planning workflow...")

            # Execute with CEO
            results = await asyncio.to_thread(self.ceo.execute_goal, goal)

            # Update final status
            execution_info["status"] = "completed"
            execution_info["results"] = results
            execution_info["end_time"] = datetime.now()

            # Send completion message
            await self._send_completion_message(chat_id, execution_id, results)

        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}")
            execution_info = self.active_executions.get(execution_id, {})
            chat_id = execution_info.get("chat_id")

            if chat_id:
                await self._send_error_message(chat_id, execution_id, str(e))

            execution_info["status"] = "failed"
            execution_info["error"] = str(e)

    async def _send_status_update(self, chat_id: int, execution_id: str, message: str) -> None:
        """Send status update to user"""
        try:
            keyboard = [
                [InlineKeyboardButton("📊 Full Status", callback_data=f"status_{execution_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{execution_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await self.application.bot.send_message(
                chat_id=chat_id,
                text=f"📱 **Status Update**\n\n"
                     f"**Execution ID:** `{execution_id}`\n"
                     f"**Update:** {message}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to send status update: {e}")

    async def _send_completion_message(self, chat_id: int, execution_id: str, results: Dict[str, Any]) -> None:
        """Send execution completion message"""
        execution_info = self.active_executions[execution_id]
        duration = execution_info["end_time"] - execution_info["start_time"]

        # Format results summary
        results_summary = self._format_results_summary(results)

        completion_message = f"""
🎉 **Execution Completed**

**Goal:** {execution_info['goal']}
**Execution ID:** `{execution_id}`
**Duration:** {self._format_duration(duration)}
**Status:** ✅ SUCCESS

**Results Summary:**
{results_summary}

**Next Steps:**
• Review detailed results below
• Consider follow-up actions
• Use `/history` to see all executions
        """

        keyboard = [
            [InlineKeyboardButton("📋 Full Report", callback_data=f"report_{execution_id}")],
            [InlineKeyboardButton("📊 View History", callback_data="history")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.application.bot.send_message(
            chat_id=chat_id,
            text=completion_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def _send_error_message(self, chat_id: int, execution_id: str, error: str) -> None:
        """Send execution error message"""
        error_message = f"""
❌ **Execution Failed**

**Execution ID:** `{execution_id}`
**Error:** {error}

**What to try:**
• Check goal formatting and clarity
• Ensure all required environment variables are set
• Try a simpler goal to test the system
• Contact support if issue persists

**Recovery:**
• Use `/execute` to start a new execution
• Use `/status` to check system health
        """

        keyboard = [
            [InlineKeyboardButton("🔄 Try Again", callback_data=f"retry_{execution_id}")],
            [InlineKeyboardButton("💬 Get Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.application.bot.send_message(
            chat_id=chat_id,
            text=error_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        if not self._is_authorized(update.effective_user.id):
            return

        if not self.active_executions:
            await update.message.reply_text(
                "📊 **System Status**\n\n"
                "✅ System healthy\n"
                "🎯 No active executions\n\n"
                "Use `/execute <goal>` to start a new execution.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        status_message = "📊 **Active Executions**\n\n"

        for exec_id, exec_info in self.active_executions.items():
            if exec_info["status"] in ["completed", "failed"]:
                continue

            duration = datetime.now() - exec_info["start_time"]
            status_icon = self._get_status_icon(exec_info["status"])

            status_message += f"**{exec_id}** {status_icon}\n"
            status_message += f"└ Goal: {exec_info['goal'][:50]}...\n"
            status_message += f"└ Duration: {self._format_duration(duration)}\n"
            status_message += f"└ Status: {exec_info['status'].title()}\n\n"

        keyboard = []
        for exec_id in self.active_executions:
            if self.active_executions[exec_id]["status"] not in ["completed", "failed"]:
                keyboard.append([
                    InlineKeyboardButton(f"📋 Details {exec_id}", callback_data=f"status_{exec_id}"),
                    InlineKeyboardButton(f"❌ Cancel {exec_id}", callback_data=f"cancel_{exec_id}")
                ])

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        await update.message.reply_text(
            status_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /history command"""
        if not self._is_authorized(update.effective_user.id):
            return

        try:
            # Get recent executions from memory
            recent_executions = await asyncio.to_thread(
                self.memory.get_recent_executions,
                limit=10
            )

            if not recent_executions:
                await update.message.reply_text(
                    "📚 **Execution History**\n\n"
                    "No previous executions found.\n\n"
                    "Use `/execute <goal>` to start your first execution.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            history_message = "📚 **Recent Executions**\n\n"

            for i, execution in enumerate(recent_executions, 1):
                status_icon = "✅" if execution.get("success") else "❌"
                timestamp = execution.get("timestamp", "Unknown")
                goal = execution.get("goal", "Unknown goal")[:40]

                history_message += f"**{i}.** {status_icon} {goal}...\n"
                history_message += f"└ Time: {timestamp}\n\n"

            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="history")],
                [InlineKeyboardButton("📊 Current Status", callback_data="status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                history_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            await update.message.reply_text(
                "❌ Failed to fetch execution history. Please try again.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /cancel command"""
        if not self._is_authorized(update.effective_user.id):
            return

        if not context.args:
            await update.message.reply_text(
                "❌ Please provide an execution ID to cancel.\n\n"
                "Example: `/cancel abc123`\n"
                "Use `/status` to see active executions.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        execution_id = context.args[0]

        if execution_id not in self.active_executions:
            await update.message.reply_text(
                f"❌ Execution `{execution_id}` not found.\n\n"
                "Use `/status` to see active executions.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Cancel execution
        execution_info = self.active_executions[execution_id]
        execution_info["status"] = "cancelled"
        execution_info["end_time"] = datetime.now()

        await update.message.reply_text(
            f"❌ **Execution Cancelled**\n\n"
            f"**Execution ID:** `{execution_id}`\n"
            f"**Goal:** {execution_info['goal']}\n\n"
            f"The execution has been cancelled and resources freed.",
            parse_mode=ParseMode.MARKDOWN
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard callbacks"""
        if not self._is_authorized(update.effective_user.id):
            return

        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith("status_"):
            execution_id = data.replace("status_", "")
            await self._handle_status_callback(query, execution_id)
        elif data.startswith("cancel_"):
            execution_id = data.replace("cancel_", "")
            await self._handle_cancel_callback(query, execution_id)
        elif data.startswith("approve_"):
            approval_id = data.replace("approve_", "")
            await self._handle_approval_callback(query, approval_id, True)
        elif data.startswith("deny_"):
            approval_id = data.replace("deny_", "")
            await self._handle_approval_callback(query, approval_id, False)
        elif data == "history":
            await self._handle_history_callback(query)
        elif data == "help":
            await self._handle_help_callback(query)

    async def _handle_status_callback(self, query, execution_id: str) -> None:
        """Handle status button callback"""
        if execution_id not in self.active_executions:
            await query.edit_message_text(
                f"❌ Execution `{execution_id}` not found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        execution_info = self.active_executions[execution_id]
        status_message = self._format_detailed_status(execution_id, execution_info)

        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data=f"status_{execution_id}")],
            [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{execution_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            status_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def _handle_cancel_callback(self, query, execution_id: str) -> None:
        """Handle cancel button callback"""
        if execution_id not in self.active_executions:
            await query.edit_message_text(
                f"❌ Execution `{execution_id}` not found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        execution_info = self.active_executions[execution_id]
        execution_info["status"] = "cancelled"
        execution_info["end_time"] = datetime.now()

        await query.edit_message_text(
            f"❌ **Execution Cancelled**\n\n"
            f"**Execution ID:** `{execution_id}`\n"
            f"**Goal:** {execution_info['goal']}\n\n"
            f"The execution has been cancelled.",
            parse_mode=ParseMode.MARKDOWN
        )

    # Helper methods for formatting and utilities

    def _format_results_summary(self, results: Dict[str, Any]) -> str:
        """Format results summary for display"""
        if not results:
            return "No results data available"

        summary = ""
        if "status" in results:
            summary += f"• **Overall Status:** {results['status']}\n"

        if "workflow_result" in results:
            workflow = results["workflow_result"]
            if "deliverables" in workflow:
                summary += f"• **Deliverables:** {len(workflow['deliverables'])} items\n"
            if "quality_score" in workflow:
                summary += f"• **Quality Score:** {workflow['quality_score']}/100\n"

        return summary if summary else "Execution completed successfully"

    def _format_detailed_status(self, execution_id: str, execution_info: Dict[str, Any]) -> str:
        """Format detailed status information"""
        duration = datetime.now() - execution_info["start_time"]
        status_icon = self._get_status_icon(execution_info["status"])

        status_msg = f"📊 **Detailed Status**\n\n"
        status_msg += f"**Execution ID:** `{execution_id}`\n"
        status_msg += f"**Goal:** {execution_info['goal']}\n"
        status_msg += f"**Status:** {status_icon} {execution_info['status'].title()}\n"
        status_msg += f"**Duration:** {self._format_duration(duration)}\n\n"

        # Add progress info if available
        progress = execution_info.get("progress", {})
        if progress:
            status_msg += "**Progress:**\n"
            for key, value in progress.items():
                status_msg += f"• {key.title()}: {value}\n"

        return status_msg

    def _get_status_icon(self, status: str) -> str:
        """Get emoji icon for status"""
        icons = {
            "starting": "🚀",
            "analyzing": "🔍",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫"
        }
        return icons.get(status, "❓")

    def _format_duration(self, duration: timedelta) -> str:
        """Format duration for display"""
        total_seconds = int(duration.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    async def run(self) -> None:
        """Run the Telegram bot"""
        # Create application
        self.application = Application.builder().token(self.bot_token).build()

        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("execute", self.execute_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))

        # Add message handler for approval responses
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

        logger.info("🤖 Devlar AI Workforce Telegram bot starting...")

        # Start bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

        logger.info("✅ Telegram bot is running!")

        # Keep running
        await self.application.updater.idle()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages for approvals and general interaction"""
        if not self._is_authorized(update.effective_user.id):
            return

        text = update.message.text.lower().strip()

        # Check for approval responses
        if text in ["approve", "✅", "yes", "y"]:
            await self._handle_approval_response(update, True)
        elif text in ["deny", "❌", "no", "n"]:
            await self._handle_approval_response(update, False)
        else:
            # General help response
            await update.message.reply_text(
                "💡 **Quick Commands:**\n\n"
                "• `/execute <goal>` - Start new execution\n"
                "• `/status` - Check active executions\n"
                "• `/help` - Show detailed help\n\n"
                "Or use the inline buttons for quick actions!",
                parse_mode=ParseMode.MARKDOWN
            )

    async def _handle_approval_response(self, update: Update, approved: bool) -> None:
        """Handle approval response from text message"""
        user_id = update.effective_user.id

        # Find pending approval for this user
        user_approvals = [
            approval_id for approval_id, approval in self.pending_approvals.items()
            if approval.get("user_id") == user_id
        ]

        if not user_approvals:
            await update.message.reply_text(
                "❓ No pending approvals found.\n\n"
                "Use `/status` to see active executions.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Use the most recent approval
        approval_id = user_approvals[-1]

        response = "✅ Approved" if approved else "❌ Denied"
        await update.message.reply_text(
            f"{response} operation `{approval_id}`.\n\n"
            "The workforce will continue accordingly.",
            parse_mode=ParseMode.MARKDOWN
        )


if __name__ == "__main__":
    """Run the Telegram bot interface"""
    import sys

    # Setup logging
    setup_logging()

    # Check required environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)

    # Run bot
    bot = TelegramInterface()
    asyncio.run(bot.run())