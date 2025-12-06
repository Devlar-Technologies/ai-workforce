# Quick Start Guide

Get your Devlar AI Workforce up and running in under 15 minutes.

## Prerequisites

- Python 3.9+
- Git
- API keys for required services (see [Environment Setup](#environment-setup))

## 🚀 Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/alanomeara1/devlar-ai-workforce.git
cd devlar-ai-workforce

# Run the one-click setup script
chmod +x setup.sh
./setup.sh
```

Or manual installation:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env  # or your preferred editor
```

**Required API Keys:**
```bash
# Primary LLM (Grok-4)
XAI_API_KEY=xai-your-api-key-here

# Memory system
PINECONE_API_KEY=your-pinecone-api-key-here

# Research tools
FIRECRAWL_API_KEY=fc-your-firecrawl-key-here

# Telegram interface
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
```

### 3. Test Installation

```bash
# Quick system test
python -c "from main import DevlarCEO; print('✅ Installation successful')"
```

## 🎯 First Execution

### Option A: Telegram Bot (Recommended)

1. **Start the bot:**
```bash
python interfaces/telegram_bot.py
```

2. **Send a message to your bot:**
```
/task Get 100 new Chromentum beta users this week
```

### Option B: Command Line

```bash
# Execute a goal directly
python main.py --goal "Research top 10 AI meditation apps for Zeneural"
```

### Option C: Streamlit Interface

```bash
# Start web interface
streamlit run interfaces/streamlit_app.py
```

Navigate to `http://localhost:8501` and enter your goal.

## 📋 Example Goals

Try these example goals to see the system in action:

### 1. **User Acquisition**
```
Get 100 new Chromentum beta users this week
```
**Expected Output:** Market research → lead generation → outreach campaigns

### 2. **Product Research**
```
Research top 10 AI meditation apps and find gaps for Zeneural
```
**Expected Output:** Competitive analysis → market gaps → feature recommendations

### 3. **Feature Development**
```
Ship a new 'AI affirmation generator' feature for Zeneural
```
**Expected Output:** Feature specification → code implementation → testing → deployment

### 4. **Marketing Campaign**
```
Optimize preorder campaign for PreOrder to drive early sales
```
**Expected Output:** Campaign analysis → optimization recommendations → implementation

### 5. **AI Framework Development**
```
Build prototype AI agent using AimStack for Elephant Desktop
```
**Expected Output:** Technical specification → prototype development → integration testing

## 🔍 Understanding Results

### Execution Flow
1. **CEO Analysis** - Goal breakdown and pod assignment
2. **Pod Execution** - Specialized agents work in parallel waves
3. **Quality Control** - Results validation and verification
4. **Report Generation** - Comprehensive output with assets

### Result Format
```
📊 Execution Results:
├── Status: Completed ✅
├── Execution Time: 23 minutes
├── Pods Involved: Research, Marketing, Sales
├── Report: reports/exec_12345/
│   ├── executive_summary.md
│   ├── detailed_report.pdf
│   └── assets.zip
└── Next Actions: [Recommended follow-ups]
```

## 🛠️ Basic Configuration

### Cost Controls
The system includes built-in cost controls:
- Automatic approval required for operations >$50
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
- Search [GitHub Issues](https://github.com/alanomeara1/devlar-ai-workforce/issues)

**Need Support:**
- 📧 Email: [support@devlar.io](mailto:support@devlar.io)
- 💬 Discord: [Devlar AI Community](https://discord.gg/devlar-ai)
- 📱 Telegram: [@DevlarSupport](https://t.me/DevlarSupport)

---

🎉 **You're ready to build your AI workforce!** Start with simple goals and gradually explore more complex workflows.