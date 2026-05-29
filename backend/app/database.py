"""
CyberSentric Database Connections
PostgreSQL / SQLite (Persistent Storage)
"""
import asyncio
from datetime import datetime, timedelta
import json
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, select, desc, func
import bcrypt

from app.config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")
    created = Column(DateTime, default=datetime.utcnow)

class ThreatLog(Base):
    __tablename__ = "threat_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    threat_type = Column(String, index=True)
    severity = Column(String, index=True)
    data_json = Column(String) # Store the whole dict for easy retrieval

class AgentEvent(Base):
    __tablename__ = "agent_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    agent_name = Column(String, index=True)
    data_json = Column(String)

class ActionHistory(Base):
    __tablename__ = "action_history"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    data_json = Column(String)

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    data_json = Column(String)

class Database:
    """Persistent SQLAlchemy database manager."""
    engine = None
    async_session = None

    @classmethod
    async def connect(cls):
        # We use SQLite for out-of-the-box persistent storage. 
        # PostgreSQL can be used by changing the URL in settings.
        db_url = "sqlite+aiosqlite:///cybersentric.db"
        cls.engine = create_async_engine(db_url, echo=False)
        cls.async_session = sessionmaker(cls.engine, class_=AsyncSession, expire_on_commit=False)
        
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # Initialize default users
        async with cls.async_session() as session:
            result = await session.execute(select(User).where(User.username == "admin"))
            if not result.scalars().first():
                def hash_pw(pw): return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                session.add(User(username="admin", password=hash_pw("admin123"), role="admin"))
                session.add(User(username="user", password=hash_pw("user123"), role="user"))
                await session.commit()
                
        print("[DB] Database connected successfully")

    @classmethod
    async def disconnect(cls):
        if cls.engine:
            await cls.engine.dispose()
            print("[DB] Database disconnected")

    @classmethod
    async def get_user(cls, username: str) -> Optional[dict]:
        async with cls.async_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalars().first()
            if user:
                return {"username": user.username, "password": user.password, "role": user.role}
            return None

    @classmethod
    async def create_user(cls, username: str, password_hash: str, role: str) -> bool:
        async with cls.async_session() as session:
            result = await session.execute(select(User).where(User.username == username))
            if result.scalars().first():
                return False
            session.add(User(username=username, password=password_hash, role=role))
            await session.commit()
            return True

    @classmethod
    async def insert_threat_log(cls, log_data: dict) -> str:
        log_data["timestamp"] = datetime.utcnow().isoformat()
        async with cls.async_session() as session:
            log = ThreatLog(
                timestamp=datetime.utcnow(),
                threat_type=log_data.get("threat_type", "unknown"),
                severity=log_data.get("severity", "unknown"),
                data_json=json.dumps(log_data)
            )
            session.add(log)
            await session.commit()
            return str(log.id)

    @classmethod
    async def insert_agent_event(cls, event_data: dict) -> str:
        event_data["timestamp"] = datetime.utcnow().isoformat()
        async with cls.async_session() as session:
            evt = AgentEvent(
                timestamp=datetime.utcnow(),
                agent_name=event_data.get("agent_name", "unknown"),
                data_json=json.dumps(event_data)
            )
            session.add(evt)
            await session.commit()
            return str(evt.id)

    @classmethod
    async def insert_action(cls, action_data: dict) -> str:
        action_data["timestamp"] = datetime.utcnow().isoformat()
        async with cls.async_session() as session:
            act = ActionHistory(
                timestamp=datetime.utcnow(),
                data_json=json.dumps(action_data)
            )
            session.add(act)
            await session.commit()
            return str(act.id)

    @classmethod
    async def get_recent_threats(cls, limit: int = 50) -> list:
        async with cls.async_session() as session:
            result = await session.execute(select(ThreatLog).order_by(desc(ThreatLog.timestamp)).limit(limit))
            return [json.loads(row.data_json) for row in result.scalars()]

    @classmethod
    async def get_recent_events(cls, limit: int = 50) -> list:
        async with cls.async_session() as session:
            result = await session.execute(select(AgentEvent).order_by(desc(AgentEvent.timestamp)).limit(limit))
            return [json.loads(row.data_json) for row in result.scalars()]

    @classmethod
    async def get_action_history(cls, limit: int = 50) -> list:
        async with cls.async_session() as session:
            result = await session.execute(select(ActionHistory).order_by(desc(ActionHistory.timestamp)).limit(limit))
            return [json.loads(row.data_json) for row in result.scalars()]

    @classmethod
    async def get_threat_stats(cls) -> dict:
        stats = {}
        async with cls.async_session() as session:
            result = await session.execute(select(ThreatLog.severity, func.count(ThreatLog.id)).group_by(ThreatLog.severity))
            for row in result:
                stats[row[0]] = row[1]
        return stats

    @classmethod
    async def get_attack_type_stats(cls) -> list:
        async with cls.async_session() as session:
            result = await session.execute(
                select(ThreatLog.threat_type, func.count(ThreatLog.id))
                .group_by(ThreatLog.threat_type)
                .order_by(desc(func.count(ThreatLog.id)))
                .limit(10)
            )
            return [{"type": row[0], "count": row[1]} for row in result]

    @classmethod
    async def get_threat_timeline(cls, hours: int = 24) -> list:
        from collections import defaultdict
        timeline = defaultdict(int)
        time_limit = datetime.utcnow() - timedelta(hours=hours)
        async with cls.async_session() as session:
            result = await session.execute(select(ThreatLog.timestamp).where(ThreatLog.timestamp >= time_limit))
            for row in result.scalars():
                hour_key = row.strftime("%Y-%m-%d %H:00")
                timeline[hour_key] += 1
        sorted_tl = sorted(timeline.items())
        return [{"time": k, "threats": v} for k, v in sorted_tl[-hours:]]

    @classmethod
    async def insert_system_metric(cls, metric_data: dict) -> str:
        metric_data["timestamp"] = datetime.utcnow().isoformat()
        async with cls.async_session() as session:
            metric = SystemMetric(
                timestamp=datetime.utcnow(),
                data_json=json.dumps(metric_data)
            )
            session.add(metric)
            await session.commit()
            return str(metric.id)

_db_instance = None

async def get_db():
    global _db_instance
    if _db_instance is not None:
        return _db_instance
    await Database.connect()
    _db_instance = Database
    return _db_instance

async def close_db():
    global _db_instance
    if _db_instance:
        await _db_instance.disconnect()
    _db_instance = None
