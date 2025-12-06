"""
Pytest configuration file for Devlar AI Workforce tests
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_environment():
    """Mock environment variables for testing"""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'PINECONE_API_KEY': 'test-pinecone-key',
        'TELEGRAM_BOT_TOKEN': 'test-telegram-token',
        'GITHUB_TOKEN': 'test-github-token',
        'APOLLO_API_KEY': 'test-apollo-key',
        'FIRECRAWL_API_KEY': 'test-firecrawl-key',
        'INSTANTLY_API_KEY': 'test-instantly-key',
        'REPLICATE_API_TOKEN': 'test-replicate-token',
        'ENABLE_METRICS': 'false',
        'MEMORY_DIR': '/tmp/test-memory'
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_memory():
    """Mock WorkforceMemory instance"""
    memory = Mock()
    memory.search_experiences.return_value = []
    memory.store_experience.return_value = True
    memory.get_recent_experiences.return_value = []
    memory.clear_memory.return_value = True
    return memory


@pytest.fixture
def mock_crew():
    """Mock CrewAI Crew instance"""
    crew = Mock()
    crew.kickoff.return_value = {
        'success': True,
        'result': 'Mock crew execution result',
        'cost': 10.0
    }
    return crew


@pytest.fixture
def mock_prometheus():
    """Mock Prometheus client components"""
    with patch.dict('sys.modules', {
        'prometheus_client': MagicMock(),
        'prometheus_client.Counter': MagicMock(),
        'prometheus_client.Histogram': MagicMock(),
        'prometheus_client.Gauge': MagicMock(),
        'prometheus_client.start_http_server': MagicMock(),
        'prometheus_client.generate_latest': MagicMock()
    }):
        yield


@pytest.fixture
def mock_external_apis():
    """Mock all external API clients"""
    mocks = {
        'openai': MagicMock(),
        'anthropic': MagicMock(),
        'pinecone': MagicMock(),
        'firecrawl': MagicMock(),
        'github': MagicMock(),
        'requests': MagicMock(),
        'replicate': MagicMock(),
        'telegram': MagicMock()
    }

    with patch.dict('sys.modules', mocks):
        yield mocks


@pytest.fixture
def sample_test_data():
    """Provide sample test data for various test scenarios"""
    return {
        'goals': {
            'research': 'Research market trends in AI automation tools',
            'product': 'Develop new user onboarding feature',
            'marketing': 'Create content strategy for Q1 2024',
            'sales': 'Design outreach strategy for enterprise clients',
            'customer_success': 'Improve user retention with better onboarding',
            'analytics': 'Analyze user engagement patterns and metrics'
        },
        'execution_results': {
            'success': {
                'success': True,
                'result': 'Task completed successfully',
                'verdict': 'GREEN',
                'cost': 8.5,
                'execution_time': 45.2
            },
            'failure': {
                'success': False,
                'error': 'Task failed due to API limits',
                'verdict': 'RED',
                'cost': 2.1,
                'execution_time': 15.8
            },
            'retry_needed': {
                'success': False,
                'error': 'Temporary service unavailable',
                'verdict': 'YELLOW',
                'cost': 1.5,
                'retry_recommended': True
            }
        },
        'pod_configurations': {
            'research': {
                'agents': ['researcher', 'analyst', 'summarizer'],
                'tools': ['firecrawl', 'github'],
                'budget_range': (5.0, 15.0)
            },
            'marketing': {
                'agents': ['content_strategist', 'campaign_manager', 'social_expert'],
                'tools': ['firecrawl', 'flux'],
                'budget_range': (8.0, 20.0)
            }
        },
        'memory_experiences': [
            {
                'task': 'Market research for SaaS tools',
                'outcome': 'success',
                'lessons': 'Use industry-specific keywords for better results',
                'pod_name': 'research',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'task': 'User onboarding flow design',
                'outcome': 'success',
                'lessons': 'Focus on reducing steps and clear CTAs',
                'pod_name': 'product_development',
                'timestamp': '2024-01-10T14:20:00Z'
            }
        ]
    }


@pytest.fixture
def mock_file_operations(temp_directory):
    """Mock file operations with temporary directory"""
    def create_test_file(filename, content='test content'):
        filepath = os.path.join(temp_directory, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def read_test_file(filename):
        filepath = os.path.join(temp_directory, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        return None

    return {
        'create_file': create_test_file,
        'read_file': read_test_file,
        'temp_dir': temp_directory
    }


@pytest.fixture
def mock_api_responses():
    """Mock API responses for external services"""
    return {
        'openai_completion': {
            'choices': [
                {
                    'message': {
                        'content': 'This is a mock OpenAI response for testing purposes.'
                    }
                }
            ],
            'usage': {
                'prompt_tokens': 50,
                'completion_tokens': 25,
                'total_tokens': 75
            }
        },
        'github_search': {
            'total_count': 2,
            'items': [
                {
                    'name': 'test-repo-1',
                    'full_name': 'user/test-repo-1',
                    'description': 'Test repository 1',
                    'stargazers_count': 150,
                    'language': 'Python'
                },
                {
                    'name': 'test-repo-2',
                    'full_name': 'user/test-repo-2',
                    'description': 'Test repository 2',
                    'stargazers_count': 89,
                    'language': 'JavaScript'
                }
            ]
        },
        'apollo_people_search': {
            'people': [
                {
                    'id': 'person_123',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'title': 'CEO',
                    'email': 'john.doe@example.com',
                    'organization': {'name': 'Example Corp'}
                }
            ]
        },
        'firecrawl_scrape': {
            'success': True,
            'data': {
                'title': 'Test Page Title',
                'content': 'This is the scraped content from the test page.',
                'url': 'https://example.com/test'
            }
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "external_api: mark test as requiring external APIs")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add 'unit' marker to all test files starting with 'test_'
        if item.fspath.basename.startswith('test_'):
            item.add_marker(pytest.mark.unit)

        # Add 'integration' marker to integration tests
        if 'integration' in item.name.lower():
            item.add_marker(pytest.mark.integration)

        # Add 'slow' marker to tests with 'slow' in name
        if 'slow' in item.name.lower():
            item.add_marker(pytest.mark.slow)

        # Add 'external_api' marker to tests that use external APIs
        if any(keyword in item.name.lower() for keyword in ['api', 'external', 'web']):
            item.add_marker(pytest.mark.external_api)