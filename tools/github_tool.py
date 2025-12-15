"""
GitHub Management Tool - Repository and deployment management
Handles code management, PR creation, and deployment automation for Devlar products
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

import requests
from github import Github
from loguru import logger
from crewai.tools import BaseTool

class GitHubManagementTool(BaseTool):
    """
    GitHub management tool for repository operations, PR management, and deployment automation.
    Optimized for Devlar's development workflow and product portfolio.
    """

    name: str = "github_management"
    description: str = (
        "Manage GitHub repositories, create pull requests, handle deployments, and automate code operations. "
        "Supports repository management, branch operations, file management, and deployment automation."
    )

    def __init__(self):
        super().__init__()
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_username = os.getenv("GITHUB_USERNAME", "devlar-technologies")
        self.github_org = os.getenv("GITHUB_ORGANIZATION", "devlar-io")

        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

        self.github = Github(self.github_token)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        })

    def _run(
        self,
        operation: str,
        repository: str = "",
        branch: str = "main",
        file_path: str = "",
        content: str = "",
        commit_message: str = "",
        pr_title: str = "",
        pr_description: str = "",
        target_branch: str = "main",
        **kwargs
    ) -> str:
        """
        Execute GitHub management operation

        Args:
            operation: Type of operation (create_repo, create_branch, create_file, create_pr, etc.)
            repository: Repository name (format: owner/repo or just repo)
            branch: Branch name for operations
            file_path: File path for file operations
            content: File content for create/update operations
            commit_message: Commit message for file operations
            pr_title: Title for pull request creation
            pr_description: Description for pull request creation
            target_branch: Target branch for PR merge

        Returns:
            Operation result with details
        """
        try:
            logger.info(f"🔧 GitHub operation: {operation} on {repository}")

            # Normalize repository name
            if repository and "/" not in repository:
                repository = f"{self.github_username}/{repository}"

            if operation == "create_repository":
                return self._create_repository(repository, **kwargs)
            elif operation == "create_branch":
                return self._create_branch(repository, branch, **kwargs)
            elif operation == "create_file":
                return self._create_file(repository, file_path, content, commit_message, branch)
            elif operation == "update_file":
                return self._update_file(repository, file_path, content, commit_message, branch)
            elif operation == "create_pull_request":
                return self._create_pull_request(repository, branch, target_branch, pr_title, pr_description)
            elif operation == "merge_pull_request":
                return self._merge_pull_request(repository, kwargs.get('pr_number', 0))
            elif operation == "deploy_to_vercel":
                return self._trigger_vercel_deployment(repository, branch)
            elif operation == "setup_ci_cd":
                return self._setup_ci_cd_pipeline(repository, kwargs.get('workflow_type', 'web'))
            elif operation == "get_repository_info":
                return self._get_repository_info(repository)
            elif operation == "list_branches":
                return self._list_branches(repository)
            elif operation == "get_file_content":
                return self._get_file_content(repository, file_path, branch)
            else:
                return f"Unknown operation: {operation}"

        except Exception as e:
            logger.error(f"❌ GitHub operation failed: {e}")
            return f"GitHub operation failed: {str(e)}"

    def _create_repository(self, repository: str, **kwargs) -> str:
        """Create a new GitHub repository"""

        try:
            repo_name = repository.split('/')[-1]
            description = kwargs.get('description', f'Devlar project: {repo_name}')
            private = kwargs.get('private', False)

            # Create repository
            if self.github_org and self.github_org != self.github_username:
                # Create in organization
                org = self.github.get_organization(self.github_org)
                repo = org.create_repo(
                    name=repo_name,
                    description=description,
                    private=private,
                    has_issues=True,
                    has_projects=True,
                    has_wiki=False,
                    auto_init=kwargs.get('auto_init', True)
                )
            else:
                # Create in personal account
                user = self.github.get_user()
                repo = user.create_repo(
                    name=repo_name,
                    description=description,
                    private=private,
                    has_issues=True,
                    has_projects=True,
                    has_wiki=False,
                    auto_init=kwargs.get('auto_init', True)
                )

            return f"""
Repository created successfully!
📁 **Repository**: {repo.full_name}
🔗 **URL**: {repo.html_url}
📝 **Description**: {description}
🔒 **Visibility**: {'Private' if private else 'Public'}
"""

        except Exception as e:
            return f"Failed to create repository: {str(e)}"

    def _create_branch(self, repository: str, branch_name: str, **kwargs) -> str:
        """Create a new branch from base branch"""

        try:
            repo = self.github.get_repo(repository)
            base_branch = kwargs.get('base_branch', 'main')

            # Get the base branch reference
            base_ref = repo.get_branch(base_branch)
            base_sha = base_ref.commit.sha

            # Create new branch
            new_ref = repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha
            )

            return f"""
Branch created successfully!
🌿 **Branch**: {branch_name}
📍 **Base**: {base_branch}
🔗 **Repository**: {repository}
"""

        except Exception as e:
            return f"Failed to create branch: {str(e)}"

    def _create_file(self, repository: str, file_path: str, content: str, commit_message: str, branch: str) -> str:
        """Create a new file in repository"""

        try:
            repo = self.github.get_repo(repository)

            # Create file
            result = repo.create_file(
                path=file_path,
                message=commit_message or f"Create {file_path}",
                content=content,
                branch=branch
            )

            return f"""
File created successfully!
📄 **File**: {file_path}
🌿 **Branch**: {branch}
💬 **Commit**: {result['commit'].sha[:7]}
🔗 **URL**: {result['content'].html_url}
"""

        except Exception as e:
            return f"Failed to create file: {str(e)}"

    def _update_file(self, repository: str, file_path: str, content: str, commit_message: str, branch: str) -> str:
        """Update an existing file in repository"""

        try:
            repo = self.github.get_repo(repository)

            # Get current file to get SHA
            current_file = repo.get_contents(file_path, ref=branch)

            # Update file
            result = repo.update_file(
                path=file_path,
                message=commit_message or f"Update {file_path}",
                content=content,
                sha=current_file.sha,
                branch=branch
            )

            return f"""
File updated successfully!
📄 **File**: {file_path}
🌿 **Branch**: {branch}
💬 **Commit**: {result['commit'].sha[:7]}
🔗 **URL**: {result['content'].html_url}
"""

        except Exception as e:
            return f"Failed to update file: {str(e)}"

    def _create_pull_request(self, repository: str, head_branch: str, base_branch: str, title: str, description: str) -> str:
        """Create a pull request"""

        try:
            repo = self.github.get_repo(repository)

            # Create pull request
            pr = repo.create_pull(
                title=title,
                body=description,
                head=head_branch,
                base=base_branch
            )

            return f"""
Pull Request created successfully!
🔄 **PR #{pr.number}**: {title}
🌿 **From**: {head_branch} → {base_branch}
🔗 **URL**: {pr.html_url}
📝 **Description**: {description[:100]}...
"""

        except Exception as e:
            return f"Failed to create pull request: {str(e)}"

    def _merge_pull_request(self, repository: str, pr_number: int) -> str:
        """Merge a pull request"""

        try:
            repo = self.github.get_repo(repository)
            pr = repo.get_pull(pr_number)

            # Check if PR is mergeable
            if not pr.mergeable:
                return f"Pull request #{pr_number} is not mergeable (conflicts detected)"

            # Merge PR
            merge_result = pr.merge(
                commit_message=f"Merge PR #{pr_number}: {pr.title}",
                merge_method="merge"  # Can be "merge", "squash", or "rebase"
            )

            return f"""
Pull Request merged successfully!
✅ **PR #{pr_number}**: {pr.title}
💬 **Merge Commit**: {merge_result.sha[:7]}
🌿 **Merged into**: {pr.base.ref}
"""

        except Exception as e:
            return f"Failed to merge pull request: {str(e)}"

    def _trigger_vercel_deployment(self, repository: str, branch: str) -> str:
        """Trigger Vercel deployment by creating a deployment commit"""

        try:
            repo = self.github.get_repo(repository)

            # Create a deployment trigger file
            timestamp = datetime.now().isoformat()
            deployment_content = f"# Deployment trigger\nTriggered at: {timestamp}\nBranch: {branch}"

            # Check if deployment file exists
            try:
                current_file = repo.get_contents(".vercel/deployment.md", ref=branch)
                # Update existing file
                repo.update_file(
                    path=".vercel/deployment.md",
                    message=f"🚀 Trigger deployment for {branch}",
                    content=deployment_content,
                    sha=current_file.sha,
                    branch=branch
                )
            except:
                # Create new file
                repo.create_file(
                    path=".vercel/deployment.md",
                    message=f"🚀 Trigger deployment for {branch}",
                    content=deployment_content,
                    branch=branch
                )

            return f"""
Vercel deployment triggered!
🚀 **Branch**: {branch}
📁 **Repository**: {repository}
⏰ **Triggered**: {timestamp}
📝 **Note**: Vercel will automatically deploy if connected to this repository
"""

        except Exception as e:
            return f"Failed to trigger deployment: {str(e)}"

    def _setup_ci_cd_pipeline(self, repository: str, workflow_type: str) -> str:
        """Set up GitHub Actions CI/CD pipeline"""

        try:
            repo = self.github.get_repo(repository)

            # Choose workflow template based on type
            if workflow_type == "chrome_extension":
                workflow_content = self._get_chrome_extension_workflow()
            elif workflow_type == "web_app":
                workflow_content = self._get_web_app_workflow()
            elif workflow_type == "python_package":
                workflow_content = self._get_python_package_workflow()
            else:
                workflow_content = self._get_default_workflow()

            # Create workflow file
            workflow_path = ".github/workflows/ci-cd.yml"

            try:
                current_file = repo.get_contents(workflow_path)
                repo.update_file(
                    path=workflow_path,
                    message="🔧 Update CI/CD pipeline",
                    content=workflow_content,
                    sha=current_file.sha
                )
            except:
                repo.create_file(
                    path=workflow_path,
                    message="🔧 Setup CI/CD pipeline",
                    content=workflow_content
                )

            return f"""
CI/CD Pipeline setup complete!
⚙️ **Workflow Type**: {workflow_type}
📁 **Repository**: {repository}
📄 **File**: {workflow_path}
✅ **Status**: Active and ready for next commit
"""

        except Exception as e:
            return f"Failed to setup CI/CD pipeline: {str(e)}"

    def _get_repository_info(self, repository: str) -> str:
        """Get repository information"""

        try:
            repo = self.github.get_repo(repository)

            info = f"""
📁 **Repository Information**: {repo.full_name}
📝 **Description**: {repo.description or 'No description'}
🌐 **URL**: {repo.html_url}
🔒 **Visibility**: {'Private' if repo.private else 'Public'}
⭐ **Stars**: {repo.stargazers_count}
🍴 **Forks**: {repo.forks_count}
📊 **Size**: {repo.size} KB
🗣️ **Language**: {repo.language or 'Not specified'}
📅 **Created**: {repo.created_at.strftime('%Y-%m-%d')}
🔄 **Last Updated**: {repo.updated_at.strftime('%Y-%m-%d')}
🌿 **Default Branch**: {repo.default_branch}
"""

            # Add recent activity
            commits = list(repo.get_commits()[:5])
            if commits:
                info += "\n📈 **Recent Commits**:\n"
                for commit in commits:
                    info += f"• {commit.sha[:7]}: {commit.commit.message.split(chr(10))[0][:50]}...\n"

            return info

        except Exception as e:
            return f"Failed to get repository info: {str(e)}"

    def _list_branches(self, repository: str) -> str:
        """List repository branches"""

        try:
            repo = self.github.get_repo(repository)
            branches = list(repo.get_branches())

            if not branches:
                return "No branches found"

            branch_info = f"🌿 **Branches in {repository}**:\n\n"

            for branch in branches:
                is_default = "⭐ " if branch.name == repo.default_branch else ""
                branch_info += f"• {is_default}{branch.name}\n"

            return branch_info

        except Exception as e:
            return f"Failed to list branches: {str(e)}"

    def _get_file_content(self, repository: str, file_path: str, branch: str) -> str:
        """Get file content from repository"""

        try:
            repo = self.github.get_repo(repository)
            file_content = repo.get_contents(file_path, ref=branch)

            if file_content.encoding == 'base64':
                content = base64.b64decode(file_content.content).decode('utf-8')
            else:
                content = file_content.content

            return f"""
📄 **File**: {file_path}
🌿 **Branch**: {branch}
📊 **Size**: {file_content.size} bytes
📅 **Last Modified**: {file_content.last_modified or 'Unknown'}

**Content**:
```
{content[:1000]}{'...' if len(content) > 1000 else ''}
```
"""

        except Exception as e:
            return f"Failed to get file content: {str(e)}"

    # Workflow templates
    def _get_chrome_extension_workflow(self) -> str:
        """Get Chrome extension CI/CD workflow"""
        return """name: Chrome Extension CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build extension
      run: npm run build

    - name: Lint code
      run: npm run lint

    - name: Package extension
      run: npm run package

    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: extension-build
        path: dist/

    - name: Chrome Web Store Upload (Production)
      if: github.ref == 'refs/heads/main'
      run: |
        echo "Deploy to Chrome Web Store"
        # Add Chrome Web Store deployment script here
"""

    def _get_web_app_workflow(self) -> str:
        """Get web application CI/CD workflow"""
        return """name: Web App CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run tests
      run: npm test

    - name: Build application
      run: npm run build

    - name: Run linter
      run: npm run lint

    - name: Deploy to Vercel (Production)
      if: github.ref == 'refs/heads/main'
      uses: amondnet/vercel-action@v20
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        vercel-args: '--prod'
"""

    def _get_python_package_workflow(self) -> str:
        """Get Python package CI/CD workflow"""
        return """name: Python Package CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest

    - name: Run linter
      run: |
        python -m ruff check .
        python -m black --check .

    - name: Type check
      run: |
        python -m mypy .

  publish:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Build package
      run: |
        python -m pip install --upgrade pip build
        python -m build

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
"""

    def _get_default_workflow(self) -> str:
        """Get default CI/CD workflow"""
        return """name: Default CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci || echo "No package.json found"

    - name: Run tests
      run: npm test || echo "No tests configured"

    - name: Build project
      run: npm run build || echo "No build script configured"

    - name: Deploy to staging
      if: github.ref == 'refs/heads/develop'
      run: echo "Deploy to staging environment"

    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: echo "Deploy to production environment"
"""