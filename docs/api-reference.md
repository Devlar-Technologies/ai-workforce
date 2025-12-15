# API Reference

Complete API documentation for Devlar AI Workforce components and interfaces.

## Overview

The Devlar AI Workforce provides multiple API interfaces:

- **CEO Orchestrator API** - Core business goal execution
- **Pod APIs** - Direct specialist pod interactions
- **Tool APIs** - Individual tool function calls
- **Memory API** - Vector memory and execution history
- **Webhook API** - External integrations
- **Monitoring API** - System metrics and health

## Authentication

### API Key Authentication

```python
headers = {
    "Authorization": f"Bearer {your_api_key}",
    "Content-Type": "application/json"
}
```

### Telegram Bot Authentication

```python
# User ID whitelist in environment variables
TELEGRAM_AUTHORIZED_USERS=123456789,987654321
```

## CEO Orchestrator API

### Execute Business Goal

Execute high-level business goals through the AI workforce.

```python
POST /api/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `goal` | string | Yes | Business goal to execute |
| `priority` | string | No | Execution priority (high/medium/low) |
| `budget_limit` | number | No | Budget limit in EUR |
| `auto_approve` | boolean | No | Auto-approve operations under threshold |
| `context` | object | No | Additional execution context |

**Request Example:**

```json
{
    "goal": "Research top 10 AI productivity tools and their pricing",
    "priority": "high",
    "budget_limit": 25.0,
    "auto_approve": true,
    "context": {
        "target_market": "SaaS founders",
        "focus_areas": ["pricing", "features", "user_reviews"]
    }
}
```

**Response:**

```json
{
    "success": true,
    "execution_id": "abc12345",
    "status": "started",
    "estimated_duration": "15-30 minutes",
    "assigned_pods": ["research_pod", "analytics_pod"],
    "workflow": {
        "total_waves": 3,
        "current_wave": 1,
        "tasks": [
            {
                "wave": 1,
                "pod": "research_pod",
                "agent": "market_researcher",
                "task": "Search and identify top AI productivity tools"
            }
        ]
    }
}
```

### Get Execution Status

```python
GET /api/execution/{execution_id}
```

**Response:**

```json
{
    "execution_id": "abc12345",
    "goal": "Research top 10 AI productivity tools",
    "status": "in_progress",
    "progress": {
        "overall_progress": 65,
        "current_wave": 2,
        "total_waves": 3,
        "current_task": "Analyzing pricing models"
    },
    "pod_activity": {
        "research_pod": {
            "status": "completed",
            "tasks_completed": 3,
            "quality_score": 94
        },
        "analytics_pod": {
            "status": "active",
            "current_task": "Comparing feature sets",
            "progress": 45
        }
    },
    "cost_tracking": {
        "estimated_cost": 12.50,
        "actual_cost": 8.75,
        "budget_remaining": 16.25
    }
}
```

### Cancel Execution

```python
DELETE /api/execution/{execution_id}
```

**Response:**

```json
{
    "success": true,
    "message": "Execution cancelled successfully",
    "execution_id": "abc12345",
    "final_status": "cancelled"
}
```

## Pod APIs

### Research Pod

Direct interaction with the research specialist pod.

```python
POST /api/pods/research/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_type` | string | Yes | research/competitor_analysis/market_analysis |
| `target` | string | Yes | Research target (company, product, market) |
| `depth` | string | No | Research depth (basic/detailed/comprehensive) |
| `output_format` | string | No | Output format (summary/report/presentation) |

**Example:**

```json
{
    "task_type": "competitor_analysis",
    "target": "Notion competitors",
    "depth": "comprehensive",
    "output_format": "report",
    "specific_aspects": ["pricing", "features", "market_share"]
}
```

### Product Development Pod

```python
POST /api/pods/product-dev/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_type` | string | Yes | web_app/chrome_extension/api/mobile_app |
| `action` | string | Yes | implement/update/optimize/deploy |
| `repository` | string | No | GitHub repository URL |
| `requirements` | string | Yes | Detailed requirements |

**Example:**

```json
{
    "project_type": "chrome_extension",
    "action": "implement",
    "repository": "https://github.com/user/chromentum",
    "requirements": "Add dark mode toggle with user preference persistence"
}
```

### Marketing Pod

```python
POST /api/pods/marketing/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `campaign_type` | string | Yes | content/social/email/ads/seo |
| `target_audience` | string | Yes | Target audience description |
| `goals` | array | Yes | Campaign goals |
| `budget` | number | No | Campaign budget |

### Sales Outreach Pod

```python
POST /api/pods/sales/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `outreach_type` | string | Yes | cold_email/linkedin/phone/demo |
| `target_criteria` | object | Yes | Lead qualification criteria |
| `message_template` | string | No | Custom message template |

### Customer Success Pod

```python
POST /api/pods/customer-success/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_type` | string | Yes | onboard/support/retention/feedback |
| `customer_segment` | string | No | Customer segment |
| `priority` | string | No | Issue priority level |

### Analytics Pod

```python
POST /api/pods/analytics/execute
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `analysis_type` | string | Yes | performance/user_behavior/conversion/revenue |
| `data_source` | string | Yes | Data source identifier |
| `time_period` | string | No | Analysis time period |
| `metrics` | array | No | Specific metrics to analyze |

## Tool APIs

### Firecrawl Tool

Web scraping and content extraction.

```python
POST /api/tools/firecrawl/scrape
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to scrape |
| `extract_type` | string | No | content/pricing/features/reviews |
| `format` | string | No | markdown/json/text |

**Example:**

```json
{
    "url": "https://notion.so/pricing",
    "extract_type": "pricing",
    "format": "json"
}
```

**Response:**

```json
{
    "success": true,
    "url": "https://notion.so/pricing",
    "content": {
        "pricing_tiers": [
            {
                "name": "Personal",
                "price": "Free",
                "features": ["Unlimited pages", "Basic blocks"]
            },
            {
                "name": "Personal Pro",
                "price": "$4/month",
                "features": ["Unlimited file uploads", "Version history"]
            }
        ]
    },
    "metadata": {
        "extraction_time": "2024-01-15T10:30:00Z",
        "page_title": "Notion Pricing",
        "word_count": 1250
    }
}
```

### GitHub Tool

Repository management and automation.

```python
POST /api/tools/github/create-pr
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repository` | string | Yes | Repository name (owner/repo) |
| `title` | string | Yes | Pull request title |
| `description` | string | Yes | Pull request description |
| `source_branch` | string | Yes | Source branch name |
| `target_branch` | string | No | Target branch (default: main) |
| `changes` | array | Yes | List of file changes |

**Example:**

```json
{
    "repository": "devlar-technologies/ai-workforce",
    "title": "Add dark mode toggle feature",
    "description": "Implements dark mode with user preference persistence",
    "source_branch": "feature/dark-mode",
    "target_branch": "main",
    "changes": [
        {
            "file_path": "js/darkMode.js",
            "content": "// Dark mode implementation",
            "action": "create"
        }
    ]
}
```

### Apollo Tool

Lead generation and prospecting.

```python
POST /api/tools/apollo/search-people
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_titles` | array | Yes | Target job titles |
| `company_keywords` | array | No | Company keywords |
| `location` | string | No | Geographic location |
| `company_size` | string | No | Company size range |

### Telegram Tool

Send notifications and updates.

```python
POST /api/tools/telegram/send
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | Message content |
| `message_type` | string | No | info/warning/error/success |
| `parse_mode` | string | No | Markdown/HTML |
| `reply_markup` | object | No | Inline keyboard |

### Flux Tool

AI image generation.

```python
POST /api/tools/flux/generate
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Image description |
| `style` | string | No | Image style |
| `aspect_ratio` | string | No | Image aspect ratio |
| `quality` | string | No | Image quality (standard/hd) |

## Memory API

### Store Execution

```python
POST /api/memory/store
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `execution_id` | string | Yes | Execution identifier |
| `goal` | string | Yes | Original goal |
| `results` | object | Yes | Execution results |
| `metadata` | object | No | Additional metadata |

### Retrieve Similar

```python
POST /api/memory/search
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `limit` | number | No | Result limit (default: 5) |
| `similarity_threshold` | number | No | Minimum similarity score |

**Response:**

```json
{
    "results": [
        {
            "execution_id": "def67890",
            "goal": "Research AI tools for productivity",
            "similarity_score": 0.94,
            "results_summary": "Found 15 top AI productivity tools...",
            "execution_date": "2024-01-10T14:20:00Z"
        }
    ]
}
```

## Webhook API

### Goal Execution Webhook

External systems can trigger goal execution via webhook.

```python
POST /webhook/execute
```

**Headers:**

```
Authorization: Bearer {webhook_token}
Content-Type: application/json
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `goal` | string | Yes | Business goal to execute |
| `callback_url` | string | No | Webhook for status updates |
| `metadata` | object | No | Additional context |

**Example:**

```json
{
    "goal": "Analyze website performance and provide optimization recommendations",
    "callback_url": "https://your-app.com/webhook/status",
    "metadata": {
        "source": "monitoring_system",
        "priority": "high",
        "website_url": "https://devlar.io"
    }
}
```

**Response:**

```json
{
    "success": true,
    "execution_id": "wbh12345",
    "message": "Goal execution started",
    "estimated_completion": "2024-01-15T16:00:00Z"
}
```

### Status Update Webhook

Receive execution status updates (if callback_url provided).

```python
POST {your_callback_url}
```

**Payload:**

```json
{
    "execution_id": "wbh12345",
    "status": "completed",
    "progress": 100,
    "results": {
        "deliverables": [
            {
                "type": "report",
                "title": "Website Performance Analysis",
                "content": "...",
                "recommendations": ["Optimize images", "Enable caching"]
            }
        ]
    },
    "metadata": {
        "completion_time": "2024-01-15T15:45:00Z",
        "execution_duration": "00:25:30",
        "total_cost": 8.75
    }
}
```

## Monitoring API

### Health Check

```python
GET /api/health
```

**Response:**

```json
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "components": {
        "ceo": "online",
        "pods": {
            "research": "healthy",
            "product_dev": "healthy",
            "marketing": "healthy",
            "sales": "healthy",
            "customer_success": "healthy",
            "analytics": "healthy"
        },
        "memory": "connected",
        "external_apis": {
            "anthropic": "connected",
            "openai": "connected",
            "pinecone": "connected",
            "firecrawl": "connected"
        }
    }
}
```

### System Metrics

```python
GET /api/metrics
```

**Response (Prometheus format):**

```
# HELP workforce_executions_total Total number of executions
# TYPE workforce_executions_total counter
workforce_executions_total{status="completed"} 150
workforce_executions_total{status="failed"} 5

# HELP workforce_execution_duration_seconds Execution duration
# TYPE workforce_execution_duration_seconds histogram
workforce_execution_duration_seconds_bucket{le="300"} 45
workforce_execution_duration_seconds_bucket{le="900"} 120
workforce_execution_duration_seconds_bucket{le="1800"} 140
```

### Usage Statistics

```python
GET /api/stats
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | Time period (day/week/month) |
| `pod` | string | Filter by pod |

**Response:**

```json
{
    "period": "week",
    "executions": {
        "total": 45,
        "completed": 42,
        "failed": 3,
        "success_rate": 93.3
    },
    "pod_performance": {
        "research_pod": {
            "executions": 15,
            "avg_duration": 450,
            "success_rate": 100,
            "avg_quality_score": 94
        }
    },
    "cost_analysis": {
        "total_cost": 127.50,
        "avg_cost_per_execution": 2.83,
        "budget_utilization": 42.5
    },
    "api_usage": {
        "anthropic": {
            "requests": 1250,
            "tokens": 85000,
            "cost": 45.20
        }
    }
}
```

## Error Handling

### Standard Error Response

```json
{
    "success": false,
    "error": {
        "code": "INVALID_GOAL",
        "message": "Goal description is too vague or incomplete",
        "details": {
            "received_goal": "do something",
            "suggestions": [
                "Be more specific about the desired outcome",
                "Include relevant context and constraints"
            ]
        }
    },
    "request_id": "req_12345"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_GOAL` | Goal is too vague or malformed |
| `BUDGET_EXCEEDED` | Operation would exceed budget limit |
| `API_LIMIT_REACHED` | External API rate limit reached |
| `AUTHENTICATION_FAILED` | Invalid or missing authentication |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `INTERNAL_ERROR` | Unexpected system error |
| `TIMEOUT` | Operation timed out |

## Rate Limiting

### Limits

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| `/api/execute` | 10 requests | per minute |
| `/api/pods/*` | 30 requests | per minute |
| `/api/tools/*` | 60 requests | per minute |
| `/webhook/*` | 100 requests | per minute |

### Headers

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642267200
```

## SDKs and Client Libraries

### Python SDK

```python
from devlar_workforce import WorkforceCEO

# Initialize client
ceo = WorkforceCEO(api_key="your_api_key")

# Execute goal
result = ceo.execute_goal(
    goal="Research competitor pricing for Chrome extensions",
    budget_limit=25.0
)

# Monitor execution
status = ceo.get_execution_status(result.execution_id)

# Get execution history
history = ceo.get_execution_history(limit=10)
```

### JavaScript SDK

```javascript
import { WorkforceCEO } from '@devlar/workforce-sdk';

const ceo = new WorkforceCEO({ apiKey: 'your_api_key' });

// Execute goal
const result = await ceo.executeGoal({
    goal: 'Research competitor pricing for Chrome extensions',
    budgetLimit: 25.0
});

// Monitor execution
const status = await ceo.getExecutionStatus(result.executionId);
```

### cURL Examples

```bash
# Execute goal
curl -X POST https://workforce.devlar.io/api/execute \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Research top 10 AI productivity tools",
    "budget_limit": 25.0
  }'

# Check status
curl -X GET https://workforce.devlar.io/api/execution/abc12345 \
  -H "Authorization: Bearer your_api_key"

# Send Telegram notification
curl -X POST https://workforce.devlar.io/api/tools/telegram/send \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test notification from API",
    "message_type": "info"
  }'
```

## WebSocket API

Real-time execution updates via WebSocket connection.

### Connection

```javascript
const ws = new WebSocket('wss://workforce.devlar.io/ws');

ws.onopen = function() {
    // Authenticate
    ws.send(JSON.stringify({
        type: 'auth',
        token: 'your_api_key'
    }));

    // Subscribe to execution updates
    ws.send(JSON.stringify({
        type: 'subscribe',
        execution_id: 'abc12345'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    switch(data.type) {
        case 'status_update':
            console.log('Progress:', data.progress);
            break;
        case 'completion':
            console.log('Completed:', data.results);
            break;
        case 'error':
            console.error('Error:', data.error);
            break;
    }
};
```

## Best Practices

### Goal Formulation

**Good Examples:**
- "Research top 10 AI productivity tools with pricing and feature comparison"
- "Implement dark mode toggle for Chromentum Chrome extension with user preference persistence"
- "Create email marketing campaign for Zeneural targeting meditation app users"

**Poor Examples:**
- "Do research" (too vague)
- "Fix the website" (unclear what needs fixing)
- "Make money" (no specific strategy or context)

### Budget Management

```python
# Set appropriate budget limits
result = ceo.execute_goal(
    goal="Complex market research task",
    budget_limit=50.0,  # Reasonable for research
    auto_approve=True   # For operations under $50
)
```

### Error Handling

```python
try:
    result = ceo.execute_goal(goal="Research task")
except WorkforceAPIError as e:
    if e.code == "BUDGET_EXCEEDED":
        # Handle budget issues
        pass
    elif e.code == "API_LIMIT_REACHED":
        # Handle rate limiting
        time.sleep(60)
        # Retry
    else:
        # Handle other errors
        logger.error(f"Execution failed: {e.message}")
```

### Performance Optimization

1. **Batch Related Goals**: Group similar tasks for better efficiency
2. **Use Appropriate Budget Limits**: Set realistic limits based on task complexity
3. **Monitor Usage**: Track API usage to avoid hitting limits
4. **Cache Results**: Store execution results for similar future goals
5. **Leverage Memory**: Similar past executions improve performance

This comprehensive API reference provides all the interfaces needed to integrate with and extend the Devlar AI Workforce system.