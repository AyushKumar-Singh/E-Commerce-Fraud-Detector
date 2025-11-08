"""
SQLAlchemy ORM models for fraud detection system
"""

from sqlalchemy import (
    Column, Integer, BigInteger, Text, Boolean, 
    Numeric, TIMESTAMP, ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, INET
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(Text, unique=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    reviews = relationship("Review", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class Review(Base):
    """Review model with fraud detection metadata"""
    __tablename__ = "reviews"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Text, index=True)
    review_text = Column(Text, nullable=False)
    rating = Column(Numeric)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    ip_address = Column(INET)
    device_fingerprint = Column(Text, index=True)
    
    # Fraud detection fields
    is_fake_pred = Column(Boolean, index=True)
    fake_score = Column(Numeric)
    decision_json = Column(JSONB)
    
    user = relationship("User", back_populates="reviews")

class Transaction(Base):
    """Transaction model with fraud detection metadata"""
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric, nullable=False)
    currency = Column(Text, default='INR')
    device_fingerprint = Column(Text, index=True)
    ip_address = Column(INET)
    channel = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    # Fraud detection fields
    is_fraud_pred = Column(Boolean, index=True)
    fraud_score = Column(Numeric)
    decision_json = Column(JSONB)
    
    user = relationship("User", back_populates="transactions")

class Label(Base):
    """Human labels for feedback loop"""
    __tablename__ = "labels"
    
    id = Column(BigInteger, primary_key=True)
    entity_type = Column(Text, nullable=False)
    entity_id = Column(BigInteger, nullable=False, index=True)
    is_fraud = Column(Boolean, nullable=False)
    notes = Column(Text)
    labeled_by = Column(Text)
    labeled_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("entity_type IN ('review', 'transaction')", name='valid_entity_type'),
    )