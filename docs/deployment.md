# Deployment Guide

Comprehensive deployment options for Devlar AI Workforce across different environments and platforms.

## Overview

The Devlar AI Workforce supports multiple deployment strategies:

- **Modal.com (Recommended)** - Serverless AI-optimized platform
- **Local Development** - Docker Compose for testing
- **Docker** - Containerized deployment for any cloud
- **Free Tier** - Deploy on free services for small scale

## Prerequisites

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Core LLMs (Required)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Vector Memory
PINECONE_API_KEY=your_pinecone_key

# Tools
GITHUB_TOKEN=your_github_token
APOLLO_API_KEY=your_apollo_key
FIRECRAWL_API_KEY=your_firecrawl_key
INSTANTLY_API_KEY=your_instantly_key
REPLICATE_API_TOKEN=your_replicate_token

# Interfaces
TELEGRAM_BOT_TOKEN=your_telegram_token

# Security
WEBHOOK_TOKEN=secure_random_string

# Monitoring (Optional)
ENABLE_METRICS=true
PROMETHEUS_PORT=9090
GRAFANA_PASSWORD=admin_password
```

### API Key Setup

1. **Anthropic Claude API**: Get from [Anthropic Console](https://console.anthropic.com)
2. **OpenAI API**: Get from [OpenAI Platform](https://platform.openai.com)
3. **xAI Grok API**: Get from [xAI Console](https://console.x.ai)
4. **Pinecone**: Get from [Pinecone Console](https://www.pinecone.io)
5. **Firecrawl**: Get from [Firecrawl](https://firecrawl.dev)
6. **Apollo.io**: Get from [Apollo.io](https://apollo.io)
7. **Telegram Bot**: Create via [@BotFather](https://t.me/BotFather)
8. **GitHub Token**: Create in GitHub Settings > Developer settings

## Deployment Options

### 1. Local Development (Recommended for Testing)

**Quick Start:**

```bash
# Clone and setup
git clone https://github.com/alanomeara1/devlar-agents.git
cd devlar-agents

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose -f deploy/docker-compose.yml up -d

# Access interfaces
# Streamlit Dashboard: http://localhost:8501
# Grafana Monitoring: http://localhost:3000
# Prometheus Metrics: http://localhost:9090
```

**Services Started:**
- Streamlit web interface (port 8501)
- Telegram bot service
- PostgreSQL database
- Redis cache
- Nginx reverse proxy
- Prometheus monitoring
- Grafana dashboards

**Development Commands:**

```bash
# View logs
docker-compose logs -f devlar-workforce

# Stop services
docker-compose down

# Rebuild after changes
docker-compose build --no-cache
```

### 2. Modal.com Deployment (Recommended for Production)

Modal.com provides serverless deployment with automatic scaling.

**Installation:**

```bash
# Install Modal CLI
pip install modal

# Login to Modal
modal token new

# Deploy workforce
cd deploy
python modal_deploy.py
```

**Configuration:**

1. Create Modal secrets with your environment variables:

```bash
modal secret create devlar-workforce-secrets \
  ANTHROPIC_API_KEY=xxx \
  OPENAI_API_KEY=xxx \
  XAI_API_KEY=xxx \
  PINECONE_API_KEY=xxx \
  # ... add all required variables
```

2. Deploy the application:

```bash
modal deploy modal_deploy.py
```

**Available Endpoints:**

- **Goal Execution**: `https://your-app.modal.run/execute`
- **Webhook**: `https://your-app.modal.run/webhook`
- **Streamlit Dashboard**: `https://your-app.modal.run`

**Usage Examples:**

```python
import requests

# Execute goal via API
response = requests.post(
    "https://your-app.modal.run/webhook",
    json={
        "goal": "Research top 10 AI productivity tools",
        "webhook_token": "your_webhook_token"
    }
)
print(response.json())
```

### 3. Docker Deployment

For deployment on any cloud provider or self-hosted environment.

**Build Image:**

```bash
# Build production image
docker build -f deploy/Dockerfile -t devlar-workforce:latest .

# Run container
docker run -d \
  --name devlar-workforce \
  -p 8501:8501 \
  --env-file .env \
  devlar-workforce:latest
```

**Cloud Provider Examples:**

**AWS ECS:**

```bash
# Tag for ECR
docker tag devlar-workforce:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/devlar-workforce:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/devlar-workforce:latest

# Deploy via ECS task definition
```

**Google Cloud Run:**

```bash
# Build and deploy
gcloud run deploy devlar-workforce \
  --image gcr.io/your-project/devlar-workforce \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Azure Container Instances:**

```bash
# Deploy to Azure
az container create \
  --resource-group devlar-rg \
  --name devlar-workforce \
  --image devlar-workforce:latest \
  --dns-name-label devlar-workforce \
  --ports 8501
```

### 4. Kubernetes Deployment

For large-scale deployments with orchestration.

**Manifests:**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devlar-workforce
spec:
  replicas: 3
  selector:
    matchLabels:
      app: devlar-workforce
  template:
    metadata:
      labels:
        app: devlar-workforce
    spec:
      containers:
      - name: workforce
        image: devlar-workforce:latest
        ports:
        - containerPort: 8501
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: workforce-secrets
              key: anthropic-api-key
        # ... add all environment variables
---
apiVersion: v1
kind: Service
metadata:
  name: devlar-workforce-service
spec:
  selector:
    app: devlar-workforce
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

**Deploy:**

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/devlar-workforce
```

## Monitoring and Maintenance

### Health Checks

All deployments include health check endpoints:

- **Application Health**: `GET /health`
- **System Status**: `GET /api/status`
- **Metrics**: `GET /metrics` (Prometheus format)

### Monitoring Stack

**Prometheus Metrics:**
- Execution counts and durations
- API usage and costs
- Pod performance metrics
- System resource usage

**Grafana Dashboards:**
- Workforce performance overview
- Cost analysis and budgeting
- Pod activity and success rates
- API usage patterns

**Access Monitoring:**
- Grafana: `http://your-domain/monitoring/grafana`
- Prometheus: `http://your-domain/monitoring/prometheus`

### Log Management

**Log Locations:**
- Application logs: `/app/logs/`
- Execution logs: `/app/logs/executions/`
- API logs: `/app/logs/api/`

**Log Rotation:**
Automatic cleanup runs daily to remove logs older than 7 days.

### Backup and Recovery

**Database Backups:**

```bash
# PostgreSQL backup
docker exec postgres pg_dump -U workforce devlar_workforce > backup.sql

# Restore
docker exec -i postgres psql -U workforce devlar_workforce < backup.sql
```

**Pinecone Vector Backups:**
Vector data is automatically replicated by Pinecone. For critical deployments, consider:
- Regular exports of execution metadata
- Backup of custom embedding configurations

## Scaling Considerations

### Modal.com Scaling
- Automatic scaling based on request volume
- Cold start latency: ~2-5 seconds
- Concurrent execution limit: 1000 (configurable)

### Docker/K8s Scaling
- Horizontal pod autoscaling based on CPU/memory
- Load balancing across multiple instances
- Database connection pooling required

### Cost Optimization

**Modal.com:**
- Pay-per-use pricing
- Automatic resource optimization
- Idle timeout to minimize costs

**Cloud Providers:**
- Use spot instances for non-critical workloads
- Implement resource limits and quotas
- Monitor and optimize API usage

## Security Best Practices

### Environment Security
- Use secret management systems (AWS Secrets Manager, Google Secret Manager)
- Rotate API keys regularly
- Implement least-privilege access

### Network Security
- Use HTTPS/TLS for all external communications
- Implement API rate limiting
- Secure webhook endpoints with tokens

### Container Security
- Run containers as non-root user
- Regular security updates
- Vulnerability scanning

## Troubleshooting

### Common Issues

**API Key Errors:**
```
❌ Invalid API key for service X
```
Solution: Verify API key format and permissions

**Memory Errors:**
```
❌ Pinecone connection failed
```
Solution: Check Pinecone credentials and index configuration

**Telegram Bot Not Responding:**
```
❌ Bot token invalid
```
Solution: Recreate bot token via @BotFather

### Debug Commands

```bash
# Check container logs
docker logs devlar-workforce

# Test API connectivity
curl -X POST http://localhost:8501/api/health

# Verify environment variables
docker exec devlar-workforce env | grep API_KEY

# Test goal execution
python -c "
from main import DevlarWorkforceCEO
ceo = DevlarWorkforceCEO()
result = ceo.execute_goal('Test system health')
print(result)
"
```

### Support

For deployment issues:
1. Check the troubleshooting section above
2. Review application logs
3. Verify all environment variables are set
4. Test individual component connectivity
5. Create issue on GitHub with logs and configuration details

## Performance Tuning

### Optimization Settings

**Memory Usage:**
```yaml
# docker-compose.yml memory limits
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

**Concurrent Executions:**
```python
# Adjust in main.py
max_concurrent_executions = 5  # Based on available resources
```

**Database Optimization:**
```sql
-- Optimize PostgreSQL for better performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

This deployment guide provides comprehensive options for running the Devlar AI Workforce in any environment from development to production scale.