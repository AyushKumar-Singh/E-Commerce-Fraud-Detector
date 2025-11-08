"""
Review feature engineering pipeline
Transforms raw review data into ML-ready features
"""

import re
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import Review, User

def engineer_review_features(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Engineer features for a single review
    
    Args:
        payload: Raw review data
        db: Database session
    
    Returns:
        Dictionary of engineered features
    """
    features = {}
    
    # ==================== TEXT FEATURES ====================
    text = payload.get("review_text", "")
    features["review_text"] = text
    features["text_len"] = len(text)
    features["word_count"] = len(text.split())
    
    # Character ratios
    if len(text) > 0:
        features["upper_ratio"] = sum(1 for c in text if c.isupper()) / len(text)
        features["digit_ratio"] = sum(1 for c in text if c.isdigit()) / len(text)
        features["punct_ratio"] = sum(1 for c in text if c in '.,!?;:') / len(text)
        features["exclaim_ratio"] = text.count('!') / len(text)
        features["question_ratio"] = text.count('?') / len(text)
    else:
        features["upper_ratio"] = 0
        features["digit_ratio"] = 0
        features["punct_ratio"] = 0
        features["exclaim_ratio"] = 0
        features["question_ratio"] = 0
    
    # Word statistics
    words = text.split()
    if words:
        features["avg_word_len"] = sum(len(w) for w in words) / len(words)
        features["unique_word_ratio"] = len(set(words)) / len(words)
    else:
        features["avg_word_len"] = 0
        features["unique_word_ratio"] = 0
    
    # Special patterns
    features["has_url"] = 1 if re.search(r'http[s]?://|www\.', text, re.I) else 0
    features["has_email"] = 1 if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text) else 0
    features["repeated_chars"] = len(re.findall(r'(.)\1{2,}', text))  # e.g., "sooo goood"
    
    # ==================== RATING FEATURES ====================
    features["rating"] = float(payload.get("rating", 3))
    
    # User's historical average rating
    user_id = payload.get("user_id")
    if user_id:
        user_avg = db.query(func.avg(Review.rating)).filter(
            Review.user_id == user_id,
            Review.id != payload.get("review_id")  # exclude current review
        ).scalar()
        
        if user_avg:
            features["rating_deviation"] = abs(features["rating"] - float(user_avg))
            features["user_avg_rating"] = float(user_avg)
        else:
            features["rating_deviation"] = 0
            features["user_avg_rating"] = features["rating"]
    else:
        features["rating_deviation"] = 0
        features["user_avg_rating"] = features["rating"]
    
    # ==================== TEMPORAL FEATURES ====================
    now = datetime.utcnow()
    
    # Account age
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.created_at:
            features["account_age_days"] = (now - user.created_at).days
        else:
            features["account_age_days"] = 0
    else:
        features["account_age_days"] = 0
    
    # ==================== BEHAVIORAL FEATURES ====================
    if user_id:
        # Reviews in last 30 days
        features["user_30d_review_count"] = db.query(func.count(Review.id)).filter(
            Review.user_id == user_id,
            Review.created_at >= now - timedelta(days=30)
        ).scalar() or 0
        
        # Reviews in last 7 days
        features["user_7d_review_count"] = db.query(func.count(Review.id)).filter(
            Review.user_id == user_id,
            Review.created_at >= now - timedelta(days=7)
        ).scalar() or 0
        
        # Reviews in last 1 hour
        features["user_1h_review_count"] = db.query(func.count(Review.id)).filter(
            Review.user_id == user_id,
            Review.created_at >= now - timedelta(hours=1)
        ).scalar() or 0
    else:
        features["user_30d_review_count"] = 0
        features["user_7d_review_count"] = 0
        features["user_1h_review_count"] = 0
    
    # ==================== IP/DEVICE FEATURES ====================
    ip = payload.get("ip_address")
    device = payload.get("device_fingerprint")
    
    if ip:
        # Reviews from this IP in last 30 days
        features["ip_30d_review_count"] = db.query(func.count(Review.id)).filter(
            Review.ip_address == ip,
            Review.created_at >= now - timedelta(days=30)
        ).scalar() or 0
        
        # Unique users from this IP
        features["ip_unique_users"] = db.query(func.count(func.distinct(Review.user_id))).filter(
            Review.ip_address == ip
        ).scalar() or 0
    else:
        features["ip_30d_review_count"] = 0
        features["ip_unique_users"] = 0
    
    if device:
        # Reviews from this device
        features["device_review_count"] = db.query(func.count(Review.id)).filter(
            Review.device_fingerprint == device
        ).scalar() or 0
        
        # Unique users from this device
        features["device_unique_users"] = db.query(func.count(func.distinct(Review.user_id))).filter(
            Review.device_fingerprint == device
        ).scalar() or 0
    else:
        features["device_review_count"] = 0
        features["device_unique_users"] = 0
    
    # ==================== PRODUCT FEATURES ====================
    product_id = payload.get("product_id")
    if product_id:
        # Total reviews for this product
        features["product_review_count"] = db.query(func.count(Review.id)).filter(
            Review.product_id == product_id
        ).scalar() or 0
        
        # Average rating for this product
        product_avg = db.query(func.avg(Review.rating)).filter(
            Review.product_id == product_id
        ).scalar()
        features["product_avg_rating"] = float(product_avg) if product_avg else 3.0
    else:
        features["product_review_count"] = 0
        features["product_avg_rating"] = 3.0
    
    return features

def batch_engineer_reviews(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    """
    Engineer features for a batch of reviews (for training)
    
    Args:
        df: DataFrame with raw review data
        db: Database session
    
    Returns:
        DataFrame with engineered features
    """
    features_list = []
    
    for _, row in df.iterrows():
        payload = row.to_dict()
        features = engineer_review_features(payload, db)
        features_list.append(features)
    
    return pd.DataFrame(features_list)