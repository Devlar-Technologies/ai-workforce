# Production Setup Guide

Complete guide for deploying and configuring the Devlar AI Workforce in production.

## 🎯 Overview

This guide covers all manual setup tasks required after the development work is complete. The AI workforce system is now fully built and tested - these steps will get it running in your production environment.

## 📋 Setup Checklist

### **Phase 1: Core Infrastructure Setup**

#### **1.1 Modal.com Account & Deployment**
- [ ] Create Modal.com account at [modal.com](https://modal.com)
- [ ] Install Modal CLI: `pip install modal`
- [ ] Login: `modal token new`
- [ ] Deploy workforce: `modal deploy deploy/modal_deploy.py`
- [ ] Verify deployment: `modal app list`

#### **1.2 API Keys & Secrets Configuration**
Set up Modal secrets with all required API keys:

```bash
# Create Modal secret with all API keys
modal secret create devlar-workforce-secrets \
  OPENAI_API_KEY=your_openai_key \
  ANTHROPIC_API_KEY=your_anthropic_key \
  PINECONE_API_KEY=your_pinecone_key \
  GITHUB_TOKEN=your_github_token \
  APOLLO_API_KEY=your_apollo_key \
  FIRECRAWL_API_KEY=your_firecrawl_key \
  INSTANTLY_API_KEY=your_instantly_key \
  REPLICATE_API_TOKEN=your_replicate_token \
  TELEGRAM_BOT_TOKEN=your_telegram_token \
  WEBHOOK_TOKEN=your_secure_webhook_token
```

**Required API Keys:**
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)
- **Pinecone**: [app.pinecone.io](https://app.pinecone.io) (for vector memory)
- **GitHub**: [github.com/settings/tokens](https://github.com/settings/tokens) (for repo access)
- **Apollo.io**: [app.apollo.io](https://app.apollo.io) (for lead generation)
- **Firecrawl**: [firecrawl.dev](https://firecrawl.dev) (for web scraping)
- **Instantly.ai**: [instantly.ai](https://instantly.ai) (for email automation)
- **Replicate**: [replicate.com](https://replicate.com) (for image generation)

### **Phase 2: External Services Setup**

#### **2.1 Pinecone Vector Database**
```bash
# Create Pinecone index for memory storage
# Index name: devlar-workforce-memory
# Dimensions: 1536 (for OpenAI embeddings)
# Metric: cosine
# Pod type: p1.x1 (starter)
```

#### **2.2 Telegram Bot**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot: `/newbot`
3. Choose bot name and username
4. Save the bot token
5. Configure bot commands:
```
/start - Start using Devlar AI Workforce
/help - Get help and available commands
/goal - Execute a business goal
/status - Check workforce status
/cost - View cost tracking
```

#### **2.3 External Tool Accounts**
- **Apollo.io**: Set up account for B2B lead generation
- **Instantly.ai**: Configure for email automation campaigns
- **Firecrawl**: Set up for advanced web scraping
- **Replicate**: Configure for AI image generation

### **Phase 3: Testing & Validation**

#### **3.1 Core Functionality Tests**
```bash
# Test goal execution
modal run deploy/modal_deploy.py::test_execution

# Test specific pods
python examples/execute_goal.py --pod research --goal "Research AI automation trends"
python examples/execute_goal.py --pod marketing --goal "Create content strategy"

# Run unit tests
python tests/run_tests.py --all
```

#### **3.2 Interface Testing**
- [ ] **Streamlit Interface**: Access web dashboard at Modal endpoint
- [ ] **Telegram Bot**: Send `/start` command and test goal execution
- [ ] **Webhook Endpoint**: Test API integration with external systems
- [ ] **Memory System**: Verify experiences are being stored and retrieved

#### **3.3 Monitoring Validation**
- [ ] Check Prometheus metrics collection
- [ ] Verify Grafana dashboards are populated
- [ ] Test alert notifications
- [ ] Validate cost tracking accuracy

### **Phase 4: Production Configuration**

#### **4.1 Budget & Cost Controls**
Configure in `main.py`:
```python
# Adjust budget limits
MAX_BUDGET = 50.0  # Maximum spend per goal
APPROVAL_THRESHOLD = 50.0  # Human approval required above this amount
DAILY_BUDGET_LIMIT = 200.0  # Daily spending limit
```

#### **4.2 Quality Control Thresholds**
Configure in pod agents:
```python
# Quality control settings
MIN_QUALITY_SCORE = 80  # Minimum score for GREEN verdict
RETRY_ON_YELLOW = True  # Retry tasks with YELLOW verdict
MAX_RETRIES = 2  # Maximum retry attempts
```

#### **4.3 Memory Settings**
Configure in `memory.py`:
```python
# Memory retention settings
MAX_EXPERIENCES = 10000  # Maximum stored experiences
CLEANUP_DAYS = 30  # Days to retain experiences
SIMILARITY_THRESHOLD = 0.8  # Experience relevance threshold
```

### **Phase 5: Monitoring & Alerts Setup**

#### **5.1 Prometheus + Grafana Deployment**
```bash
# Deploy monitoring stack
docker-compose -f deploy/docker-compose.yml up -d

# Access dashboards
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

#### **5.2 Alert Configuration**
Configure notifications in `deploy/alert_rules.yml`:
- **Critical alerts**: System down, budget exceeded
- **Warning alerts**: High latency, queue backlogs
- **Info alerts**: Daily summaries, cost reports

#### **5.3 Log Management**
- **Modal Logs**: `modal logs devlar-workforce`
- **Local Logs**: Check `logs/` directory
- **Grafana Dashboards**: Real-time metrics visualization

### **Phase 6: Business Integration**

#### **6.1 Team Access Setup**
- [ ] Share Streamlit dashboard URL with team
- [ ] Add team members to Telegram bot
- [ ] Configure role-based access controls
- [ ] Set up approval workflows for high-cost goals

#### **6.2 Workflow Integration**
- [ ] Connect to existing business tools (CRM, project management)
- [ ] Set up automated goal triggers (scheduled tasks)
- [ ] Configure result notifications (email, Slack, etc.)
- [ ] Establish reporting cadence

#### **6.3 Initial Production Goals**
Start with these proven goal types:
```python
# Research & Analysis
"Research top 5 competitors in our market segment"
"Analyze customer feedback from last quarter"

# Marketing & Content
"Create content calendar for Q1 2024"
"Develop social media strategy for product launch"

# Sales & Business Development
"Identify 50 potential enterprise clients in fintech"
"Create sales outreach sequence for SMB market"

# Product Development
"Analyze user onboarding flow optimization opportunities"
"Research feature requests from customer feedback"
```

## ⚡ Quick Start Commands

### Deploy Everything
```bash
# 1. Deploy to Modal
modal deploy deploy/modal_deploy.py

# 2. Test deployment
modal run deploy/modal_deploy.py::test_execution

# 3. Start monitoring
docker-compose -f deploy/docker-compose.yml up -d

# 4. Run example goals
python examples/execute_goal.py
```

### Daily Operations
```bash
# Check workforce status
modal logs devlar-workforce

# Monitor costs
python -c "from utils.metrics import get_cost_tracker; print(f'Daily cost: ${get_cost_tracker().get_daily_total():.2f}')"

# View recent executions
modal app logs devlar-workforce --follow
```

## 🚨 Troubleshooting

### Common Issues

**API Key Errors**
```bash
# Verify secrets are configured
modal secret list
# Update if needed
modal secret create devlar-workforce-secrets KEY=value
```

**Memory Issues**
```bash
# Check Pinecone connection
python -c "from memory import WorkforceMemory; m = WorkforceMemory(); print(m.search_experiences('test'))"
```

**Pod Execution Failures**
```bash
# Check individual pod functionality
python -c "from pods.research_pod.agents import execute_pod_goal; print(execute_pod_goal('test research task'))"
```

**Cost Tracking Issues**
```bash
# Verify metrics collection
python -c "from utils.metrics import get_metrics; m = get_metrics(); print(f'Enabled: {m.enabled}')"
```

## 📊 Success Metrics

### Week 1 Targets
- [ ] 10+ successful goal executions
- [ ] All 6 pods functioning correctly
- [ ] Cost tracking under $100/week
- [ ] 95%+ success rate (GREEN verdicts)

### Month 1 Targets
- [ ] 100+ goal executions
- [ ] Average execution time under 2 minutes
- [ ] Cost efficiency improving through memory learning
- [ ] Team actively using all interfaces

### Ongoing KPIs
- **Execution Success Rate**: >95% GREEN verdicts
- **Average Cost Per Goal**: Trending downward (learning effect)
- **Response Time**: <120 seconds average
- **Memory Utilization**: Growing experience database
- **Business Value**: Measurable impact on productivity

## 🔒 Security Considerations

### API Key Management
- Store all keys in Modal secrets (never in code)
- Rotate keys monthly
- Use least-privilege access for each service
- Monitor API usage for anomalies

### Access Controls
- Secure webhook endpoints with tokens
- Implement rate limiting
- Log all goal executions for audit
- Restrict high-cost operations to approved users

### Data Privacy
- No sensitive data stored in memory without encryption
- Comply with data retention policies
- Regular cleanup of old experiences
- Secure communication channels

## 📞 Support & Maintenance

### Daily Checks
- Review execution logs for errors
- Monitor cost accumulation
- Check system resource usage
- Verify all services are healthy

### Weekly Tasks
- Review goal execution patterns
- Analyze cost trends and optimization opportunities
- Update pod configurations based on learnings
- Clean up old logs and temporary files

### Monthly Reviews
- Performance optimization based on metrics
- API key rotation
- Memory system cleanup and optimization
- Business value assessment and ROI calculation

---

**Next Step**: Begin with Phase 1 - Modal.com deployment and API key configuration.