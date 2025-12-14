# Free Tier Deployment Guide

Solo founder-friendly deployment using only free tiers and open-source alternatives.

## Free Tier Stack Overview

This configuration minimizes costs by leveraging generous free tiers:

| Component | Free Tier Option | Monthly Limit | Cost After Limit |
|-----------|------------------|---------------|-------------------|
| **AI Models** | Anthropic Claude Sonnet | 1M tokens | $0.003/1K tokens |
| **Vector DB** | Pinecone Serverless | 100K vectors | $0.20/1M vectors |
| **Web Scraping** | Firecrawl | 500 pages | $1/1K pages |
| **Hosting** | Modal.com | $30 credits | Pay per use |
| **Database** | Supabase | 500MB | $25/month pro |
| **Monitoring** | Self-hosted | Free | Infrastructure only |
| **Notifications** | Telegram Bot | Free | Free forever |

**Total Free Usage:** ~$0/month for moderate usage (up to limits)

## Optimized Free Tier Configuration

### 1. Environment Variables (.env)

```bash
# AI Models - Start with free tiers
ANTHROPIC_API_KEY=your_anthropic_key_here  # Free tier: 1M tokens
OPENAI_API_KEY=your_openai_key_here        # $5 credit on signup
XAI_API_KEY=your_xai_grok_key_here         # Optional fallback

# Vector Memory - Free tier
PINECONE_API_KEY=your_pinecone_key_here    # Free: 100K vectors
PINECONE_ENVIRONMENT=gcp-starter           # Free tier environment

# External APIs - Generous free tiers
FIRECRAWL_API_KEY=your_firecrawl_key_here  # Free: 500 pages/month
APOLLO_API_KEY=your_apollo_key_here        # Free: 100 contacts/month
INSTANTLY_API_KEY=optional                 # Optional for basic setup

# Image Generation (optional)
FAL_KEY=your_fal_key_here                  # Free tier available

# GitHub (free for public repos)
GITHUB_TOKEN=your_github_token_here        # Free

# Telegram (completely free)
TELEGRAM_BOT_TOKEN=your_bot_token_here     # Free
TELEGRAM_CHAT_ID=your_chat_id_here         # Free
TELEGRAM_AUTHORIZED_USERS=your_user_id

# Database - Supabase free tier
SUPABASE_URL=your_supabase_url             # Free: 500MB
SUPABASE_ANON_KEY=your_supabase_anon_key   # 2 users included
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Security
WEBHOOK_TOKEN=generate_random_token_here
JWT_SECRET=generate_random_secret_here
```

### 2. Modal.com Free Deployment

Modal.com offers $30 monthly credits - perfect for solo founders.

**Optimized modal_deploy.py:**

```python
# deploy/modal_deploy_free.py
import modal

app = modal.App("devlar-workforce-free")

# Minimal image for cost optimization
image = modal.Image.debian_slim().pip_install([
    "anthropic==0.18.1",
    "openai==1.13.3",
    "pinecone-client==3.0.3",
    "requests==2.31.0",
    "loguru==0.7.2",
    "crewai==0.28.8",
    "python-telegram-bot==20.8",
    "streamlit==1.31.1"
])

@app.function(
    image=image,
    memory=512,  # Reduced memory for cost savings
    timeout=1800,  # 30 minutes max
    concurrency_limit=3,  # Limit concurrent executions
    container_idle_timeout=60,  # Quick shutdown to save costs
)
def execute_goal_free(goal: str) -> dict:
    """Cost-optimized goal execution"""
    # Implementation with cost controls
    pass

@app.function(
    image=image,
    memory=256,  # Minimal for webhook
    timeout=300,
)
@modal.web_endpoint(method="POST")
def webhook_free(goal: str) -> dict:
    """Free tier webhook endpoint"""
    execute_goal_free.spawn(goal)
    return {"status": "started", "goal": goal}
```

### 3. Supabase Database Setup (Free)

Replace PostgreSQL with Supabase's free tier:

**Database Schema (Supabase SQL Editor):**

```sql
-- Free tier Supabase setup
-- executions table
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id TEXT UNIQUE NOT NULL,
    goal TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    results JSONB,
    cost DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies for security
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for authenticated users"
ON executions FOR SELECT
USING (auth.role() = 'authenticated');

CREATE POLICY "Enable insert for authenticated users"
ON executions FOR INSERT
WITH CHECK (auth.role() = 'authenticated');
```

### 4. Railway/Render Free Deployment Alternative

For even simpler deployment, use Railway or Render's free tiers:

**railway.toml:**

```toml
[build]
builder = "dockerfile"
dockerfilePath = "deploy/Dockerfile.free"

[deploy]
numReplicas = 1
restartPolicy = "on-failure"
```

**Dockerfile.free:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
COPY requirements.free.txt .
RUN pip install --no-cache-dir -r requirements.free.txt

COPY . .

# Remove unnecessary files for smaller image
RUN find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} + && \
    rm -rf .git docs/examples tests/

EXPOSE 8501

CMD ["streamlit", "run", "interfaces/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 5. Self-Hosted Minimal Stack

For complete control and zero recurring costs:

**docker-compose.free.yml:**

```yaml
version: '3.8'

services:
  # Main application
  devlar-workforce:
    build:
      context: .
      dockerfile: deploy/Dockerfile.free
    ports:
      - "8501:8501"
    environment:
      - PYTHONPATH=/app
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped

  # Lightweight SQLite instead of PostgreSQL
  # (using file-based storage)

  # Optional: Minimal monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./deploy/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=7d'  # Keep only 7 days

networks:
  default:
    driver: bridge
```

## Cost Monitoring and Optimization

### 1. Usage Tracking

```python
# utils/cost_tracker.py
import json
from datetime import datetime

class FreeTierTracker:
    """Track usage against free tier limits"""

    def __init__(self):
        self.limits = {
            "anthropic_tokens": 1000000,    # 1M tokens
            "pinecone_vectors": 100000,     # 100K vectors
            "firecrawl_pages": 500,         # 500 pages
            "modal_credits": 30.0           # $30 credits
        }
        self.usage_file = "data/usage_tracking.json"

    def track_usage(self, service: str, amount: int, cost: float = 0):
        """Track service usage"""
        usage = self._load_usage()

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in usage:
            usage[today] = {}

        if service not in usage[today]:
            usage[today][service] = {"count": 0, "cost": 0}

        usage[today][service]["count"] += amount
        usage[today][service]["cost"] += cost

        self._save_usage(usage)

        # Check limits
        self._check_limits(usage, today, service)

    def _check_limits(self, usage: dict, date: str, service: str):
        """Alert if approaching limits"""
        if service in self.limits:
            current = usage[date][service]["count"]
            limit = self.limits[service]

            if current > limit * 0.8:  # 80% threshold
                print(f"⚠️ {service} usage at {current}/{limit} ({current/limit*100:.1f}%)")
```

### 2. Automated Cost Alerts

```python
# Add to main.py
def check_free_tier_usage():
    """Check and alert on free tier usage"""
    tracker = FreeTierTracker()

    # Alert via Telegram if approaching limits
    if tracker.approaching_limit():
        # Send notification
        pass
```

## Free Tier Service Alternatives

### Vector Database Alternatives

1. **Pinecone Serverless (Recommended)**
   - Free: 100K vectors
   - Perfect for moderate usage
   - Easy setup

2. **Weaviate Cloud**
   - Free: 14-day trial
   - Self-hosted option available

3. **ChromaDB (Self-hosted)**
   - Completely free
   - Lightweight and fast
   - No external dependencies

**ChromaDB Integration:**

```python
# memory/chromadb_memory.py
import chromadb

class ChromaDBMemory:
    """Free self-hosted vector memory"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path="./data/chromadb")
        self.collection = self.client.get_or_create_collection("executions")

    def store_execution(self, execution_id: str, content: str, metadata: dict):
        """Store execution in ChromaDB"""
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[execution_id]
        )
```

### Web Scraping Alternatives

1. **Firecrawl (Recommended)**
   - Free: 500 pages/month
   - High quality extraction

2. **Playwright (Self-hosted)**
   - Completely free
   - Full browser automation
   - More complex setup

3. **BeautifulSoup + Requests**
   - Free basic scraping
   - Limited compared to Firecrawl

### AI Model Free Tiers

1. **Anthropic Claude**
   - $25 credit on signup
   - Most generous for testing

2. **OpenAI GPT**
   - $5 credit on signup
   - Good for development

3. **Groq (Free)**
   - Fast inference
   - Limited models available

4. **Ollama (Self-hosted)**
   - Completely free
   - Run models locally
   - Requires GPU for speed

## Production Cost Estimation

### Monthly Costs by Usage Level

**Light Usage (Solo Founder Testing):**
- Executions: 20/month
- Cost: $0/month (within free tiers)

**Moderate Usage (Active Development):**
- Executions: 100/month
- Estimated cost: $5-10/month

**Heavy Usage (Production):**
- Executions: 500/month
- Estimated cost: $50-75/month

### Scaling Beyond Free Tiers

When you outgrow free tiers, prioritize upgrades:

1. **First Priority**: Anthropic API ($3/month minimum)
2. **Second Priority**: Modal.com credits ($30/month)
3. **Third Priority**: Pinecone paid plan ($70/month)
4. **Last Priority**: Premium monitoring tools

## Getting Started Checklist

### Free Tier Setup (30 minutes)

1. **Create Accounts** (All Free)
   - [ ] Anthropic Console
   - [ ] Pinecone
   - [ ] Firecrawl
   - [ ] Modal.com
   - [ ] Supabase
   - [ ] Telegram Bot

2. **Configure Environment**
   - [ ] Copy `.env.example` to `.env`
   - [ ] Add all API keys
   - [ ] Set up Telegram bot

3. **Deploy**
   ```bash
   # Quick start with free tier
   git clone https://github.com/alanomeara1/ai-workforce.git
   cd ai-workforce
   cp .env.example .env
   # Edit .env with your keys
   python deploy/modal_deploy_free.py
   ```

4. **Test**
   - [ ] Send test goal via Telegram
   - [ ] Check Streamlit dashboard
   - [ ] Verify cost tracking

5. **Monitor Usage**
   - [ ] Set up cost alerts
   - [ ] Track API usage daily
   - [ ] Plan scaling timeline

This free tier setup provides a fully functional AI workforce for solo founders with minimal ongoing costs!