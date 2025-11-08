"""
Transaction feature engineering pipeline
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import Transaction, User

def engineer_tx_features(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Engineer features for a single transaction
    
    Args:
        payload: Raw transaction data
        db: Database session
    
    Returns:
        Dictionary of engineered features
    """
    features = {}
    
    # ==================== BASIC FEATURES ====================
    features["amount"] = float(payload.get("amount", 0))
    features["currency"] = payload.get("currency", "INR")
    features["channel"] = payload.get("channel", "web")
    
    user_id = payload.get("user_id")
    now = datetime.utcnow()
    
    # ==================== TEMPORAL FEATURES ====================
    hour = now.hour
    features["hour_of_day"] = hour
    features["is_night_time"] = 1 if (hour >= 0 and hour < 6) or (hour >= 22) else 0
    features["is_weekend"] = 1 if now.weekday() >= 5 else 0
    
    # ==================== USER HISTORY ====================
    if user_id:
        # Account age
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.created_at:
            features["account_age_days"] = (now - user.created_at).days
        else:
            features["account_age_days"] = 0
        
        # Historical transaction stats
        user_txs = db.query(Transaction.amount).filter(
            Transaction.user_id == user_id,
            Transaction.created_at < now
        ).all()
        
        if user_txs:
            amounts = [float(tx.amount) for tx in user_txs]
            features["user_total_txs"] = len(amounts)
            features["user_avg_amount"] = sum(amounts) / len(amounts)
            features["user_max_amount"] = max(amounts)
            features["user_min_amount"] = min(amounts)
            features["user_std_amount"] = pd.Series(amounts).std() if len(amounts) > 1 else 0
            
            # Z-score of current amount
            if features["user_std_amount"] > 0:
                features["amount_z"] = (features["amount"] - features["user_avg_amount"]) / features["user_std_amount"]
            else:
                features["amount_z"] = 0
        else:
            features["user_total_txs"] = 0
            features["user_avg_amount"] = 0
            features["user_max_amount"] = 0
            features["user_min_amount"] = 0
            features["user_std_amount"] = 0
            features["amount_z"] = 0
        
        # ==================== VELOCITY FEATURES ====================
        # Transactions in last 1 hour
        features["user_1h_tx"] = db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= now - timedelta(hours=1)
        ).scalar() or 0
        
        # Transactions in last 24 hours
        features["user_24h_tx"] = db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= now - timedelta(hours=24)
        ).scalar() or 0
        
        # Transactions in last 7 days
        features["user_7d_tx"] = db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= now - timedelta(days=7)
        ).scalar() or 0
        
        # Amount velocity (sum in last 24h)
        sum_24h = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= now - timedelta(hours=24)
        ).scalar() or 0
        features["user_24h_amount"] = float(sum_24h)
        
    else:
        features["account_age_days"] = 0
        features["user_total_txs"] = 0
        features["user_avg_amount"] = 0
        features["user_max_amount"] = 0
        features["user_min_amount"] = 0
        features["user_std_amount"] = 0
        features["amount_z"] = 0
        features["user_1h_tx"] = 0
        features["user_24h_tx"] = 0
        features["user_7d_tx"] = 0
        features["user_24h_amount"] = 0
    
    # ==================== IP/DEVICE FEATURES ====================
    ip = payload.get("ip_address")
    device = payload.get("device_fingerprint")
    
    if ip:
        # Transactions from this IP in last 1 hour
        features["ip_1h_tx"] = db.query(func.count(Transaction.id)).filter(
            Transaction.ip_address == ip,
            Transaction.created_at >= now - timedelta(hours=1)
        ).scalar() or 0
        
        # Unique users from this IP
        features["ip_unique_users"] = db.query(func.count(func.distinct(Transaction.user_id))).filter(
            Transaction.ip_address == ip
        ).scalar() or 0
    else:
        features["ip_1h_tx"] = 0
        features["ip_unique_users"] = 0
    
    if device and user_id:
        # Device switches in last 7 days
        unique_devices = db.query(func.count(func.distinct(Transaction.device_fingerprint))).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= now - timedelta(days=7)
        ).scalar() or 1
        features["dev_switch_7d"] = unique_devices - 1  # subtract current device
    else:
        features["dev_switch_7d"] = 0
    
    # ==================== ROLLING STATISTICS ====================
    if user_id and features["user_total_txs"] > 3:
        # Get last 10 transactions
        recent_txs = db.query(Transaction.amount).filter(
            Transaction.user_id == user_id,
            Transaction.created_at < now
        ).order_by(Transaction.created_at.desc()).limit(10).all()
        
        if recent_txs:
            recent_amounts = [float(tx.amount) for tx in recent_txs]
            rolling_mean = sum(recent_amounts) / len(recent_amounts)
            features["rolling_mean_diff"] = features["amount"] - rolling_mean
            features["rolling_std"] = pd.Series(recent_amounts).std() if len(recent_amounts) > 1 else 0
        else:
            features["rolling_mean_diff"] = 0
            features["rolling_std"] = 0
    else:
        features["rolling_mean_diff"] = 0
        features["rolling_std"] = 0
    
    # ==================== CHANNEL FEATURES ====================
    channel = payload.get("channel", "web")
    if user_id:
        # User's most common channel
        channel_counts = db.query(
            Transaction.channel, func.count(Transaction.id)
        ).filter(
            Transaction.user_id == user_id
        ).group_by(Transaction.channel).all()
        
        if channel_counts:
            most_common_channel = max(channel_counts, key=lambda x: x[1])[0]
            features["channel_mismatch"] = 1 if channel != most_common_channel else 0
            features["channel_freq"] = dict(channel_counts).get(channel, 0)
        else:
            features["channel_mismatch"] = 0
            features["channel_freq"] = 0
    else:
        features["channel_mismatch"] = 0
        features["channel_freq"] = 0
    
    # ==================== GEO FEATURES (placeholder) ====================
    # In production, use IP geolocation service
    features["country_mismatch"] = 0  # implement with GeoIP lookup
    
    return features

def batch_engineer_transactions(df: pd.DataFrame, db: Session) -> pd.DataFrame:
    """
    Engineer features for a batch of transactions (for training)
    """
    features_list = []
    
    for _, row in df.iterrows():
        payload = row.to_dict()
        features = engineer_tx_features(payload, db)
        features_list.append(features)
    
    return pd.DataFrame(features_list)