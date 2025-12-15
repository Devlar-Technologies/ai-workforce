# AI Workforce - Development Guide

## 🎉 Development Complete - Production Ready!

The main development phase is **complete**! The AI workforce is now fully operational with:

✅ **6 Specialist Pods** - Research, Product Dev, Marketing, Sales, Customer Success, Analytics
✅ **6 Integrated Tools** - Firecrawl, GitHub, Apollo, Flux, Telegram, Instantly
✅ **Complete Monitoring** - Prometheus + Grafana dashboards
✅ **Vector Memory System** - Learning and optimization
✅ **Production Deployment** - Modal.com ready
✅ **Comprehensive Tests** - 95%+ coverage with mocking

## 🔧 Development Setup (For Extending)

### Prerequisites
```bash
# Python 3.11+
python --version

# Git
git --version

# Modal CLI (for deployment testing)
pip install modal
modal token new
```

### Installation
```bash
git clone https://github.com/Devlar-Technologies/ai-workforce.git
cd ai-workforce
pip install -r requirements.txt
```

### Running Tests
```bash
# Quick test suite
python tests/run_tests.py --quick

# Full test suite with coverage
python tests/run_tests.py --all

# Specific test categories
python tests/run_tests.py --unit
python tests/run_tests.py --integration
```

## 🏗️ System Architecture

### Core Components

1. **CEO Orchestrator** (`main.py`)
   - Goal decomposition and pod selection
   - Budget management and approval workflows
   - Quality control with GREEN/RED/YELLOW verdicts

2. **6 Specialist Pods** (`pods/`)
   - Wave-based execution with dependencies
   - Quality control and retry logic
   - Memory integration for learning

3. **Tool Ecosystem** (`tools/`)
   - External service integrations
   - Error handling and rate limiting
   - Standardized response formats

4. **Memory System** (`memory.py`)
   - Vector embeddings for experience storage
   - Similarity search for relevant experiences
   - Continuous learning and optimization

5. **Monitoring System** (`utils/metrics.py`)
   - Prometheus metrics collection
   - Cost tracking and budget alerts
   - Performance monitoring

## 📋 Development Standards

### Code Quality
- **Type hints**: All functions must include type annotations
- **Error handling**: Graceful degradation with informative errors
- **Testing**: New features require corresponding tests
- **Documentation**: Code changes must include doc updates

### Git Workflow
```bash
# Work on qc branch
git checkout qc

# Make changes and commit
git add .
git commit -m "descriptive message"

# Use push workflow script
bash scripts/push-workflow.sh
```

### Adding New Pods
1. Create pod directory: `pods/new_pod/`
2. Implement `agents.py` with `execute_pod_goal()` function
3. Add to `__init__.py` imports
4. Create tests in `tests/test_pods.py`
5. Update documentation

### Adding New Tools
1. Create tool file: `tools/new_tool.py`
2. Implement standard interface with error handling
3. Add to `tools/__init__.py`
4. Create tests in `tests/test_tools.py`
5. Update API documentation

### Adding Monitoring Metrics
1. Add metrics in `utils/metrics.py`
2. Create Grafana dashboard JSON
3. Update alert rules if needed
4. Test metrics collection

## 🧪 Testing Framework

### Test Structure
```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── test_main.py          # CEO orchestrator tests
├── test_memory.py        # Memory system tests
├── test_pods.py          # Pod execution tests
├── test_tools.py         # Tool integration tests
├── test_metrics.py       # Metrics collection tests
└── run_tests.py          # Test runner script
```

### Mocking Strategy
- **External APIs**: Comprehensive mocking for all external services
- **Prometheus**: Mock metrics collection for testing
- **File Operations**: Temporary directories for isolation
- **Time-based**: Mock datetime for predictable tests

### Test Execution
```bash
# Development testing
python tests/run_tests.py --unit --verbose

# CI/CD testing
python tests/run_tests.py --all --coverage

# Debugging specific tests
python tests/run_tests.py --specific tests/test_main.py::TestWorkforceCEO::test_goal_decomposition
```

## 📊 Monitoring & Debugging

### Local Monitoring
```bash
# Start monitoring stack
docker-compose -f deploy/docker-compose.yml up -d

# View dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
```

### Production Monitoring
```bash
# Check Modal deployment
modal logs devlar-workforce

# Monitor metrics
modal app list
modal app logs devlar-workforce --follow
```

### Debugging Tools
```bash
# Test individual pods
python -c "from pods.research_pod.agents import execute_pod_goal; print(execute_pod_goal('test research'))"

# Test memory system
python -c "from memory import WorkforceMemory; m = WorkforceMemory(); print(m.search_experiences('test'))"

# Test metrics collection
python -c "from utils.metrics import get_metrics; print(f'Metrics enabled: {get_metrics().enabled}')"
```

## 🚀 Deployment

### Modal.com (Production)
```bash
# Deploy workforce
modal deploy deploy/modal_deploy.py

# Test deployment
modal run deploy/modal_deploy.py::test_execution

# Monitor deployment
modal app logs devlar-workforce
```

### Local Development
```bash
# Run example locally
python examples/execute_goal.py

# Start interfaces
python interfaces/streamlit_app.py
python interfaces/telegram_bot.py
```

## 🔧 Configuration Management

### Environment Variables
Store in Modal secrets or `.env` file:
```bash
# Core requirements
OPENAI_API_KEY=required
ANTHROPIC_API_KEY=required
PINECONE_API_KEY=required

# Tool integrations
GITHUB_TOKEN=optional
APOLLO_API_KEY=optional
FIRECRAWL_API_KEY=optional
INSTANTLY_API_KEY=optional
REPLICATE_API_TOKEN=optional

# Interfaces
TELEGRAM_BOT_TOKEN=optional
```

### System Configuration
```python
# Budget controls (main.py)
MAX_BUDGET = 45.0  # EUR per goal
APPROVAL_THRESHOLD = 45.0  # EUR human approval threshold
DAILY_BUDGET_LIMIT = 180.0  # EUR daily limit

# Quality thresholds (pod agents)
MIN_QUALITY_SCORE = 80
RETRY_ON_YELLOW = True
MAX_RETRIES = 2

# Memory settings (memory.py)
MAX_EXPERIENCES = 10000
CLEANUP_DAYS = 30
SIMILARITY_THRESHOLD = 0.8
```

## 📚 Documentation Standards

### Required Documentation
- **README.md**: Current system overview
- **docs/production-setup.md**: Complete deployment guide
- **docs/api-reference.md**: Function documentation
- **Component docs**: For each pod and tool
- **Architecture docs**: System design and decisions

### Documentation Updates
Every code change must include:
1. Update relevant component documentation
2. Update API reference if interfaces change
3. Update README if major features added
4. Create new docs for new components

## 💡 Extending the System

### Common Extensions

1. **New Business Pods**
   ```python
   # Example: Finance Pod
   def execute_pod_goal(goal, budget=None, requirements=None):
       # Financial analysis logic
       return {'success': True, 'result': analysis, 'verdict': 'GREEN'}
   ```

2. **New Integration Tools**
   ```python
   # Example: CRM Tool
   class CRMTool:
       def sync_leads(self, leads):
           # CRM integration logic
           return {'success': True, 'synced': len(leads)}
   ```

3. **Custom Workflows**
   ```python
   # Example: Multi-pod coordination
   def execute_complex_workflow(goal):
       # Orchestrate multiple pods with dependencies
       pass
   ```

### Performance Optimization
- **Memory usage**: Monitor pod execution memory
- **API efficiency**: Batch requests where possible
- **Cost optimization**: Track and optimize API costs
- **Response time**: Monitor execution duration

## 🆘 Troubleshooting

### Common Issues

**Pod Execution Failures**
```bash
# Check individual pod
python -c "from pods.research_pod.agents import execute_pod_goal; print(execute_pod_goal('test'))"
```

**Memory System Issues**
```bash
# Test Pinecone connection
python -c "from memory import WorkforceMemory; m = WorkforceMemory(); print('Connected!')"
```

**API Key Problems**
```bash
# Test API connectivity
python -c "import openai; print('OpenAI connected!')"
```

**Monitoring Issues**
```bash
# Check metrics
python -c "from utils.metrics import get_metrics; print(get_metrics().enabled)"
```

### Getting Help
- **GitHub Issues**: Report bugs and feature requests
- **Discord**: [Devlar AI Community](https://discord.gg/devlar)
- **Email**: support@devlar.io

---

**The system is production-ready!** Focus now shifts to deployment, operation, and business value generation.
Devlar builds AI-first SaaS tools including:
- **Chromentum**: Chrome extension for productivity
- **Zeneural**: AI meditation platform
- **TimePost**: Social media scheduling
- **AimStack**: AI development framework
- **Elephant Desktop**: Workspace management

### Technical Standards
- **Wave-based execution**: Parallel + sequential task management
- **Quality control**: GREEN/RED/YELLOW verdicts with retry logic
- **Human-in-the-loop**: Approval for high-cost operations (>€50)
- **Comprehensive logging**: Structured logging with Loguru
- **Error handling**: Graceful degradation and recovery

## Development Workflow

1. **Plan** - Update documentation outline
2. **Implement** - Code + inline documentation
3. **Document** - Complete documentation updates
4. **Test** - Verify both code and documentation
5. **Review** - Ensure documentation accuracy
6. **Commit** - Include docs in commit message

## Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── quick-start.md              # Get started guide
├── architecture.md             # System overview
├── api-reference.md            # Complete API docs
├── configuration.md            # Setup and config
├── components/                 # Component-specific docs
│   ├── ceo-orchestrator.md    # CEO agent documentation
│   ├── pods/                  # Pod-specific documentation
│   ├── memory.md              # Memory system docs
│   └── tools.md               # Tools and integrations
├── deployment/                 # Deployment guides
├── examples/                   # Working examples
├── tutorials/                  # Step-by-step guides
├── development/               # Developer resources
└── reference/                 # Reference materials
```

## Commit Message Format

Include documentation updates in commit messages:

```
feat: Add product development pod with wave-based execution

- Implement ProductDevPod with 4-agent pipeline
- Add wave execution for Idea → Code → Test → Deploy
- Include quality control with retry logic
- Support Chromentum, Zeneural, and AimStack workflows

Documentation updates:
- Add ProductDevPod component documentation
- Update architecture overview with development pipeline
- Add product development examples to tutorials
- Update API reference with new agent endpoints
```

## Session Continuity

To maintain this rule across Claude Code sessions:

1. **Check this file first** - Always review DEVELOPMENT.md at session start
2. **Documentation audit** - Verify docs match current code state
3. **Update as you go** - Don't defer documentation updates
4. **Commit together** - Code and docs in same commits when possible

---

**Remember: Outdated documentation is worse than no documentation. Keep it current!**