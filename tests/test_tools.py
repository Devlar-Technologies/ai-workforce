"""
Test suite for tools module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os

# Mock external dependencies
with patch.dict('sys.modules', {
    'requests': MagicMock(),
    'firecrawl': MagicMock(),
    'github': MagicMock(),
    'apollo': MagicMock(),
    'replicate': MagicMock(),
    'telegram': MagicMock(),
    'loguru': MagicMock()
}):
    from tools.firecrawl_tool import FirecrawlWebTool
    from tools.github_tool import GitHubTool
    from tools.apollo_tool import ApolloTool
    from tools.flux_tool import FluxImageTool
    from tools.telegram_tool import TelegramTool
    from tools.instantly_tool import InstantlyEmailTool


class TestFirecrawlWebTool(unittest.TestCase):
    """Test cases for FirecrawlWebTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = FirecrawlWebTool()

    @patch('tools.firecrawl_tool.FirecrawlApp')
    def test_scrape_url_success(self, mock_firecrawl):
        """Test successful URL scraping"""
        mock_client = Mock()
        mock_client.scrape_url.return_value = {
            'success': True,
            'data': {
                'content': 'Test content',
                'title': 'Test Title',
                'url': 'https://example.com'
            }
        }
        mock_firecrawl.return_value = mock_client

        result = self.tool.scrape_url('https://example.com')

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('content', result.get('data', {}))

    @patch('tools.firecrawl_tool.FirecrawlApp')
    def test_scrape_url_failure(self, mock_firecrawl):
        """Test URL scraping failure"""
        mock_client = Mock()
        mock_client.scrape_url.side_effect = Exception('Network error')
        mock_firecrawl.return_value = mock_client

        result = self.tool.scrape_url('https://invalid-url.com')

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('success', True))
        self.assertIn('error', result)

    def test_extract_key_points(self):
        """Test key points extraction"""
        test_content = "This is important information. This is secondary info. Key point here."

        result = self.tool.extract_key_points(test_content, max_points=2)

        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)

    def test_validate_url(self):
        """Test URL validation"""
        valid_urls = [
            'https://example.com',
            'http://test.com',
            'https://subdomain.example.com/path'
        ]

        invalid_urls = [
            'not-a-url',
            'ftp://example.com',
            '',
            None
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.tool.validate_url(url))

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.tool.validate_url(url))


class TestGitHubTool(unittest.TestCase):
    """Test cases for GitHubTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = GitHubTool()

    @patch('tools.github_tool.Github')
    def test_search_repositories(self, mock_github):
        """Test repository search"""
        mock_client = Mock()
        mock_repo = Mock()
        mock_repo.name = 'test-repo'
        mock_repo.description = 'Test repository'
        mock_repo.html_url = 'https://github.com/user/test-repo'
        mock_repo.stargazers_count = 100
        mock_repo.language = 'Python'

        mock_client.search_repositories.return_value = [mock_repo]
        mock_github.return_value = mock_client

        result = self.tool.search_repositories('python machine learning', limit=1)

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('repositories', result.get('data', {}))

    @patch('tools.github_tool.Github')
    def test_get_repository_info(self, mock_github):
        """Test getting repository information"""
        mock_client = Mock()
        mock_repo = Mock()
        mock_repo.name = 'test-repo'
        mock_repo.description = 'Test repository'
        mock_repo.html_url = 'https://github.com/user/test-repo'
        mock_repo.stargazers_count = 100
        mock_repo.language = 'Python'
        mock_repo.topics = ['ai', 'ml']

        mock_client.get_repo.return_value = mock_repo
        mock_github.return_value = mock_client

        result = self.tool.get_repository_info('user/test-repo')

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('repository', result.get('data', {}))

    def test_parse_github_url(self):
        """Test GitHub URL parsing"""
        test_cases = [
            ('https://github.com/user/repo', ('user', 'repo')),
            ('https://github.com/user/repo/', ('user', 'repo')),
            ('user/repo', ('user', 'repo')),
            ('invalid-url', (None, None))
        ]

        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.tool.parse_github_url(url)
                self.assertEqual(result, expected)


class TestApolloTool(unittest.TestCase):
    """Test cases for ApolloTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = ApolloTool()

    @patch('tools.apollo_tool.requests.post')
    def test_search_people_success(self, mock_post):
        """Test successful people search"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'people': [
                {
                    'id': '123',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'title': 'CEO',
                    'email': 'john@example.com',
                    'organization': {'name': 'Test Corp'}
                }
            ]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.tool.search_people(company_name='Test Corp', job_titles=['CEO'])

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('people', result.get('data', {}))

    @patch('tools.apollo_tool.requests.post')
    def test_search_companies_success(self, mock_post):
        """Test successful company search"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'organizations': [
                {
                    'id': '456',
                    'name': 'Test Corp',
                    'website_url': 'https://testcorp.com',
                    'industry': 'Technology',
                    'num_employees': 100
                }
            ]
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.tool.search_companies(industry='Technology', size_range='51-200')

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('companies', result.get('data', {}))

    def test_validate_search_params(self):
        """Test search parameter validation"""
        # Valid parameters
        self.assertTrue(self.tool.validate_search_params(company_name='Test'))
        self.assertTrue(self.tool.validate_search_params(job_titles=['CEO']))

        # Invalid parameters
        self.assertFalse(self.tool.validate_search_params())
        self.assertFalse(self.tool.validate_search_params(company_name=''))


class TestFluxImageTool(unittest.TestCase):
    """Test cases for FluxImageTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = FluxImageTool()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('tools.flux_tool.replicate.run')
    def test_generate_image_success(self, mock_replicate):
        """Test successful image generation"""
        mock_replicate.return_value = ['https://example.com/generated-image.jpg']

        result = self.tool.generate_image(
            'A beautiful sunset',
            output_dir=self.temp_dir
        )

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))
        self.assertIn('image_url', result.get('data', {}))

    def test_validate_prompt(self):
        """Test prompt validation"""
        valid_prompts = [
            'A simple image',
            'Complex scene with multiple elements'
        ]

        invalid_prompts = [
            '',
            'x' * 501,  # Too long
            None
        ]

        for prompt in valid_prompts:
            with self.subTest(prompt=prompt):
                self.assertTrue(self.tool.validate_prompt(prompt))

        for prompt in invalid_prompts:
            with self.subTest(prompt=prompt):
                self.assertFalse(self.tool.validate_prompt(prompt))

    def test_create_filename(self):
        """Test filename creation"""
        prompt = 'A beautiful sunset over mountains'
        filename = self.tool.create_filename(prompt)

        self.assertTrue(filename.endswith('.jpg'))
        self.assertNotIn(' ', filename)
        self.assertLessEqual(len(filename), 100)


class TestTelegramTool(unittest.TestCase):
    """Test cases for TelegramTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = TelegramTool()

    @patch('tools.telegram_tool.Bot')
    def test_send_message_success(self, mock_bot_class):
        """Test successful message sending"""
        mock_bot = Mock()
        mock_bot.send_message.return_value = Mock(message_id=123)
        mock_bot_class.return_value = mock_bot

        result = self.tool.send_message('123456', 'Test message')

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))

    @patch('tools.telegram_tool.Bot')
    def test_send_message_failure(self, mock_bot_class):
        """Test message sending failure"""
        mock_bot = Mock()
        mock_bot.send_message.side_effect = Exception('Network error')
        mock_bot_class.return_value = mock_bot

        result = self.tool.send_message('123456', 'Test message')

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('success', True))

    def test_validate_chat_id(self):
        """Test chat ID validation"""
        valid_ids = ['123456789', '-123456789', '123']
        invalid_ids = ['', 'not-a-number', None, 'abc123']

        for chat_id in valid_ids:
            with self.subTest(chat_id=chat_id):
                self.assertTrue(self.tool.validate_chat_id(chat_id))

        for chat_id in invalid_ids:
            with self.subTest(chat_id=chat_id):
                self.assertFalse(self.tool.validate_chat_id(chat_id))


class TestInstantlyEmailTool(unittest.TestCase):
    """Test cases for InstantlyEmailTool"""

    def setUp(self):
        """Set up test fixtures"""
        self.tool = InstantlyEmailTool()

    @patch('tools.instantly_tool.requests.post')
    def test_create_campaign_success(self, mock_post):
        """Test successful campaign creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'campaign_id': 'camp_123',
            'status': 'created'
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.tool.create_campaign(
            name='Test Campaign',
            subject='Test Subject',
            template='Hello {{first_name}}'
        )

        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success', False))

    def test_validate_email_template(self):
        """Test email template validation"""
        valid_templates = [
            'Hello {{first_name}}',
            'Dear {{first_name}} {{last_name}}, welcome to {{company}}!'
        ]

        invalid_templates = [
            '',
            None,
            'No variables here',
            'x' * 5001  # Too long
        ]

        for template in valid_templates:
            with self.subTest(template=template):
                self.assertTrue(self.tool.validate_email_template(template))

        for template in invalid_templates:
            with self.subTest(template=template):
                self.assertFalse(self.tool.validate_email_template(template))

    def test_parse_lead_data(self):
        """Test lead data parsing"""
        test_leads = [
            {
                'email': 'test@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'company': 'Test Corp'
            }
        ]

        result = self.tool.parse_lead_data(test_leads)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn('email', result[0])


class TestToolsIntegration(unittest.TestCase):
    """Integration tests for tools"""

    def test_tool_error_handling(self):
        """Test that all tools handle errors gracefully"""
        tools = [
            FirecrawlWebTool(),
            GitHubTool(),
            ApolloTool(),
            FluxImageTool(),
            TelegramTool(),
            InstantlyEmailTool()
        ]

        for tool in tools:
            with self.subTest(tool=tool.__class__.__name__):
                # Each tool should have error handling
                self.assertTrue(hasattr(tool, 'validate_input') or
                               hasattr(tool, 'validate_url') or
                               hasattr(tool, 'validate_prompt') or
                               hasattr(tool, 'validate_chat_id') or
                               hasattr(tool, 'validate_email_template') or
                               hasattr(tool, 'validate_search_params'))


if __name__ == '__main__':
    unittest.main()