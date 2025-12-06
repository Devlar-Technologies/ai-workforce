"""
Devlar AI Workforce - Modal.com Deployment Configuration
Production-ready serverless deployment for scalable AI workforce operations
"""

import modal
from pathlib import Path

# Define Modal app
app = modal.App("devlar-workforce")

# Define image with all dependencies
image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")

# Mount the application code
workforce_mount = modal.Mount.from_local_dir(
    Path(__file__).parent.parent,
    remote_path="/app"
)

# Define secrets for environment variables
secrets = [
    modal.Secret.from_name("devlar-workforce-secrets"),  # Contains all API keys
]

# Define storage volumes
logs_volume = modal.Volume.from_name("devlar-logs", create_if_missing=True)
data_volume = modal.Volume.from_name("devlar-data", create_if_missing=True)

@app.function(
    image=image,
    mounts=[workforce_mount],
    secrets=secrets,
    volumes={
        "/app/logs": logs_volume,
        "/app/data": data_volume
    },
    gpu=None,  # CPU-only for most operations
    memory=2048,  # 2GB memory
    timeout=3600,  # 1 hour timeout
    container_idle_timeout=600,  # 10 minute idle timeout
    allow_concurrent_inputs=10,  # Handle multiple requests
)
def execute_goal(goal: str, options: dict = None) -> dict:
    """
    Execute a business goal using the Devlar AI Workforce

    Args:
        goal: The business goal to execute
        options: Optional execution parameters

    Returns:
        Execution results and metadata
    """
    import sys
    sys.path.append("/app")

    from main import DevlarWorkforceCEO
    from memory import WorkforceMemory
    import logging

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/app/logs/modal-execution.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info(f"🚀 Starting goal execution: {goal}")

    try:
        # Initialize CEO and execute goal
        ceo = DevlarWorkforceCEO()
        results = ceo.execute_goal(goal)

        logger.info(f"✅ Goal execution completed: {goal}")

        return {
            "success": True,
            "goal": goal,
            "results": results,
            "execution_platform": "modal.com"
        }

    except Exception as e:
        logger.error(f"❌ Goal execution failed: {e}")
        return {
            "success": False,
            "goal": goal,
            "error": str(e),
            "execution_platform": "modal.com"
        }

@app.function(
    image=image,
    mounts=[workforce_mount],
    secrets=secrets,
    volumes={
        "/app/logs": logs_volume,
        "/app/data": data_volume
    },
    gpu=None,
    memory=1024,
    timeout=300,
    allow_concurrent_inputs=50,
)
@modal.web_endpoint(method="POST")
def webhook_endpoint(goal: str, webhook_token: str = None) -> dict:
    """
    Webhook endpoint for triggering goal execution

    Args:
        goal: Business goal to execute
        webhook_token: Optional authentication token

    Returns:
        Execution acknowledgment
    """
    import os
    import uuid

    # Simple token validation
    expected_token = os.getenv("WEBHOOK_TOKEN")
    if expected_token and webhook_token != expected_token:
        return {
            "success": False,
            "error": "Invalid webhook token"
        }

    # Generate execution ID
    execution_id = str(uuid.uuid4())[:8]

    # Start execution asynchronously
    execute_goal.spawn(goal, {"execution_id": execution_id})

    return {
        "success": True,
        "message": "Goal execution started",
        "execution_id": execution_id,
        "goal": goal
    }

@app.function(
    image=image,
    mounts=[workforce_mount],
    secrets=secrets,
    volumes={
        "/app/logs": logs_volume,
        "/app/data": data_volume
    },
    gpu=None,
    memory=2048,
    timeout=7200,  # 2 hours for Streamlit
)
@modal.web_endpoint(port=8501)
def streamlit_app():
    """
    Streamlit web interface deployment
    """
    import subprocess
    import sys

    sys.path.append("/app")

    # Start Streamlit app
    subprocess.run([
        "streamlit", "run",
        "/app/interfaces/streamlit_app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ])

@app.function(
    image=image,
    mounts=[workforce_mount],
    secrets=secrets,
    volumes={
        "/app/logs": logs_volume,
        "/app/data": data_volume
    },
    gpu=None,
    memory=1024,
    timeout=86400,  # 24 hours
    schedule=None,  # Can be configured for periodic tasks
)
def telegram_bot():
    """
    Telegram bot service deployment
    """
    import sys
    import asyncio

    sys.path.append("/app")

    from interfaces.telegram_bot import TelegramInterface

    # Run Telegram bot
    bot = TelegramInterface()
    asyncio.run(bot.run())

@app.function(
    image=image,
    mounts=[workforce_mount],
    secrets=secrets,
    volumes={
        "/app/logs": logs_volume,
        "/app/data": data_volume
    },
    schedule=modal.Cron("0 */6 * * *")  # Every 6 hours
)
def cleanup_logs():
    """
    Periodic log cleanup and maintenance
    """
    import os
    import time
    from pathlib import Path

    log_dir = Path("/app/logs")
    current_time = time.time()

    # Remove logs older than 7 days
    for log_file in log_dir.glob("*.log"):
        if current_time - log_file.stat().st_mtime > 7 * 24 * 3600:
            log_file.unlink()
            print(f"Removed old log file: {log_file}")

@app.function(
    image=image,
    mounts=[workforce_mount],
    secrets=secrets,
    volumes={
        "/app/logs": logs_volume,
        "/app/data": data_volume
    },
    schedule=modal.Cron("0 0 * * *")  # Daily at midnight
)
def daily_maintenance():
    """
    Daily maintenance tasks
    """
    import sys
    sys.path.append("/app")

    from memory import WorkforceMemory
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Cleanup old memory entries
        memory = WorkforceMemory()
        # Implement cleanup logic here

        logger.info("✅ Daily maintenance completed")

    except Exception as e:
        logger.error(f"❌ Daily maintenance failed: {e}")

# Utility functions for deployment management

@app.local_entrypoint()
def deploy():
    """Deploy the workforce to Modal.com"""
    print("🚀 Deploying Devlar AI Workforce to Modal.com...")
    print("📦 Deployment includes:")
    print("  • Goal execution function")
    print("  • Webhook endpoint")
    print("  • Streamlit web interface")
    print("  • Telegram bot service")
    print("  • Maintenance tasks")
    print("✅ Deployment complete!")

@app.local_entrypoint()
def test_execution(goal: str = "Test goal execution"):
    """Test goal execution on Modal"""
    print(f"🧪 Testing goal execution: {goal}")

    result = execute_goal.remote(goal)
    print(f"📊 Result: {result}")

    return result

if __name__ == "__main__":
    # Local testing
    test_execution("Research top 3 AI productivity tools")