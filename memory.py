"""
Devlar AI Workforce - Memory Management System
Pinecone-based vector memory with conversation history
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import pinecone
from pinecone import Pinecone
import openai
from loguru import logger

@dataclass
class MemoryEntry:
    """Structured memory entry for workforce executions"""
    id: str
    timestamp: datetime
    goal: str
    context: Dict[str, Any]
    execution_id: str
    results: Dict[str, Any]
    embeddings: List[float]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class DevlarMemory:
    """
    Memory management system for the Devlar AI workforce.
    Uses Pinecone for vector storage and retrieval of execution history.
    """

    def __init__(self):
        self.setup_pinecone()
        self.setup_embeddings()
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_history_length = 50  # Keep last 50 interactions

    def setup_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            # Initialize Pinecone
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

            # Get or create index
            index_name = os.getenv("PINECONE_INDEX_NAME", "devlar-ai-workforce")

            # Check if index exists
            existing_indexes = pc.list_indexes().names()

            if index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI ada-002 embedding dimension
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-west-2"
                        }
                    }
                )

            self.index = pc.Index(index_name)
            logger.success(f"✅ Connected to Pinecone index: {index_name}")

        except Exception as e:
            logger.error(f"❌ Failed to setup Pinecone: {e}")
            raise

    def setup_embeddings(self):
        """Initialize embedding model"""
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = "text-embedding-ada-002"

    async def store_execution(self, execution_id: str, execution_data: Dict[str, Any]) -> str:
        """
        Store execution results in vector memory

        Args:
            execution_id: Unique execution identifier
            execution_data: Complete execution data including goal, results, etc.

        Returns:
            Memory entry ID
        """
        try:
            # Create searchable text for embedding
            searchable_text = self.create_searchable_text(execution_data)

            # Generate embeddings
            embeddings = await self.generate_embeddings(searchable_text)

            # Create memory entry
            memory_id = f"exec_{execution_id}_{int(datetime.now().timestamp())}"

            memory_entry = MemoryEntry(
                id=memory_id,
                timestamp=datetime.now(),
                goal=execution_data.get("goal", ""),
                context=execution_data.get("context", {}),
                execution_id=execution_id,
                results=execution_data.get("results", {}),
                embeddings=embeddings,
                metadata={
                    "success": execution_data.get("results", {}).get("status") == "completed",
                    "execution_time": execution_data.get("execution_time", 0),
                    "workflow_type": execution_data.get("workflow_plan", {}).get("workflow", ""),
                    "pods_involved": list(execution_data.get("results", {}).keys())
                }
            )

            # Store in Pinecone
            self.index.upsert([{
                "id": memory_id,
                "values": embeddings,
                "metadata": {
                    "goal": memory_entry.goal,
                    "execution_id": execution_id,
                    "timestamp": memory_entry.timestamp.isoformat(),
                    "success": memory_entry.metadata["success"],
                    "execution_time": memory_entry.metadata["execution_time"],
                    "workflow_type": memory_entry.metadata["workflow_type"],
                    "searchable_text": searchable_text[:1000]  # Truncate for metadata
                }
            }])

            logger.info(f"💾 Stored execution memory: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"❌ Failed to store execution memory: {e}")
            raise

    async def retrieve_similar_executions(self, goal: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve similar past executions based on goal similarity

        Args:
            goal: Current goal to find similar executions for
            limit: Maximum number of results to return

        Returns:
            List of similar execution memories
        """
        try:
            # Generate embeddings for the query goal
            query_embeddings = await self.generate_embeddings(goal)

            # Search Pinecone
            results = self.index.query(
                vector=query_embeddings,
                top_k=limit,
                include_metadata=True,
                filter={"success": True}  # Only successful executions
            )

            similar_executions = []
            for match in results.matches:
                similar_executions.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })

            logger.info(f"🔍 Found {len(similar_executions)} similar executions")
            return similar_executions

        except Exception as e:
            logger.error(f"❌ Failed to retrieve similar executions: {e}")
            return []

    async def get_execution_details(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get full execution details by memory ID"""
        try:
            # Query Pinecone for specific ID
            result = self.index.fetch([memory_id])

            if memory_id in result.vectors:
                return result.vectors[memory_id].metadata
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Failed to get execution details: {e}")
            return None

    def add_conversation(self, user_input: str, ai_response: str, execution_id: Optional[str] = None):
        """Add conversation to local history"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_response": ai_response,
            "execution_id": execution_id
        }

        self.conversation_history.append(conversation)

        # Trim history if too long
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]

        logger.debug(f"📝 Added conversation to history (total: {len(self.conversation_history)})")

    def get_conversation_context(self, lookback: int = 5) -> str:
        """Get recent conversation context for AI agents"""
        if not self.conversation_history:
            return "No previous conversation history."

        recent_conversations = self.conversation_history[-lookback:]

        context_parts = []
        for conv in recent_conversations:
            timestamp = conv["timestamp"]
            context_parts.append(f"[{timestamp}] User: {conv['user_input']}")
            context_parts.append(f"[{timestamp}] AI: {conv['ai_response'][:200]}...")

        return "\n".join(context_parts)

    async def analyze_execution_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze execution patterns to improve future performance"""
        try:
            # Query recent successful executions
            cutoff_date = datetime.now() - timedelta(days=days_back)

            # Note: In production, you'd implement proper date filtering in Pinecone
            # For now, we'll get all recent executions and filter locally
            dummy_embeddings = [0.0] * 1536  # Placeholder for pattern analysis query

            results = self.index.query(
                vector=dummy_embeddings,
                top_k=100,
                include_metadata=True,
                filter={"success": True}
            )

            # Analyze patterns
            patterns = {
                "successful_workflows": {},
                "average_execution_time": 0,
                "common_failure_points": [],
                "most_used_pods": {},
                "performance_trends": {}
            }

            execution_times = []
            workflow_counts = {}

            for match in results.matches:
                metadata = match.metadata

                # Track workflow types
                workflow_type = metadata.get("workflow_type", "unknown")
                workflow_counts[workflow_type] = workflow_counts.get(workflow_type, 0) + 1

                # Track execution times
                exec_time = metadata.get("execution_time", 0)
                if exec_time > 0:
                    execution_times.append(exec_time)

            # Calculate analytics
            if execution_times:
                patterns["average_execution_time"] = sum(execution_times) / len(execution_times)

            patterns["successful_workflows"] = workflow_counts

            logger.info("📊 Analyzed execution patterns")
            return patterns

        except Exception as e:
            logger.error(f"❌ Failed to analyze execution patterns: {e}")
            return {}

    def create_searchable_text(self, execution_data: Dict[str, Any]) -> str:
        """Create searchable text from execution data"""
        parts = [
            f"Goal: {execution_data.get('goal', '')}",
            f"Context: {json.dumps(execution_data.get('context', {}), default=str)}",
            f"Workflow: {execution_data.get('workflow_plan', {}).get('workflow', '')}",
            f"Results: {json.dumps(execution_data.get('results', {}), default=str)[:500]}"
        ]

        return " | ".join(parts)

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using OpenAI"""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text.replace("\n", " ")[:8000]  # Limit input size
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536

    async def cleanup_old_memories(self, days_to_keep: int = 90):
        """Clean up old memory entries to manage storage costs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # In production, implement proper date-based cleanup
            # For now, this is a placeholder
            logger.info(f"🧹 Cleanup would remove memories older than {cutoff_date}")

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old memories: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Get memory system status"""
        try:
            # Get index stats
            stats = self.index.describe_index_stats()

            return {
                "index_name": os.getenv("PINECONE_INDEX_NAME", "devlar-ai-workforce"),
                "total_vectors": stats.total_vector_count if hasattr(stats, 'total_vector_count') else 0,
                "dimension": stats.dimension if hasattr(stats, 'dimension') else 1536,
                "conversation_history_length": len(self.conversation_history),
                "status": "connected"
            }

        except Exception as e:
            logger.error(f"❌ Failed to get memory status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }