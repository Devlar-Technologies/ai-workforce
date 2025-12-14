"""
Devlar AI Workforce - Metrics Collection
Prometheus metrics for monitoring workforce performance and health
"""

import time
import os
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from loguru import logger


class WorkforceMetrics:
    """
    Prometheus metrics collection for Devlar AI Workforce
    Tracks executions, performance, costs, and system health
    """

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """Initialize metrics collection"""
        self.registry = registry
        self.enabled = PROMETHEUS_AVAILABLE and os.getenv("ENABLE_METRICS", "true").lower() == "true"

        if not self.enabled:
            logger.warning("Metrics collection disabled or Prometheus client not available")
            return

        # Execution metrics
        self.executions_total = Counter(
            'workforce_executions_total',
            'Total number of goal executions',
            ['status', 'pod_name'],
            registry=self.registry
        )

        self.executions_successful = Counter(
            'workforce_executions_successful_total',
            'Total successful executions',
            ['pod_name'],
            registry=self.registry
        )

        self.executions_failed = Counter(
            'workforce_executions_failed_total',
            'Total failed executions',
            ['pod_name', 'error_type'],
            registry=self.registry
        )

        # Performance metrics
        self.execution_duration = Histogram(
            'workforce_execution_duration_seconds',
            'Goal execution duration',
            ['pod_name', 'goal_type'],
            buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1200],
            registry=self.registry
        )

        self.queue_size = Gauge(
            'workforce_pod_queue_size',
            'Number of tasks in pod queue',
            ['pod_name'],
            registry=self.registry
        )

        self.active_executions = Gauge(
            'workforce_active_executions',
            'Number of currently active executions',
            registry=self.registry
        )

        # Cost metrics
        self.daily_cost = Gauge(
            'workforce_daily_cost_eur',
            'Daily cost in EUR',
            registry=self.registry
        )

        self.api_requests = Counter(
            'workforce_api_requests_total',
            'Total API requests to external services',
            ['service', 'status'],
            registry=self.registry
        )

        self.api_latency = Histogram(
            'workforce_external_api_latency_seconds',
            'External API response time',
            ['service'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30],
            registry=self.registry
        )

        # System health
        self.memory_usage = Gauge(
            'workforce_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )

        self.external_api_health = Gauge(
            'workforce_external_api_health',
            'External API health status (1=healthy, 0=down)',
            ['service'],
            registry=self.registry
        )

        # Pod-specific metrics
        self.pod_executions = Counter(
            'workforce_pod_executions_total',
            'Total pod executions',
            ['pod_name', 'agent_name'],
            registry=self.registry
        )

        self.pod_execution_duration = Histogram(
            'workforce_pod_execution_duration_seconds',
            'Pod execution duration',
            ['pod_name', 'agent_name'],
            buckets=[1, 5, 10, 30, 60, 120, 300],
            registry=self.registry
        )

        # User interaction metrics
        self.telegram_messages = Counter(
            'telegram_bot_messages_total',
            'Total Telegram bot messages',
            ['message_type', 'status'],
            registry=self.registry
        )

        self.telegram_errors = Counter(
            'telegram_bot_errors_total',
            'Telegram bot errors',
            ['error_type'],
            registry=self.registry
        )

        logger.info("📊 Workforce metrics collection initialized")

    def record_execution_start(self, pod_name: str, goal_type: str = "general") -> float:
        """Record execution start"""
        if not self.enabled:
            return time.time()

        self.active_executions.inc()
        return time.time()

    def record_execution_complete(self, pod_name: str, goal_type: str, start_time: float, success: bool = True):
        """Record execution completion"""
        if not self.enabled:
            return

        duration = time.time() - start_time
        status = "success" if success else "failed"

        self.executions_total.labels(status=status, pod_name=pod_name).inc()
        self.execution_duration.labels(pod_name=pod_name, goal_type=goal_type).observe(duration)
        self.active_executions.dec()

        if success:
            self.executions_successful.labels(pod_name=pod_name).inc()
        else:
            self.executions_failed.labels(pod_name=pod_name, error_type="unknown").inc()

    def record_execution_error(self, pod_name: str, error_type: str):
        """Record execution error"""
        if not self.enabled:
            return

        self.executions_failed.labels(pod_name=pod_name, error_type=error_type).inc()
        self.active_executions.dec()

    def record_api_request(self, service: str, status: str, duration: float):
        """Record external API request"""
        if not self.enabled:
            return

        self.api_requests.labels(service=service, status=status).inc()
        self.api_latency.labels(service=service).observe(duration)

    def update_api_health(self, service: str, healthy: bool):
        """Update external API health status"""
        if not self.enabled:
            return

        self.external_api_health.labels(service=service).set(1 if healthy else 0)

    def update_daily_cost(self, cost_usd: float):
        """Update daily cost tracking"""
        if not self.enabled:
            return

        self.daily_cost.set(cost_usd)

    def update_queue_size(self, pod_name: str, size: int):
        """Update pod queue size"""
        if not self.enabled:
            return

        self.queue_size.labels(pod_name=pod_name).set(size)

    def update_memory_usage(self, bytes_used: int):
        """Update memory usage"""
        if not self.enabled:
            return

        self.memory_usage.set(bytes_used)

    def record_telegram_message(self, message_type: str, status: str):
        """Record Telegram bot message"""
        if not self.enabled:
            return

        self.telegram_messages.labels(message_type=message_type, status=status).inc()

    def record_telegram_error(self, error_type: str):
        """Record Telegram bot error"""
        if not self.enabled:
            return

        self.telegram_errors.labels(error_type=error_type).inc()

    def record_pod_execution(self, pod_name: str, agent_name: str, duration: float):
        """Record pod-specific execution"""
        if not self.enabled:
            return

        self.pod_executions.labels(pod_name=pod_name, agent_name=agent_name).inc()
        self.pod_execution_duration.labels(pod_name=pod_name, agent_name=agent_name).observe(duration)


# Global metrics instance
_metrics_instance = None


def get_metrics() -> WorkforceMetrics:
    """Get global metrics instance"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = WorkforceMetrics()
    return _metrics_instance


def timing_metric(pod_name: str, goal_type: str = "general"):
    """Decorator to automatically track execution timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = metrics.record_execution_start(pod_name, goal_type)

            try:
                result = func(*args, **kwargs)
                success = result.get('success', True) if isinstance(result, dict) else True
                metrics.record_execution_complete(pod_name, goal_type, start_time, success)
                return result
            except Exception as e:
                metrics.record_execution_error(pod_name, type(e).__name__)
                raise

        return wrapper
    return decorator


def api_request_metric(service: str):
    """Decorator to track external API requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                status = "success" if result.get('success', True) else "error"
                metrics.record_api_request(service, status, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_api_request(service, "error", duration)
                raise

        return wrapper
    return decorator


def start_metrics_server(port: int = 8000):
    """Start Prometheus metrics HTTP server"""
    if not PROMETHEUS_AVAILABLE:
        logger.warning("Prometheus client not available - metrics server not started")
        return

    try:
        start_http_server(port)
        logger.info(f"📊 Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")


def export_metrics_to_file(filepath: str):
    """Export current metrics to file (for debugging)"""
    if not PROMETHEUS_AVAILABLE:
        return

    try:
        from prometheus_client import generate_latest
        metrics_output = generate_latest().decode('utf-8')

        with open(filepath, 'w') as f:
            f.write(f"# Devlar AI Workforce Metrics Export\n")
            f.write(f"# Generated at: {datetime.now().isoformat()}\n")
            f.write(f"# \n")
            f.write(metrics_output)

        logger.info(f"📊 Metrics exported to {filepath}")
    except Exception as e:
        logger.error(f"Failed to export metrics: {e}")


# Health check metrics for monitoring endpoints
def record_health_check(endpoint: str, healthy: bool, response_time: float):
    """Record health check results"""
    metrics = get_metrics()
    if not metrics.enabled:
        return

    try:
        # Use existing API metrics for health checks
        status = "success" if healthy else "error"
        metrics.record_api_request(f"health_{endpoint}", status, response_time)
    except Exception as e:
        logger.error(f"Failed to record health check metric: {e}")


# Cost tracking helpers
class CostTracker:
    """Helper class for tracking daily costs"""

    def __init__(self):
        self.daily_costs = {}
        self.metrics = get_metrics()

    def add_cost(self, service: str, amount: float):
        """Add cost for a service"""
        today = datetime.now().strftime('%Y-%m-%d')

        if today not in self.daily_costs:
            self.daily_costs[today] = {}

        if service not in self.daily_costs[today]:
            self.daily_costs[today][service] = 0

        self.daily_costs[today][service] += amount

        # Update total daily cost
        total_today = sum(self.daily_costs[today].values())
        self.metrics.update_daily_cost(total_today)

        logger.debug(f"💰 Added ${amount:.4f} cost for {service}, daily total: ${total_today:.2f}")

    def get_daily_total(self, date: str = None) -> float:
        """Get total cost for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        return sum(self.daily_costs.get(date, {}).values())

    def get_service_cost(self, service: str, date: str = None) -> float:
        """Get cost for specific service on date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        return self.daily_costs.get(date, {}).get(service, 0.0)


# Global cost tracker
_cost_tracker = None


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance"""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker