"""
Test suite for memory.py module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import json
from datetime import datetime

# Mock Pinecone to avoid import errors in testing
with patch.dict('sys.modules', {
    'pinecone': MagicMock(),
    'openai': MagicMock(),
    'loguru': MagicMock()
}):
    from memory import WorkforceMemory, MemoryError


class TestWorkforceMemory(unittest.TestCase):
    """Test cases for WorkforceMemory class"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'memory_dir': self.temp_dir,
            'enable_pinecone': False,
            'embedding_model': 'text-embedding-3-small'
        }

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('memory.os.getenv')
    def test_init_without_pinecone(self, mock_getenv):
        """Test initialization without Pinecone"""
        mock_getenv.side_effect = lambda key, default=None: {
            'PINECONE_API_KEY': None,
            'MEMORY_DIR': self.temp_dir
        }.get(key, default)

        memory = WorkforceMemory()
        self.assertFalse(memory.pinecone_enabled)
        self.assertEqual(memory.memory_dir, self.temp_dir)

    def test_store_experience_local(self):
        """Test storing experience in local memory"""
        memory = WorkforceMemory()
        memory.pinecone_enabled = False
        memory.memory_dir = self.temp_dir

        test_experience = {
            'task': 'test_task',
            'outcome': 'success',
            'lessons': 'test lesson',
            'pod_name': 'test_pod'
        }

        # Test successful storage
        result = memory.store_experience(
            task="test task",
            outcome="success",
            lessons="test lesson",
            pod_name="test_pod"
        )

        self.assertTrue(result)

        # Verify file was created
        files = os.listdir(self.temp_dir)
        self.assertEqual(len(files), 1)

        # Verify content
        with open(os.path.join(self.temp_dir, files[0]), 'r') as f:
            stored_data = json.load(f)
            self.assertEqual(stored_data['task'], 'test task')
            self.assertEqual(stored_data['outcome'], 'success')

    def test_search_experiences_local(self):
        """Test searching experiences in local memory"""
        memory = WorkforceMemory()
        memory.pinecone_enabled = False
        memory.memory_dir = self.temp_dir

        # Store some test experiences
        experiences = [
            ('research task', 'success', 'use specific keywords'),
            ('marketing task', 'failure', 'need better targeting'),
            ('sales task', 'success', 'follow up is key')
        ]

        for task, outcome, lessons in experiences:
            memory.store_experience(task, outcome, lessons, 'test_pod')

        # Test search
        results = memory.search_experiences('research', limit=2)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 2)

        # Test with pod filter
        results = memory.search_experiences('task', pod_name='test_pod', limit=5)
        self.assertGreaterEqual(len(results), 1)

    def test_get_recent_experiences(self):
        """Test getting recent experiences"""
        memory = WorkforceMemory()
        memory.pinecone_enabled = False
        memory.memory_dir = self.temp_dir

        # Store test experience
        memory.store_experience('recent task', 'success', 'test', 'test_pod')

        # Get recent experiences
        results = memory.get_recent_experiences(limit=1)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 1)

    def test_clear_memory(self):
        """Test clearing memory"""
        memory = WorkforceMemory()
        memory.pinecone_enabled = False
        memory.memory_dir = self.temp_dir

        # Store test experience
        memory.store_experience('test', 'success', 'test', 'test_pod')

        # Verify file exists
        files_before = os.listdir(self.temp_dir)
        self.assertGreater(len(files_before), 0)

        # Clear memory
        result = memory.clear_memory()
        self.assertTrue(result)

        # Verify files are cleared
        files_after = os.listdir(self.temp_dir)
        self.assertEqual(len(files_after), 0)

    @patch('memory.openai.OpenAI')
    def test_generate_embedding_mock(self, mock_openai):
        """Test embedding generation with mocked OpenAI"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        memory = WorkforceMemory()
        embedding = memory._generate_embedding('test text')

        self.assertEqual(embedding, [0.1, 0.2, 0.3])
        mock_client.embeddings.create.assert_called_once()

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        memory = WorkforceMemory()
        memory.pinecone_enabled = False
        memory.memory_dir = '/invalid/path'

        # Test storing to invalid directory
        result = memory.store_experience('test', 'success', 'test', 'test_pod')
        self.assertFalse(result)

        # Test searching in invalid directory
        results = memory.search_experiences('test')
        self.assertEqual(results, [])

    def test_filename_generation(self):
        """Test memory filename generation"""
        memory = WorkforceMemory()

        # Test with normal task
        filename = memory._generate_filename('test task', 'test_pod')
        self.assertTrue(filename.endswith('.json'))
        self.assertIn('test_pod', filename)

        # Test with special characters
        filename = memory._generate_filename('test/task\\with:chars', 'pod')
        self.assertNotIn('/', filename)
        self.assertNotIn('\\', filename)
        self.assertNotIn(':', filename)


class TestMemoryIntegration(unittest.TestCase):
    """Integration tests for memory functionality"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up integration test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_memory_persistence(self):
        """Test that memory persists across instances"""
        # First instance stores experience
        memory1 = WorkforceMemory()
        memory1.pinecone_enabled = False
        memory1.memory_dir = self.temp_dir

        memory1.store_experience('persistent task', 'success', 'lesson', 'pod1')

        # Second instance should be able to access stored experience
        memory2 = WorkforceMemory()
        memory2.pinecone_enabled = False
        memory2.memory_dir = self.temp_dir

        results = memory2.search_experiences('persistent')
        self.assertGreater(len(results), 0)
        self.assertIn('persistent task', str(results[0]))

    def test_concurrent_access_simulation(self):
        """Test simulation of concurrent access to memory"""
        memory = WorkforceMemory()
        memory.pinecone_enabled = False
        memory.memory_dir = self.temp_dir

        # Simulate multiple rapid stores
        for i in range(5):
            result = memory.store_experience(
                f'concurrent_task_{i}',
                'success',
                f'lesson_{i}',
                f'pod_{i % 2}'
            )
            self.assertTrue(result)

        # Verify all were stored
        results = memory.search_experiences('concurrent', limit=10)
        self.assertGreaterEqual(len(results), 5)


if __name__ == '__main__':
    unittest.main()