"""Database models for users and settings"""

from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.sql import func
from database.db import Base
import enum


class DonationType(enum.Enum):
    """Donation type enumeration"""
    AMAL_JARIAH = "amal_jariah"
    HADIAH = "hadiah"
    CLASS_FEES = "class_fees"
    DAWAH = "dawah"
    ORPHAN_SPONSORSHIP = "orphan_sponsorship"
    GENERAL = "general"


class DonationFrequency(enum.Enum):
    """Donation frequency for standing instructions"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


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
    friday_khutbah = Column(Boolean, default=True, nullable=False)  # Receive Friday Khutbah
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, prayer_reminders={self.prayer_reminders})>"


class Donation(Base):
    """Donation records"""
    __tablename__ = 'donations'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    donation_type = Column(SQLEnum(DonationType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_reference = Column(String(255), nullable=True)
    notes = Column(String(500), nullable=True)
    donated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Donation(id={self.id}, user_id={self.user_id}, amount={self.amount})>"


class StandingInstruction(Base):
    """Standing instructions for recurring donations"""
    __tablename__ = 'standing_instructions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    donation_type = Column(SQLEnum(DonationType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    frequency = Column(SQLEnum(DonationFrequency), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    next_donation_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<StandingInstruction(id={self.id}, user_id={self.user_id}, frequency={self.frequency})>"
