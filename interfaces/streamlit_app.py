"""
Devlar AI Workforce - Streamlit Dashboard
Fallback web interface for workforce management and monitoring
"""

import streamlit as st
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from main import DevlarWorkforceCEO
from memory import WorkforceMemory
from utils import setup_logging

# Configure page
st.set_page_config(
    page_title="Devlar AI Workforce",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logger = logging.getLogger(__name__)

class StreamlitInterface:
    """
    Streamlit web interface for Devlar AI Workforce
    Provides comprehensive dashboard for task execution and monitoring
    """

    def __init__(self):
        """Initialize Streamlit interface"""
        if 'ceo' not in st.session_state:
            st.session_state.ceo = DevlarWorkforceCEO()
        if 'memory' not in st.session_state:
            st.session_state.memory = WorkforceMemory()
        if 'active_executions' not in st.session_state:
            st.session_state.active_executions = {}
        if 'execution_history' not in st.session_state:
            st.session_state.execution_history = []

    def render_header(self):
        """Render application header"""
        st.title("🤖 Devlar AI Workforce")
        st.markdown("*CEO Orchestrator Dashboard - Scale your business with AI*")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            active_count = len([e for e in st.session_state.active_executions.values()
                               if e.get('status') not in ['completed', 'failed', 'cancelled']])
            st.metric("Active Executions", active_count)

        with col2:
            completed_today = len([e for e in st.session_state.execution_history
                                 if e.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
            st.metric("Completed Today", completed_today)

        with col3:
            success_rate = self._calculate_success_rate()
            st.metric("Success Rate", f"{success_rate:.1f}%")

        with col4:
            cost_today = self._calculate_daily_cost()
            st.metric("Cost Today", f"${cost_today:.2f}")

        st.divider()

    def render_sidebar(self):
        """Render sidebar navigation"""
        st.sidebar.title("🎯 Navigation")

        page = st.sidebar.selectbox(
            "Select Page",
            ["🚀 Execute Goal", "📊 Dashboard", "📋 Executions", "📈 Analytics", "⚙️ Settings"],
            index=0
        )

        st.sidebar.divider()

        # Quick actions
        st.sidebar.subheader("⚡ Quick Actions")

        if st.sidebar.button("🔄 Refresh Data", type="secondary"):
            st.rerun()

        if st.sidebar.button("🧹 Clear History", type="secondary"):
            if st.sidebar.checkbox("Confirm clear history"):
                st.session_state.execution_history = []
                st.success("History cleared!")
                st.rerun()

        st.sidebar.divider()

        # System status
        st.sidebar.subheader("🏥 System Health")
        st.sidebar.success("✅ CEO Online")
        st.sidebar.info("📡 Memory Connected")
        st.sidebar.info("🛠️ All Tools Ready")

        return page

    def render_execute_page(self):
        """Render goal execution page"""
        st.header("🚀 Execute Business Goal")

        # Goal input section
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                goal = st.text_area(
                    "What would you like to accomplish?",
                    placeholder="Examples:\n• Get 100 new Chromentum beta users\n• Research top 10 AI meditation apps\n• Implement dark mode for TimePost",
                    height=120
                )

            with col2:
                st.markdown("**💡 Goal Examples:**")

                example_goals = [
                    "Research competitor pricing",
                    "Launch user acquisition campaign",
                    "Implement new feature",
                    "Optimize conversion rates",
                    "Analyze user behavior",
                    "Create content strategy"
                ]

                for example in example_goals:
                    if st.button(f"📝 {example}", key=f"example_{example}", type="secondary"):
                        st.session_state.goal_input = example

        # Execution options
        with st.expander("🔧 Execution Options", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
                budget_limit = st.number_input("Budget Limit (€)", min_value=0.0, value=100.0, step=10.0)

            with col2:
                notification_level = st.selectbox("Notifications", ["All", "Important Only", "None"], index=1)
                auto_approve = st.checkbox("Auto-approve operations under €50", value=True)

        # Execute button
        if st.button("🚀 Execute Goal", type="primary", disabled=not goal):
            if goal:
                execution_id = self._start_execution(goal, {
                    "priority": priority,
                    "budget_limit": budget_limit,
                    "notification_level": notification_level,
                    "auto_approve": auto_approve
                })

                st.success(f"✅ Execution started! ID: `{execution_id}`")
                st.info("🔄 Check the Executions page for real-time progress.")

                # Auto-redirect to executions page
                st.session_state.redirect_to_executions = True

    def render_dashboard_page(self):
        """Render main dashboard page"""
        st.header("📊 Workforce Dashboard")

        # Recent activity
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🕐 Recent Activity")

            if st.session_state.execution_history:
                df_history = pd.DataFrame(st.session_state.execution_history[-10:])

                # Create timeline chart
                fig = px.timeline(
                    df_history,
                    x_start="start_time",
                    x_end="end_time",
                    y="goal",
                    color="status",
                    title="Execution Timeline"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent executions. Start your first goal execution!")

        with col2:
            st.subheader("📈 Performance Metrics")

            # Success rate chart
            if st.session_state.execution_history:
                success_data = self._get_success_rate_data()
                fig = px.pie(
                    values=success_data["values"],
                    names=success_data["labels"],
                    title="Success Rate"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Active executions
        st.subheader("🔄 Active Executions")
        active_executions = [
            e for e in st.session_state.active_executions.values()
            if e.get('status') not in ['completed', 'failed', 'cancelled']
        ]

        if active_executions:
            for exec_info in active_executions:
                self._render_execution_card(exec_info)
        else:
            st.info("No active executions. Ready for new goals!")

    def render_executions_page(self):
        """Render executions management page"""
        st.header("📋 Execution Management")

        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                ["active", "completed", "failed", "cancelled"],
                default=["active", "completed"]
            )

        with col2:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=7), datetime.now()),
                max_value=datetime.now()
            )

        with col3:
            search_term = st.text_input("Search Goals", placeholder="Enter keywords...")

        # Executions list
        all_executions = list(st.session_state.active_executions.values()) + st.session_state.execution_history

        # Apply filters
        filtered_executions = self._filter_executions(
            all_executions, status_filter, date_range, search_term
        )

        if filtered_executions:
            for exec_info in filtered_executions:
                self._render_detailed_execution_card(exec_info)
        else:
            st.info("No executions match the current filters.")

    def render_analytics_page(self):
        """Render analytics and insights page"""
        st.header("📈 Workforce Analytics")

        if not st.session_state.execution_history:
            st.info("📊 Analytics will appear after you have execution history.")
            return

        # Performance metrics
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Execution Performance")

            # Execution time analysis
            df_performance = self._get_performance_data()
            fig = px.box(
                df_performance,
                x="category",
                y="duration_minutes",
                title="Execution Duration by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("💰 Cost Analysis")

            # Cost trends
            df_costs = self._get_cost_data()
            fig = px.line(
                df_costs,
                x="date",
                y="cumulative_cost",
                title="Cumulative Cost Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Pod activity analysis
        st.subheader("🏭 Pod Activity Analysis")

        pod_stats = self._get_pod_statistics()

        col1, col2 = st.columns(2)

        with col1:
            # Pod utilization
            fig = px.bar(
                x=pod_stats["pod_names"],
                y=pod_stats["utilization"],
                title="Pod Utilization Rate"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Pod success rates
            fig = px.bar(
                x=pod_stats["pod_names"],
                y=pod_stats["success_rates"],
                title="Pod Success Rates"
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_settings_page(self):
        """Render settings and configuration page"""
        st.header("⚙️ Workforce Settings")

        # General settings
        st.subheader("🔧 General Configuration")

        col1, col2 = st.columns(2)

        with col1:
            default_budget = st.number_input(
                "Default Budget Limit ($)",
                min_value=0.0,
                value=100.0,
                step=10.0,
                help="Default budget for new executions"
            )

            auto_approval_threshold = st.number_input(
                "Auto-approval Threshold ($)",
                min_value=0.0,
                value=50.0,
                step=5.0,
                help="Operations below this amount are auto-approved"
            )

        with col2:
            notification_email = st.text_input(
                "Notification Email",
                placeholder="you@devlar.io",
                help="Email for important notifications"
            )

            max_concurrent = st.number_input(
                "Max Concurrent Executions",
                min_value=1,
                max_value=10,
                value=3,
                help="Maximum parallel executions"
            )

        # API configurations
        st.subheader("🔌 API Configurations")

        with st.expander("Environment Variables", expanded=False):
            st.code("""
# Required Environment Variables:
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_env_here
FIRECRAWL_API_KEY=your_key_here
APOLLO_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
TELEGRAM_BOT_TOKEN=your_token_here
            """)

        # Save settings
        if st.button("💾 Save Settings", type="primary"):
            st.session_state.settings = {
                "default_budget": default_budget,
                "auto_approval_threshold": auto_approval_threshold,
                "notification_email": notification_email,
                "max_concurrent": max_concurrent
            }
            st.success("✅ Settings saved!")

    def _start_execution(self, goal: str, options: Dict[str, Any]) -> str:
        """Start new goal execution"""
        execution_id = str(uuid.uuid4())[:8]

        execution_info = {
            "id": execution_id,
            "goal": goal,
            "status": "starting",
            "start_time": datetime.now(),
            "options": options,
            "progress": {}
        }

        st.session_state.active_executions[execution_id] = execution_info

        # Start execution asynchronously (simulated for demo)
        # In real implementation, this would trigger the CEO
        self._simulate_execution_progress(execution_id)

        return execution_id

    def _simulate_execution_progress(self, execution_id: str):
        """Simulate execution progress (replace with real CEO execution)"""
        # This is a placeholder - in real implementation,
        # this would call st.session_state.ceo.execute_goal(goal)
        pass

    def _render_execution_card(self, exec_info: Dict[str, Any]):
        """Render execution status card"""
        status_color = {
            "starting": "🚀",
            "active": "🔄",
            "completed": "✅",
            "failed": "❌",
            "cancelled": "🚫"
        }

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{status_color.get(exec_info.get('status'), '❓')} {exec_info.get('goal', 'Unknown goal')}**")
                if 'start_time' in exec_info:
                    duration = datetime.now() - exec_info['start_time']
                    st.caption(f"Duration: {self._format_duration(duration)}")

            with col2:
                st.metric("Status", exec_info.get('status', 'unknown').title())

            with col3:
                if exec_info.get('status') in ['starting', 'active']:
                    if st.button("❌ Cancel", key=f"cancel_{exec_info.get('id')}"):
                        self._cancel_execution(exec_info.get('id'))

        st.divider()

    def _render_detailed_execution_card(self, exec_info: Dict[str, Any]):
        """Render detailed execution card with more information"""
        with st.expander(f"{exec_info.get('goal', 'Unknown goal')}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**ID:** `{exec_info.get('id', 'unknown')}`")
                st.write(f"**Status:** {exec_info.get('status', 'unknown').title()}")

                if 'start_time' in exec_info:
                    st.write(f"**Started:** {exec_info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

                if 'end_time' in exec_info:
                    st.write(f"**Ended:** {exec_info['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")

            with col2:
                if 'options' in exec_info:
                    st.write("**Options:**")
                    for key, value in exec_info['options'].items():
                        st.write(f"- {key}: {value}")

                if 'results' in exec_info:
                    st.write("**Results Available:** ✅")
                    if st.button("📋 View Results", key=f"results_{exec_info.get('id')}"):
                        st.json(exec_info['results'])

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        if not st.session_state.execution_history:
            return 100.0

        total = len(st.session_state.execution_history)
        successful = len([e for e in st.session_state.execution_history if e.get('status') == 'completed'])

        return (successful / total) * 100 if total > 0 else 100.0

    def _calculate_daily_cost(self) -> float:
        """Calculate today's estimated cost"""
        today = datetime.now().strftime('%Y-%m-%d')

        daily_executions = [
            e for e in st.session_state.execution_history
            if e.get('timestamp', '').startswith(today)
        ]

        # Estimated cost per execution (placeholder)
        return len(daily_executions) * 5.0

    def _get_success_rate_data(self) -> Dict[str, List]:
        """Get data for success rate chart"""
        if not st.session_state.execution_history:
            return {"labels": ["No Data"], "values": [1]}

        statuses = [e.get('status', 'unknown') for e in st.session_state.execution_history]
        status_counts = {}

        for status in statuses:
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "labels": list(status_counts.keys()),
            "values": list(status_counts.values())
        }

    def _filter_executions(self, executions: List[Dict[str, Any]], status_filter: List[str],
                          date_range: tuple, search_term: str) -> List[Dict[str, Any]]:
        """Filter executions based on criteria"""
        filtered = []

        for exec_info in executions:
            # Status filter
            if exec_info.get('status') not in status_filter:
                continue

            # Date filter
            if 'start_time' in exec_info:
                exec_date = exec_info['start_time'].date()
                if exec_date < date_range[0] or exec_date > date_range[1]:
                    continue

            # Search filter
            if search_term and search_term.lower() not in exec_info.get('goal', '').lower():
                continue

            filtered.append(exec_info)

        return filtered

    def _get_performance_data(self) -> pd.DataFrame:
        """Get performance data for analytics"""
        data = []

        for exec_info in st.session_state.execution_history:
            if 'start_time' in exec_info and 'end_time' in exec_info:
                duration = exec_info['end_time'] - exec_info['start_time']
                duration_minutes = duration.total_seconds() / 60

                # Categorize by goal type (simple heuristic)
                goal = exec_info.get('goal', '').lower()
                if 'research' in goal:
                    category = 'Research'
                elif 'implement' in goal or 'develop' in goal:
                    category = 'Development'
                elif 'marketing' in goal or 'campaign' in goal:
                    category = 'Marketing'
                else:
                    category = 'Other'

                data.append({
                    "category": category,
                    "duration_minutes": duration_minutes,
                    "status": exec_info.get('status', 'unknown')
                })

        return pd.DataFrame(data)

    def _get_cost_data(self) -> pd.DataFrame:
        """Get cost data for analytics"""
        data = []
        cumulative_cost = 0

        for exec_info in sorted(st.session_state.execution_history,
                               key=lambda x: x.get('start_time', datetime.min)):
            if 'start_time' in exec_info:
                # Estimated cost per execution
                execution_cost = 5.0  # Placeholder
                cumulative_cost += execution_cost

                data.append({
                    "date": exec_info['start_time'].date(),
                    "cost": execution_cost,
                    "cumulative_cost": cumulative_cost
                })

        return pd.DataFrame(data)

    def _get_pod_statistics(self) -> Dict[str, List]:
        """Get pod utilization and success statistics"""
        # Placeholder data - in real implementation, this would come from memory
        return {
            "pod_names": ["Research", "Product Dev", "Marketing", "Sales", "Customer Success", "Analytics"],
            "utilization": [85, 92, 67, 78, 83, 71],
            "success_rates": [94, 89, 96, 87, 91, 93]
        }

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

    def _cancel_execution(self, execution_id: str):
        """Cancel an active execution"""
        if execution_id in st.session_state.active_executions:
            st.session_state.active_executions[execution_id]['status'] = 'cancelled'
            st.session_state.active_executions[execution_id]['end_time'] = datetime.now()
            st.success(f"✅ Execution {execution_id} cancelled")
            st.rerun()

    def run(self):
        """Main application runner"""
        self.render_header()
        page = self.render_sidebar()

        # Route to appropriate page
        if page == "🚀 Execute Goal":
            self.render_execute_page()
        elif page == "📊 Dashboard":
            self.render_dashboard_page()
        elif page == "📋 Executions":
            self.render_executions_page()
        elif page == "📈 Analytics":
            self.render_analytics_page()
        elif page == "⚙️ Settings":
            self.render_settings_page()

        # Handle redirects
        if st.session_state.get('redirect_to_executions'):
            st.session_state.redirect_to_executions = False
            st.switch_page("📋 Executions")


def main():
    """Main entry point"""
    # Setup logging
    setup_logging()

    # Initialize and run interface
    interface = StreamlitInterface()
    interface.run()


if __name__ == "__main__":
    main()