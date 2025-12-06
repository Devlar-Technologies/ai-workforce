# Devlar AI Workforce - Production Docker Image
# Multi-stage build for optimized production deployment

FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Set labels
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="devlar-workforce" \
      org.label-schema.description="Devlar AI Workforce - Hierarchical AI system for business automation" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/alanomeara1/devlar-agents" \
      org.label-schema.schema-version="1.0"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Remove development files
RUN find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -type d -exec rm -rf {} + && \
    rm -rf .git .github .gitignore .env.example

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r workforce && useradd -r -g workforce workforce

# Set working directory
WORKDIR /app

# Copy from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create directories
RUN mkdir -p /app/logs /app/data /app/temp && \
    chown -R workforce:workforce /app

# Switch to non-root user
USER workforce

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose ports
EXPOSE 8501

# Default command (can be overridden)
CMD ["streamlit", "run", "interfaces/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]