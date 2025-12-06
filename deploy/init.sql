-- Devlar AI Workforce - Database Initialization
-- PostgreSQL schema for execution history and metadata

-- Create database if not exists (handled by docker-compose)
-- CREATE DATABASE IF NOT EXISTS devlar_workforce;

-- Use the workforce database
\c devlar_workforce;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Execution history table
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id VARCHAR(8) UNIQUE NOT NULL,
    goal TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'medium',

    -- Timing
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,

    -- Execution details
    workflow_type VARCHAR(50),
    assigned_pods JSONB,
    progress JSONB,
    results JSONB,

    -- Cost tracking
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    budget_limit DECIMAL(10,2),

    -- User and context
    user_id VARCHAR(100),
    chat_id BIGINT,
    execution_context JSONB,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pod activity tracking
CREATE TABLE IF NOT EXISTS pod_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    pod_name VARCHAR(100) NOT NULL,
    agent_name VARCHAR(100),

    -- Activity details
    task_description TEXT,
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,

    -- Results
    output JSONB,
    quality_score INTEGER,
    cost DECIMAL(8,2),

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Memory embeddings (for Pinecone fallback)
CREATE TABLE IF NOT EXISTS memory_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,

    -- Content
    content_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,

    -- Vector (for local similarity search if needed)
    embedding VECTOR(1536), -- OpenAI embedding dimension

    -- External references
    pinecone_id VARCHAR(100),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,

    -- API details
    api_provider VARCHAR(50) NOT NULL,
    endpoint VARCHAR(200),
    method VARCHAR(10),

    -- Usage metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost DECIMAL(8,4),
    duration_ms INTEGER,

    -- Status
    status_code INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User approvals
CREATE TABLE IF NOT EXISTS approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,

    -- Approval details
    operation_description TEXT NOT NULL,
    estimated_cost DECIMAL(10,2),
    risk_level VARCHAR(10) DEFAULT 'medium',

    -- Decision
    status VARCHAR(20) DEFAULT 'pending',
    approved_by VARCHAR(100),
    decision_time TIMESTAMP WITH TIME ZONE,
    notes TEXT,

    -- Timing
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    timeout_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification log
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,

    -- Notification details
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200),
    message TEXT,

    -- Delivery
    channel VARCHAR(50), -- telegram, email, webhook
    recipient VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',

    -- Metadata
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_start_time ON executions(start_time);
CREATE INDEX idx_executions_user_id ON executions(user_id);
CREATE INDEX idx_executions_execution_id ON executions(execution_id);

CREATE INDEX idx_pod_activities_execution_id ON pod_activities(execution_id);
CREATE INDEX idx_pod_activities_pod_name ON pod_activities(pod_name);
CREATE INDEX idx_pod_activities_status ON pod_activities(status);

CREATE INDEX idx_api_usage_execution_id ON api_usage(execution_id);
CREATE INDEX idx_api_usage_provider ON api_usage(api_provider);
CREATE INDEX idx_api_usage_timestamp ON api_usage(timestamp);

CREATE INDEX idx_approvals_execution_id ON approvals(execution_id);
CREATE INDEX idx_approvals_status ON approvals(status);

CREATE INDEX idx_notifications_execution_id ON notifications(execution_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Full-text search indexes
CREATE INDEX idx_executions_goal_fts ON executions USING gin(to_tsvector('english', goal));

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_executions_updated_at
    BEFORE UPDATE ON executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
CREATE OR REPLACE VIEW execution_summary AS
SELECT
    e.execution_id,
    e.goal,
    e.status,
    e.start_time,
    e.end_time,
    e.duration_seconds,
    e.actual_cost,
    COUNT(pa.id) as pod_activities_count,
    AVG(pa.quality_score) as avg_quality_score
FROM executions e
LEFT JOIN pod_activities pa ON e.id = pa.execution_id
GROUP BY e.id, e.execution_id, e.goal, e.status, e.start_time, e.end_time, e.duration_seconds, e.actual_cost;

CREATE OR REPLACE VIEW daily_metrics AS
SELECT
    DATE(start_time) as date,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_executions,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_executions,
    SUM(actual_cost) as total_cost,
    AVG(duration_seconds) as avg_duration_seconds
FROM executions
WHERE start_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(start_time)
ORDER BY date DESC;

-- Insert sample data for testing (optional)
-- INSERT INTO executions (execution_id, goal, status)
-- VALUES ('test123', 'Sample test goal for system validation', 'completed');

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO workforce;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO workforce;

COMMIT;