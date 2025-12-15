# Quick Start Guide

Get your AI Workforce up and running in under 15 minutes.

## Prerequisites

- Python 3.11+
- Git
- API keys for required services (see setup guide below)

## 🚀 Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Devlar-Technologies/ai-workforce.git
cd ai-workforce

# Install dependencies
pip install -r requirements.txt
```

### 2. Quick Test (Local)

```bash
# Run example execution locally
python examples/execute_goal.py
```

This will run in simulation mode to test the system without API keys.

## 🌐 Production Deployment

### 1. Modal.com Setup

```bash
# Install Modal CLI
pip install modal

# Create account and login
modal token new

# Deploy the workforce
modal deploy deploy/modal_deploy.py
```

### 2. Configure API Keys

**Required API Keys:**
```bash
# Core LLMs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Memory system
PINECONE_API_KEY=your_pinecone_key

# Tools
GITHUB_TOKEN=your_github_token
APOLLO_API_KEY=your_apollo_key
FIRECRAWL_API_KEY=your_firecrawl_key
INSTANTLY_API_KEY=your_instantly_key
REPLICATE_API_TOKEN=your_replicate_token

# Interfaces
TELEGRAM_BOT_TOKEN=your_telegram_token
```

### 3. Test Installation

```bash
# Quick system test
python examples/execute_goal.py
```

## 🎯 First Execution

### Option A: Direct Execution (Easiest)

```bash
# Execute a goal directly
python -c "from main import execute_goal; print(execute_goal('Research AI automation trends'))"
```

### Option B: Example Script

```bash
# Run interactive examples
python examples/execute_goal.py
```

### Option C: Production (Modal.com)

```bash
# Test on Modal after deployment
modal run deploy/modal_deploy.py::test_execution
```

## 📋 Example Goals

Try these example goals to see the system in action:

### 1. **Market Research**
```
Research top 5 AI automation tools in 2025
```
**Expected Output:** Research Pod → Comprehensive market analysis with competitor insights

### 2. **Product Development**
```
Design user onboarding flow for SaaS platform
```
**Expected Output:** Product Pod → User journey mapping, wireframes, technical specs

### 3. **Marketing Campaign**
```
Create content strategy for Q1 2026 product launch
```
**Expected Output:** Marketing Pod → Content calendar, blog posts, social strategy

### 4. **Sales Strategy**
```
Generate 50 qualified leads for enterprise software
```
**Expected Output:** Sales Pod → Lead lists, outreach sequences, qualification criteria

### 5. **Customer Success**
```
Improve user retention with better onboarding experience
```
**Expected Output:** Customer Success Pod → Retention analysis, onboarding optimization

## 🔍 Understanding Results

### Execution Flow
1. **CEO Orchestrator** - Goal decomposition and pod selection
2. **Wave Execution** - Specialist pods execute in dependency order
3. **Quality Control** - GREEN/YELLOW/RED verdicts with auto-retry
4. **Memory Storage** - Experience saved for future learning

### Result Format
```
📊 Execution Results:
├── Status: Completed ✅ (GREEN verdict)
├── Execution Time: 2.3 minutes
├── Cost: €7.70
├── Pods Used: Research → Marketing → Sales
├── Result: Comprehensive strategy document
├── Learning: Stored in vector memory for future use
└── Verdict: GREEN (High quality, no retry needed)
```

## 🛠️ Basic Configuration

### Cost Controls
The system includes built-in cost controls:
- Automatic approval required for operations >€50
- Real-time cost tracking
- Budget alerts via Telegram

### Performance Tuning
```python
# In your .env file
MAX_CONCURRENT_TASKS=5  # Adjust based on your API limits
EXECUTION_TIMEOUT=3600  # 1 hour max per goal
```

### Logging
```bash
# Set log level
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# View logs
tail -f logs/devlar-workforce.log
```

## 🔧 Common Issues

### API Key Issues
```bash
# Test API connectivity
python tools/test_apis.py
```

### Memory Issues
```bash
# Test Pinecone connection
python -c "from memory import DevlarMemory; m = DevlarMemory(); print('Memory connected')"
```

### Telegram Bot Not Responding
1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Check bot is added to your chat
3. Ensure bot has appropriate permissions

## 📚 Next Steps

### Learning More
- [Architecture Overview](./architecture.md) - Understand how it works
- [Example Workflows](./examples/) - See detailed examples
- [API Reference](./api-reference.md) - Integrate with your systems

### Customization
- [Custom Tools](./tutorials/custom-tools.md) - Add new capabilities
- [Workflow Design](./tutorials/workflows.md) - Create custom workflows
- [Agent Configuration](./configuration.md) - Tune agent behavior

### Deployment
- [Modal.com Deployment](./deployment/modal-deployment.md) - Serverless production
- [Docker Deployment](./deployment/docker.md) - Container deployment
- [Monitoring Setup](./deployment/monitoring.md) - Production monitoring

## 🆘 Getting Help

**Quick Help:**
- Check [Troubleshooting Guide](./reference/troubleshooting.md)
- Review [Error Codes](./reference/error-codes.md)
- Search [GitHub Issues](https://github.com/Devlar-Technologies/ai-workforce/issues)

**Need Support:**
- 📧 Email: [support@devlar.io](mailto:support@devlar.io)
- 🌐 Website: [devlar.io](https://www.devlar.io)

---

🎉 **You're ready to build your AI workforce!** Start with simple goals and gradually explore more complex workflows.