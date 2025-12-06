"""
Test suite for metrics.py module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import time
from datetime import datetime

# Mock Prometheus client
with patch.dict('sys.modules', {
    'prometheus_client': MagicMock(),
    'loguru': MagicMock()
}):
    from utils.metrics import (
        WorkforceMetrics,
        get_metrics,
        timing_metric,
        api_request_metric,
        start_metrics_server,
        export_metrics_to_file,
        record_health_check,
        CostTracker,
        get_cost_tracker
    )


class TestWorkforceMetrics(unittest.TestCase):
    """Test cases for WorkforceMetrics class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('utils.metrics.os.getenv')
    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    def test_metrics_initialization_enabled(self, mock_getenv):
        """Test metrics initialization when enabled"""
        mock_getenv.return_value = 'true'

        with patch('utils.metrics.Counter'), \
             patch('utils.metrics.Histogram'), \
             patch('utils.metrics.Gauge'):
            metrics = WorkforceMetrics()
            self.assertTrue(metrics.enabled)

    @patch('utils.metrics.os.getenv')
    @patch('utils.metrics.PROMETHEUS_AVAILABLE', False)
    def test_metrics_initialization_disabled(self, mock_getenv):
        """Test metrics initialization when disabled"""
        mock_getenv.return_value = 'false'

        metrics = WorkforceMetrics()
        self.assertFalse(metrics.enabled)

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    @patch('utils.metrics.os.getenv')
    def test_record_execution_start(self, mock_getenv):
        """Test recording execution start"""
        mock_getenv.return_value = 'true'

        with patch('utils.metrics.Counter'), \
             patch('utils.metrics.Histogram'), \
             patch('utils.metrics.Gauge') as mock_gauge:

            mock_active_executions = Mock()
            mock_gauge.return_value = mock_active_executions

            metrics = WorkforceMetrics()
            metrics.active_executions = mock_active_executions

            start_time = metrics.record_execution_start('test_pod', 'test_goal')

            self.assertIsInstance(start_time, float)
            mock_active_executions.inc.assert_called_once()

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    @patch('utils.metrics.os.getenv')
    def test_record_execution_complete(self, mock_getenv):
        """Test recording execution completion"""
        mock_getenv.return_value = 'true'

        with patch('utils.metrics.Counter') as mock_counter, \
             patch('utils.metrics.Histogram') as mock_histogram, \
             patch('utils.metrics.Gauge') as mock_gauge:

            mock_executions_total = Mock()
            mock_executions_successful = Mock()
            mock_execution_duration = Mock()
            mock_active_executions = Mock()

            metrics = WorkforceMetrics()
            metrics.executions_total = mock_executions_total
            metrics.executions_successful = mock_executions_successful
            metrics.execution_duration = mock_execution_duration
            metrics.active_executions = mock_active_executions

            start_time = time.time() - 5  # 5 seconds ago

            metrics.record_execution_complete('test_pod', 'test_goal', start_time, True)

            mock_executions_total.labels.assert_called()
            mock_executions_successful.labels.assert_called()
            mock_execution_duration.labels.assert_called()
            mock_active_executions.dec.assert_called_once()

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    @patch('utils.metrics.os.getenv')
    def test_record_execution_error(self, mock_getenv):
        """Test recording execution error"""
        mock_getenv.return_value = 'true'

        with patch('utils.metrics.Counter'), \
             patch('utils.metrics.Histogram'), \
             patch('utils.metrics.Gauge'):

            mock_executions_failed = Mock()
            mock_active_executions = Mock()

            metrics = WorkforceMetrics()
            metrics.executions_failed = mock_executions_failed
            metrics.active_executions = mock_active_executions

            metrics.record_execution_error('test_pod', 'timeout')

            mock_executions_failed.labels.assert_called_with(pod_name='test_pod', error_type='timeout')
            mock_active_executions.dec.assert_called_once()

    def test_disabled_metrics_no_op(self):
        """Test that disabled metrics are no-op"""
        with patch('utils.metrics.PROMETHEUS_AVAILABLE', False):
            metrics = WorkforceMetrics()

            # All methods should return quickly without errors
            start_time = metrics.record_execution_start('test_pod')
            self.assertIsInstance(start_time, float)

            metrics.record_execution_complete('test_pod', 'goal', start_time)
            metrics.record_execution_error('test_pod', 'error')
            metrics.record_api_request('service', 'success', 1.0)
            metrics.update_daily_cost(10.0)

            # Should not raise any exceptions


class TestMetricsDecorators(unittest.TestCase):
    """Test cases for metrics decorators"""

    @patch('utils.metrics.get_metrics')
    def test_timing_metric_decorator_success(self, mock_get_metrics):
        """Test timing metric decorator with successful function"""
        mock_metrics = Mock()
        mock_metrics.record_execution_start.return_value = time.time()
        mock_get_metrics.return_value = mock_metrics

        @timing_metric('test_pod', 'test_goal')
        def test_function():
            return {'success': True, 'result': 'test'}

        result = test_function()

        self.assertEqual(result, {'success': True, 'result': 'test'})
        mock_metrics.record_execution_start.assert_called_once_with('test_pod', 'test_goal')
        mock_metrics.record_execution_complete.assert_called_once()

    @patch('utils.metrics.get_metrics')
    def test_timing_metric_decorator_exception(self, mock_get_metrics):
        """Test timing metric decorator with exception"""
        mock_metrics = Mock()
        mock_metrics.record_execution_start.return_value = time.time()
        mock_get_metrics.return_value = mock_metrics

        @timing_metric('test_pod', 'test_goal')
        def test_function():
            raise ValueError('Test error')

        with self.assertRaises(ValueError):
            test_function()

        mock_metrics.record_execution_start.assert_called_once()
        mock_metrics.record_execution_error.assert_called_once_with('test_pod', 'ValueError')

    @patch('utils.metrics.get_metrics')
    def test_api_request_metric_decorator(self, mock_get_metrics):
        """Test API request metric decorator"""
        mock_metrics = Mock()
        mock_get_metrics.return_value = mock_metrics

        @api_request_metric('test_service')
        def api_function():
            return {'success': True, 'data': 'test'}

        result = api_function()

        self.assertEqual(result, {'success': True, 'data': 'test'})
        mock_metrics.record_api_request.assert_called_once()


class TestCostTracker(unittest.TestCase):
    """Test cases for CostTracker class"""

    def setUp(self):
        """Set up test fixtures"""
        with patch('utils.metrics.get_metrics'):
            self.cost_tracker = CostTracker()

    def test_add_cost(self):
        """Test adding cost for a service"""
        with patch('utils.metrics.get_metrics'):
            self.cost_tracker.add_cost('openai', 5.50)
            self.cost_tracker.add_cost('openai', 2.25)

            total = self.cost_tracker.get_service_cost('openai')
            self.assertEqual(total, 7.75)

    def test_get_daily_total(self):
        """Test getting daily total cost"""
        with patch('utils.metrics.get_metrics'):
            self.cost_tracker.add_cost('openai', 10.0)
            self.cost_tracker.add_cost('anthropic', 15.0)

            total = self.cost_tracker.get_daily_total()
            self.assertEqual(total, 25.0)

    def test_get_service_cost_nonexistent(self):
        """Test getting cost for non-existent service"""
        cost = self.cost_tracker.get_service_cost('nonexistent')
        self.assertEqual(cost, 0.0)

    def test_get_daily_total_specific_date(self):
        """Test getting daily total for specific date"""
        # Should return 0 for dates with no data
        cost = self.cost_tracker.get_daily_total('2023-01-01')
        self.assertEqual(cost, 0.0)


class TestMetricsUtilities(unittest.TestCase):
    """Test cases for metrics utility functions"""

    @patch('utils.metrics.get_metrics')
    def test_record_health_check(self, mock_get_metrics):
        """Test health check recording"""
        mock_metrics = Mock()
        mock_metrics.enabled = True
        mock_get_metrics.return_value = mock_metrics

        record_health_check('api_endpoint', True, 0.5)

        mock_metrics.record_api_request.assert_called_once_with('health_api_endpoint', 'success', 0.5)

    @patch('utils.metrics.get_metrics')
    def test_record_health_check_disabled(self, mock_get_metrics):
        """Test health check recording when disabled"""
        mock_metrics = Mock()
        mock_metrics.enabled = False
        mock_get_metrics.return_value = mock_metrics

        # Should not raise exception
        record_health_check('api_endpoint', False, 1.0)

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    @patch('utils.metrics.start_http_server')
    def test_start_metrics_server(self, mock_start_server):
        """Test starting metrics server"""
        start_metrics_server(8080)
        mock_start_server.assert_called_once_with(8080)

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', False)
    def test_start_metrics_server_unavailable(self):
        """Test starting metrics server when Prometheus unavailable"""
        # Should not raise exception
        start_metrics_server(8080)

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    @patch('utils.metrics.generate_latest')
    def test_export_metrics_to_file(self, mock_generate_latest):
        """Test exporting metrics to file"""
        mock_generate_latest.return_value = b'# Metrics data\nmetric_name 1.0\n'

        temp_file = os.path.join(tempfile.mkdtemp(), 'metrics.txt')

        export_metrics_to_file(temp_file)

        self.assertTrue(os.path.exists(temp_file))

        with open(temp_file, 'r') as f:
            content = f.read()
            self.assertIn('Devlar AI Workforce Metrics Export', content)
            self.assertIn('metric_name 1.0', content)

        os.remove(temp_file)


class TestMetricsSingleton(unittest.TestCase):
    """Test cases for metrics singleton pattern"""

    def test_get_metrics_singleton(self):
        """Test that get_metrics returns same instance"""
        metrics1 = get_metrics()
        metrics2 = get_metrics()

        self.assertIs(metrics1, metrics2)

    def test_get_cost_tracker_singleton(self):
        """Test that get_cost_tracker returns same instance"""
        tracker1 = get_cost_tracker()
        tracker2 = get_cost_tracker()

        self.assertIs(tracker1, tracker2)


class TestMetricsIntegration(unittest.TestCase):
    """Integration tests for metrics system"""

    @patch('utils.metrics.PROMETHEUS_AVAILABLE', True)
    @patch('utils.metrics.os.getenv')
    def test_end_to_end_metrics_flow(self, mock_getenv):
        """Test complete metrics collection flow"""
        mock_getenv.return_value = 'true'

        with patch('utils.metrics.Counter'), \
             patch('utils.metrics.Histogram'), \
             patch('utils.metrics.Gauge'):

            # Initialize metrics
            metrics = WorkforceMetrics()

            # Record complete execution flow
            start_time = metrics.record_execution_start('test_pod', 'test_goal')
            time.sleep(0.01)  # Small delay
            metrics.record_execution_complete('test_pod', 'test_goal', start_time, True)

            # Record API request
            metrics.record_api_request('openai', 'success', 1.5)

            # Update costs
            metrics.update_daily_cost(25.0)

            # Record telegram activity
            metrics.record_telegram_message('command', 'success')

            # Should complete without errors

    def test_metrics_with_real_decorators(self):
        """Test decorators with actual function execution"""
        @timing_metric('test_pod', 'integration_test')
        def test_task():
            time.sleep(0.01)
            return {'success': True, 'message': 'completed'}

        @api_request_metric('test_api')
        def test_api_call():
            return {'success': True, 'response': 'data'}

        # Should execute without errors
        result1 = test_task()
        result2 = test_api_call()

        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])


if __name__ == '__main__':
    unittest.main()