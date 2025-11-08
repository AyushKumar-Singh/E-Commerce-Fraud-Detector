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
    
    # ==================== PRESERVE ORIGINAL TEXT (CRITICAL!) ====================
    features["review_text"] = str(payload.get("review_text", ""))
    
    # ==================== TEXT FEATURES ====================
    text = str(payload.get("review_text", ""))
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
    features["repeated_chars"] = len(re.findall(r'(.)\1{2,}', text))
    
    # ==================== RATING FEATURES ====================
    features["rating"] = float(payload.get("rating", 3))
    
    # User's historical average rating
    user_id = payload.get("user_id")
    if user_id:
        user_avg = db.query(func.avg(Review.rating)).filter(
            Review.user_id == user_id,
            Review.id != payload.get("review_id")
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
        features["user_30d_review_count"] = db.query(func.count(Review.id)).filter(
            Review.user_id == user_id,
            Review.created_at >= now - timedelta(days=30)
        ).scalar() or 0
        
        features["user_7d_review_count"] = db.query(func.count(Review.id)).filter(
            Review.user_id == user_id,
            Review.created_at >= now - timedelta(days=7)
        ).scalar() or 0
        
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
        features["ip_30d_review_count"] = db.query(func.count(Review.id)).filter(
            Review.ip_address == ip,
            Review.created_at >= now - timedelta(days=30)
        ).scalar() or 0
        
        features["ip_unique_users"] = db.query(func.count(func.distinct(Review.user_id))).filter(
            Review.ip_address == ip
        ).scalar() or 0
    else:
        features["ip_30d_review_count"] = 0
        features["ip_unique_users"] = 0
    
    if device:
        features["device_review_count"] = db.query(func.count(Review.id)).filter(
            Review.device_fingerprint == device
        ).scalar() or 0
        
        features["device_unique_users"] = db.query(func.count(func.distinct(Review.user_id))).filter(
            Review.device_fingerprint == device
        ).scalar() or 0
    else:
        features["device_review_count"] = 0
        features["device_unique_users"] = 0
    
    # ==================== PRODUCT FEATURES ====================
    product_id = payload.get("product_id")
    if product_id:
        features["product_review_count"] = db.query(func.count(Review.id)).filter(
            Review.product_id == product_id
        ).scalar() or 0
        
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
        DataFrame with engineered features INCLUDING original review_text
    """
    print(f"   Processing {len(df):,} reviews for feature engineering...")
    
    features_list = []
    
    for idx, row in df.iterrows():
        if idx % 1000 == 0:
            print(f"   ... {idx:,}/{len(df):,}")
        
        payload = row.to_dict()
        features = engineer_review_features(payload, db)
        
        # DOUBLE CHECK: Ensure review_text is present
        if 'review_text' not in features or not features['review_text']:
            features['review_text'] = str(payload.get('review_text', ''))
        
        # Preserve the label if it exists
        if 'label_is_fake' in payload:
            features['label_is_fake'] = payload['label_is_fake']
        
        features_list.append(features)
    
    result_df = pd.DataFrame(features_list)
    
    # Verify review_text is present
    if 'review_text' not in result_df.columns:
        raise ValueError("ERROR: review_text column missing after feature engineering!")
    
    # Check if review_text is empty
    empty_count = (result_df['review_text'].str.len() == 0).sum()
    if empty_count > len(result_df) * 0.5:
        raise ValueError(f"ERROR: {empty_count:,} reviews have empty text!")
    
    # Reorder columns: review_text first
    cols = ['review_text'] + [c for c in result_df.columns if c != 'review_text' and c != 'label_is_fake']
    if 'label_is_fake' in result_df.columns:
        cols.append('label_is_fake')
    result_df = result_df[cols]
    
    # Ensure label is integer
    if 'label_is_fake' in result_df.columns:
        result_df['label_is_fake'] = result_df['label_is_fake'].astype(int)
    
    print(f"   ✅ Feature engineering complete: {result_df.shape[1]} features")
    print(f"   ✅ Review text preserved: avg length = {result_df['review_text'].str.len().mean():.1f}")
    
    return result_df