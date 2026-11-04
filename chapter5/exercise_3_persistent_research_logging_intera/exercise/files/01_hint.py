#!/usr/bin/env python3
# -*- coding coding: utf-8 -*-

import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Database Setup and Model Definition
DATABASE_URL = "sqlite:///agent_runs.db"
Engine = create_engine(DATABASE_URL)
Base = declarative_base()

class ResearchLog(Base):
    """SQLAlchemy model for logging agent research runs."""
    __tablename__ = 'research_logs'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    query_topic = Column(String, index=True, nullable=False)
    agent_role = Column(String, nullable=False)
    summary_snippet = Column(Text)

# Create tables in the database (if they don't exist)
Base.metadata.create_all(bind=Engine)

# Create a Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# 2. Persistence Logic (To be integrated as the final task in the agent's workflow)
def persist_research_log(topic: str, role: str, full_report: str):
    """
    Handles the transactional persistence of the agent's research results.
    """
    db = SessionLocal()
    try:
        # Take the first 500 characters of the report for the summary snippet
        snippet = full_report[:500] + "..." if len(full_report) > 500 else full_report

        new_log = ResearchLog(
            query_topic=topic,
            agent_role=role,
            summary_snippet=snippet
        )

        db.add(new_log)
        # CRITICAL: Commit the transaction to persist changes
        db.commit()
        print(f"[{datetime.datetime.now()}] Successfully logged research run for topic: {topic}")

    except Exception as e:
        db.rollback()
        print(f"Database error during logging: {e}")
    finally:
        db.close()

# 3. Verification Script Example (Separate file logic)
def verify_logs():
    """Connects and queries the database to verify persistence."""
    db = SessionLocal()
    try:
        print("\n--- Verifying Last 5 Agent Runs ---")
        recent_logs = db.query(ResearchLog).order_by(ResearchLog.timestamp.desc()).limit(5).all()
        if not recent_logs:
            print("No logs found.")
            return

        for i, log in enumerate(recent_logs):
            print(f"Log {i+1}:")
            print(f"  ID: {log.id}, Time: {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Topic: {log.query_topic}")
            print(f"  Role: {log.agent_role}")
            print(f"  Snippet Length: {len(log.summary_snippet.strip())}")
            print("-" * 20)
    finally:
        db.close()

# Note: In the final solution, the agent execution script would call 
# persist_research_log(agent_input, agent_role, final_output)
# after the research is complete.
