import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="developer", nullable=False)  # "developer" or "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    runs = relationship("AgentRun", back_populates="user")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(100), index=True, nullable=False)
    ticket_title = Column(String(255), nullable=False)
    ticket_type = Column(String(50), default="Bug")  # "Bug" or "Feature"
    status = Column(String(50), default="pending")  # "pending", "running", "completed", "failed"
    branch_name = Column(String(100), nullable=True)
    commit_hash = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    test_output = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="runs")
    logs = relationship("AgentActivityLog", back_populates="run", cascade="all, delete-orphan")


class AgentActivityLog(Base):
    __tablename__ = "agent_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    step = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")  # "pending", "running", "success", "failed"
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    run = relationship("AgentRun", back_populates="logs")


class ProjectConfig(Base):
    __tablename__ = "project_config"

    id = Column(Integer, primary_key=True, index=True)
    openproject_url = Column(String(255), nullable=False)
    openproject_api_key = Column(String(255), nullable=True)
    target_repo_path = Column(String(500), nullable=False)
    is_mock_mode = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
