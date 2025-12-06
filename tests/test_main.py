"""
Test suite for main.py module (CEO orchestrator)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import tempfile
import os

# Mock all external dependencies
with patch.dict('sys.modules', {
    'crewai': MagicMock(),
    'modal': MagicMock(),
    'loguru': MagicMock(),
    'memory': MagicMock(),
    'telegram': MagicMock()
}):
    from main import WorkforceCEO, GoalExecution, execute_goal


class TestWorkforceCEO(unittest.TestCase):
    """Test cases for WorkforceCEO class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock memory
        self.mock_memory = Mock()
        self.mock_memory.search_experiences.return_value = []
        self.mock_memory.store_experience.return_value = True

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('main.WorkforceMemory')
    def test_ceo_initialization(self, mock_memory_class):
        """Test CEO initialization"""
        mock_memory_class.return_value = self.mock_memory

        ceo = WorkforceCEO()

        self.assertIsNotNone(ceo.memory)
        self.assertEqual(ceo.max_budget, 50.0)
        self.assertIsInstance(ceo.available_pods, dict)
        self.assertIn('research', ceo.available_pods)

    @patch('main.WorkforceMemory')
    def test_goal_decomposition(self, mock_memory_class):
        """Test goal decomposition logic"""
        mock_memory_class.return_value = self.mock_memory
        ceo = WorkforceCEO()

        test_goal = "Launch a new product for small businesses"

        # Test decomposition
        decomposition = ceo.decompose_goal(test_goal)

        self.assertIsInstance(decomposition, dict)
        self.assertIn('phases', decomposition)
        self.assertIn('estimated_cost', decomposition)
        self.assertIn('timeline', decomposition)

    @patch('main.WorkforceMemory')
    def test_pod_selection(self, mock_memory_class):
        """Test pod selection for different goal types"""
        mock_memory_class.return_value = self.mock_memory
        ceo = WorkforceCEO()

        test_cases = [
            ("research market trends", ["research"]),
            ("develop new features", ["product_development"]),
            ("create marketing campaign", ["marketing"]),
            ("increase sales", ["sales"]),
            ("improve customer satisfaction", ["customer_success"]),
            ("analyze performance data", ["analytics"])
        ]

        for goal, expected_pods in test_cases:
            with self.subTest(goal=goal):
                selected_pods = ceo.select_pods_for_goal(goal)
                self.assertIsInstance(selected_pods, list)
                # At least one expected pod should be selected
                self.assertTrue(any(pod in selected_pods for pod in expected_pods))

    @patch('main.WorkforceMemory')
    def test_cost_estimation(self, mock_memory_class):
        """Test cost estimation for different goals"""
        mock_memory_class.return_value = self.mock_memory
        ceo = WorkforceCEO()

        test_goal = "Simple research task"
        cost = ceo.estimate_goal_cost(test_goal, ["research"])

        self.assertIsInstance(cost, (int, float))
        self.assertGreater(cost, 0)
        self.assertLess(cost, 100)  # Reasonable upper bound

    @patch('main.WorkforceMemory')
    def test_budget_validation(self, mock_memory_class):
        """Test budget validation logic"""
        mock_memory_class.return_value = self.mock_memory
        ceo = WorkforceCEO()

        # Test valid budget
        self.assertTrue(ceo.validate_budget(10.0))

        # Test budget exceeding limit
        self.assertFalse(ceo.validate_budget(100.0))

        # Test negative budget
        self.assertFalse(ceo.validate_budget(-5.0))

    @patch('main.WorkforceMemory')
    def test_execution_planning(self, mock_memory_class):
        """Test execution plan generation"""
        mock_memory_class.return_value = self.mock_memory
        ceo = WorkforceCEO()

        test_goal = "Research competitor analysis"
        plan = ceo.create_execution_plan(test_goal, ["research"], 15.0)

        self.assertIsInstance(plan, dict)
        self.assertIn('goal', plan)
        self.assertIn('pods', plan)
        self.assertIn('estimated_cost', plan)
        self.assertIn('execution_steps', plan)


class TestGoalExecution(unittest.TestCase):
    """Test cases for GoalExecution class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_memory = Mock()
        self.mock_memory.search_experiences.return_value = []
        self.mock_memory.store_experience.return_value = True

    @patch('main.WorkforceMemory')
    def test_execution_initialization(self, mock_memory_class):
        """Test execution initialization"""
        mock_memory_class.return_value = self.mock_memory

        execution_plan = {
            'goal': 'test goal',
            'pods': ['research'],
            'estimated_cost': 10.0,
            'execution_steps': []
        }

        execution = GoalExecution(execution_plan)

        self.assertEqual(execution.plan, execution_plan)
        self.assertEqual(execution.status, 'pending')
        self.assertEqual(execution.total_cost, 0.0)

    @patch('main.WorkforceMemory')
    def test_execution_status_management(self, mock_memory_class):
        """Test execution status management"""
        mock_memory_class.return_value = self.mock_memory

        execution_plan = {
            'goal': 'test goal',
            'pods': ['research'],
            'estimated_cost': 10.0,
            'execution_steps': []
        }

        execution = GoalExecution(execution_plan)

        # Test status transitions
        execution.start_execution()
        self.assertEqual(execution.status, 'running')

        execution.complete_execution('success')
        self.assertEqual(execution.status, 'completed')

    @patch('main.WorkforceMemory')
    @patch('main.import_module')
    def test_pod_execution_mock(self, mock_import, mock_memory_class):
        """Test pod execution with mocked pod"""
        mock_memory_class.return_value = self.mock_memory

        # Mock pod module
        mock_pod = Mock()
        mock_pod.execute_pod_goal.return_value = {
            'success': True,
            'result': 'Test result',
            'cost': 5.0,
            'verdict': 'GREEN'
        }
        mock_import.return_value = mock_pod

        execution_plan = {
            'goal': 'test goal',
            'pods': ['research'],
            'estimated_cost': 10.0,
            'execution_steps': [{'pod': 'research', 'task': 'test task'}]
        }

        execution = GoalExecution(execution_plan)
        result = execution.execute_step({'pod': 'research', 'task': 'test task'})

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))


class TestExecuteGoalFunction(unittest.TestCase):
    """Test cases for execute_goal function"""

    @patch('main.WorkforceCEO')
    def test_execute_goal_basic(self, mock_ceo_class):
        """Test basic goal execution"""
        # Mock CEO
        mock_ceo = Mock()
        mock_ceo.decompose_goal.return_value = {
            'phases': [],
            'estimated_cost': 10.0,
            'timeline': '1 day'
        }
        mock_ceo.select_pods_for_goal.return_value = ['research']
        mock_ceo.estimate_goal_cost.return_value = 10.0
        mock_ceo.validate_budget.return_value = True
        mock_ceo.create_execution_plan.return_value = {
            'goal': 'test goal',
            'pods': ['research'],
            'estimated_cost': 10.0,
            'execution_steps': []
        }
        mock_ceo_class.return_value = mock_ceo

        # Mock execution
        with patch('main.GoalExecution') as mock_execution_class:
            mock_execution = Mock()
            mock_execution.execute.return_value = {
                'success': True,
                'result': 'Test completed',
                'total_cost': 8.0
            }
            mock_execution_class.return_value = mock_execution

            result = execute_goal("test goal", max_cost=15.0)

            self.assertIsInstance(result, dict)
            self.assertTrue(result.get('success', False))

    @patch('main.WorkforceCEO')
    def test_execute_goal_over_budget(self, mock_ceo_class):
        """Test goal execution when over budget"""
        # Mock CEO with over-budget scenario
        mock_ceo = Mock()
        mock_ceo.decompose_goal.return_value = {
            'phases': [],
            'estimated_cost': 60.0,
            'timeline': '1 day'
        }
        mock_ceo.select_pods_for_goal.return_value = ['research']
        mock_ceo.estimate_goal_cost.return_value = 60.0
        mock_ceo.validate_budget.return_value = False
        mock_ceo_class.return_value = mock_ceo

        result = execute_goal("expensive goal", max_cost=50.0)

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('success', True))
        self.assertIn('budget', result.get('error', '').lower())


class TestIntegration(unittest.TestCase):
    """Integration tests for main components"""

    @patch('main.WorkforceMemory')
    def test_end_to_end_simple_goal(self, mock_memory_class):
        """Test end-to-end execution of a simple goal"""
        # Mock memory
        mock_memory = Mock()
        mock_memory.search_experiences.return_value = []
        mock_memory.store_experience.return_value = True
        mock_memory_class.return_value = mock_memory

        # Mock pod execution
        with patch('main.import_module') as mock_import:
            mock_pod = Mock()
            mock_pod.execute_pod_goal.return_value = {
                'success': True,
                'result': 'Research completed',
                'cost': 5.0,
                'verdict': 'GREEN'
            }
            mock_import.return_value = mock_pod

            # Test simple research goal
            result = execute_goal("Research industry trends", max_cost=20.0)

            self.assertIsInstance(result, dict)
            # Should at least attempt execution without errors


if __name__ == '__main__':
    unittest.main()