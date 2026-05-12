"""
CyberSentric Database Connections
MongoDB (logs, events) + PostgreSQL (structured data)
"""
import asyncio
from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings


# ─── MongoDB Connection ───────────────────────────────────────────────────────

class MongoDB:
    """MongoDB connection manager for event logs and unstructured data."""

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls):
        """Initialize MongoDB connection."""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        cls.db = cls.client[settings.MONGODB_DB_NAME]

        # Create indexes for performance
        await cls.db.threat_logs.create_index([("timestamp", -1)])
        await cls.db.threat_logs.create_index([("severity", 1)])
        await cls.db.agent_events.create_index([("timestamp", -1)])
        await cls.db.agent_events.create_index([("agent_name", 1)])
        await cls.db.action_history.create_index([("timestamp", -1)])
        await cls.db.system_metrics.create_index([("timestamp", -1)])

        print("[DB] MongoDB connected successfully")

    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            print("[DB] MongoDB disconnected")

    @classmethod
    async def insert_threat_log(cls, log_data: dict) -> str:
        """Insert a threat log entry."""
        log_data["timestamp"] = datetime.utcnow()
        result = await cls.db.threat_logs.insert_one(log_data)
        return str(result.inserted_id)

    @classmethod
    async def insert_agent_event(cls, event_data: dict) -> str:
        """Insert an agent event."""
        event_data["timestamp"] = datetime.utcnow()
        result = await cls.db.agent_events.insert_one(event_data)
        return str(result.inserted_id)

    @classmethod
    async def insert_action(cls, action_data: dict) -> str:
        """Insert an action history entry."""
        action_data["timestamp"] = datetime.utcnow()
        result = await cls.db.action_history.insert_one(action_data)
        return str(result.inserted_id)

    @classmethod
    async def get_recent_threats(cls, limit: int = 50) -> list:
        """Get recent threat logs."""
        cursor = cls.db.threat_logs.find().sort("timestamp", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    @classmethod
    async def get_recent_events(cls, limit: int = 50) -> list:
        """Get recent agent events."""
        cursor = cls.db.agent_events.find().sort("timestamp", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    @classmethod
    async def get_action_history(cls, limit: int = 50) -> list:
        """Get recent action history."""
        cursor = cls.db.action_history.find().sort("timestamp", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    @classmethod
    async def get_threat_stats(cls) -> dict:
        """Get aggregated threat statistics."""
        pipeline = [
            {
                "$group": {
                    "_id": "$severity",
                    "count": {"$sum": 1},
                }
            }
        ]
        stats = {}
        async for doc in cls.db.threat_logs.aggregate(pipeline):
            stats[doc["_id"]] = doc["count"]
        return stats

    @classmethod
    async def get_attack_type_stats(cls) -> list:
        """Get attack type distribution."""
        pipeline = [
            {"$group": {"_id": "$threat_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10},
        ]
        results = []
        async for doc in cls.db.threat_logs.aggregate(pipeline):
            results.append({"type": doc["_id"], "count": doc["count"]})
        return results

    @classmethod
    async def get_threat_timeline(cls, hours: int = 24) -> list:
        """Get threat frequency over time."""
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": datetime.utcnow().replace(
                            hour=datetime.utcnow().hour - min(hours, datetime.utcnow().hour)
                        )
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d %H:00",
                            "date": "$timestamp",
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]
        results = []
        async for doc in cls.db.threat_logs.aggregate(pipeline):
            results.append({"time": doc["_id"], "threats": doc["count"]})
        return results

    @classmethod
    async def insert_system_metric(cls, metric_data: dict) -> str:
        """Insert a system metric entry."""
        metric_data["timestamp"] = datetime.utcnow()
        result = await cls.db.system_metrics.insert_one(metric_data)
        return str(result.inserted_id)


# ─── In-Memory Fallback Store ─────────────────────────────────────────────────
# Used when MongoDB/PostgreSQL are not available (development mode)

class InMemoryStore:
    """In-memory data store for development without databases."""

    _threats: list = []
    _events: list = []
    _actions: list = []
    _metrics: list = []
    _users: dict = {}
    _counter: int = 0

    @classmethod
    def _next_id(cls) -> str:
        cls._counter += 1
        return f"mem_{cls._counter}"

    @classmethod
    async def insert_threat_log(cls, log_data: dict) -> str:
        log_data["timestamp"] = datetime.utcnow().isoformat()
        log_data["_id"] = cls._next_id()
        cls._threats.insert(0, log_data)
        cls._threats = cls._threats[:500]  # Keep last 500
        return log_data["_id"]

    @classmethod
    async def insert_agent_event(cls, event_data: dict) -> str:
        event_data["timestamp"] = datetime.utcnow().isoformat()
        event_data["_id"] = cls._next_id()
        cls._events.insert(0, event_data)
        cls._events = cls._events[:500]
        return event_data["_id"]

    @classmethod
    async def insert_action(cls, action_data: dict) -> str:
        action_data["timestamp"] = datetime.utcnow().isoformat()
        action_data["_id"] = cls._next_id()
        cls._actions.insert(0, action_data)
        cls._actions = cls._actions[:500]
        return action_data["_id"]

    @classmethod
    async def get_recent_threats(cls, limit: int = 50) -> list:
        return cls._threats[:limit]

    @classmethod
    async def get_recent_events(cls, limit: int = 50) -> list:
        return cls._events[:limit]

    @classmethod
    async def get_action_history(cls, limit: int = 50) -> list:
        return cls._actions[:limit]

    @classmethod
    async def get_threat_stats(cls) -> dict:
        stats = {}
        for t in cls._threats:
            sev = t.get("severity", "unknown")
            stats[sev] = stats.get(sev, 0) + 1
        return stats

    @classmethod
    async def get_attack_type_stats(cls) -> list:
        type_counts = {}
        for t in cls._threats:
            tt = t.get("threat_type", "unknown")
            type_counts[tt] = type_counts.get(tt, 0) + 1
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"type": k, "count": v} for k, v in sorted_types[:10]]

    @classmethod
    async def get_threat_timeline(cls, hours: int = 24) -> list:
        from collections import defaultdict
        timeline = defaultdict(int)
        for t in cls._threats:
            ts = t.get("timestamp", "")
            if isinstance(ts, str) and len(ts) >= 13:
                hour_key = ts[:13] + ":00"
                timeline[hour_key] += 1
        sorted_tl = sorted(timeline.items())
        return [{"time": k, "threats": v} for k, v in sorted_tl[-hours:]]

    @classmethod
    async def insert_system_metric(cls, metric_data: dict) -> str:
        metric_data["timestamp"] = datetime.utcnow().isoformat()
        metric_data["_id"] = cls._next_id()
        cls._metrics.insert(0, metric_data)
        cls._metrics = cls._metrics[:200]
        return metric_data["_id"]


# ─── Database Selector ────────────────────────────────────────────────────────

_db_instance = None


async def get_db():
    """Get the active database instance. Falls back to in-memory if MongoDB unavailable."""
    global _db_instance
    if _db_instance is not None:
        return _db_instance

    try:
        await MongoDB.connect()
        _db_instance = MongoDB
        return _db_instance
    except Exception as e:
        print(f"[DB] MongoDB unavailable ({e}), using in-memory store")
        _db_instance = InMemoryStore
        return _db_instance


async def close_db():
    """Close database connections."""
    global _db_instance
    if _db_instance is MongoDB:
        await MongoDB.disconnect()
    _db_instance = None
