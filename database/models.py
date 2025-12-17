"""Database models for users and settings"""

from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.db import Base


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class UserSettings(Base):
    """User settings model"""
    __tablename__ = 'user_settings'
    
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    prayer_reminders = Column(Boolean, default=False, nullable=False)
    morning_adkar = Column(Boolean, default=False, nullable=False)
    evening_adkar = Column(Boolean, default=False, nullable=False)
    sleep_adkar = Column(Boolean, default=False, nullable=False)
    allahu_allah_interval = Column(Integer, nullable=True)  # 2, 4, 6 hours or NULL
    city = Column(String(255), default='Singapore', nullable=False)
    country = Column(String(255), default='Singapore', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, prayer_reminders={self.prayer_reminders})>"
