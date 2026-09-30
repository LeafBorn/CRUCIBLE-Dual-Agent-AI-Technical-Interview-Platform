import os
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base, engine
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class UserProfile(Base):
    __tablename__ = "user_profile"
    id             = Column(Integer, primary_key=True, index=True)
    username       = Column(String, ForeignKey("users.username"), unique=True)
    target_role    = Column(String, default="")
    resume_skill   = Column(String, default="[]")
    matching_skill = Column(String, default="[]")
    missing_skill  = Column(String, default="[]")
    score          = Column(Integer, default=0)

class UserHistory(Base):
    __tablename__ = "user_history"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, ForeignKey("users.username"), index=True)
    score         = Column(Integer)
    accuracy      = Column(Float)
    blunder       = Column(Integer)
    confidence    = Column(String)
    streak        = Column(Integer)
    communication = Column(String)
    turns_data    = Column(String, default="[]")
    breaking_points = Column(String, default="[]")
    avg_confidence = Column(Float, default=0.0)
    peak_difficulty = Column(Float, default=0.0)
    created_at    = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

def init_db():
    Base.metadata.create_all(bind=engine)
    # Lightweight column migration for existing SQLite databases
    import sqlite3
    from database import DB_PATH
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(user_history)")
            existing_cols = [row[1] for row in cur.fetchall()]
            new_cols = {
                "turns_data": "TEXT DEFAULT '[]'",
                "breaking_points": "TEXT DEFAULT '[]'",
                "avg_confidence": "REAL DEFAULT 0.0",
                "peak_difficulty": "REAL DEFAULT 0.0"
            }
            for col_name, col_type in new_cols.items():
                if col_name not in existing_cols:
                    cur.execute(f"ALTER TABLE user_history ADD COLUMN {col_name} {col_type}")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[init_db migration notice]: {e}")