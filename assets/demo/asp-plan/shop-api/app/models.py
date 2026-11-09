"""SQLAlchemy models for the shop API (PostgreSQL 15, ~40 million users)."""
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(320), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
