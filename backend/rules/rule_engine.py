"""
Business rules engine for hybrid AI + rule-based fraud detection
"""

from typing import Dict, List, Tuple

def review_rules(features: Dict) -> Tuple[float, List[str]]:
    """
    Apply business rules to review features
    
    Args:
        features: Engineered feature dictionary
    
    Returns:
        (score_boost, reasons) tuple
    """
    boost = 0.0
    reasons = []
    
    # Rule 1: IP burst (too many reviews from same IP)
    if features.get("ip_30d_review_count", 0) > 50:
        reasons.append("⚠️ Suspicious IP activity (50+ reviews in 30 days)")
        boost += 0.15
    
    # Rule 2: New account, high activity
    if features.get("account_age_days", 999) < 7 and features.get("user_30d_review_count", 0) > 5:
        reasons.append("⚠️ New account with unusual activity")
        boost += 0.20
    
    # Rule 3: Excessive uppercase (shouting)
    if features.get("upper_ratio", 0) > 0.4:
        reasons.append("⚠️ Excessive uppercase usage")
        boost += 0.05
    
    # Rule 4: Very short or very long review
    text_len = features.get("text_len", 50)
    if text_len < 10:
        reasons.append("⚠️ Suspiciously short review")
        boost += 0.10
    elif text_len > 1000:
        reasons.append("⚠️ Unusually long review")
        boost += 0.05
    
    # Rule 5: Extreme rating with low engagement text
    if features.get("rating", 3) in [1, 5] and text_len < 20:
        reasons.append("⚠️ Extreme rating with minimal text")
        boost += 0.10
    
    # Rule 6: Rating deviation (user's rating far from their average)
    if abs(features.get("rating_deviation", 0)) > 2.5:
        reasons.append("⚠️ Rating inconsistent with user history")
        boost += 0.08
    
    # Rule 7: Device fingerprint reuse
    if features.get("device_review_count", 0) > 100:
        reasons.append("⚠️ Device used for 100+ reviews")
        boost += 0.12
    
    return boost, reasons

def tx_rules(features: Dict) -> Tuple[float, List[str]]:
    """
    Apply business rules to transaction features
    
    Args:
        features: Engineered feature dictionary
    
    Returns:
        (score_boost, reasons) tuple
    """
    boost = 0.0
    reasons = []
    
    # Rule 1: Very high amount
    amount = features.get("amount", 0)
    if amount > 50000:
        reasons.append("⚠️ High-value transaction (>50,000)")
        boost += 0.25
    elif amount > 20000:
        reasons.append("⚠️ Elevated transaction amount (>20,000)")
        boost += 0.10
    
    # Rule 2: Velocity spike (too many transactions in short time)
    if features.get("user_1h_tx", 0) > 5:
        reasons.append("⚠️ High transaction velocity (5+ in 1 hour)")
        boost += 0.20
    
    # Rule 3: Frequent device switching
    if features.get("dev_switch_7d", 0) > 5:
        reasons.append("⚠️ Frequent device changes (5+ in 7 days)")
        boost += 0.15
    
    # Rule 4: Geographic mismatch
    if features.get("country_mismatch", 0) == 1:
        reasons.append("⚠️ Transaction from unusual location")
        boost += 0.15
    
    # Rule 5: Unusual amount pattern (z-score)
    if abs(features.get("amount_z", 0)) > 3:
        reasons.append("⚠️ Amount significantly deviates from user pattern")
        boost += 0.12
    
    # Rule 6: Night-time transaction (assuming feature exists)
    if features.get("is_night_time", 0) == 1 and amount > 10000:
        reasons.append("⚠️ Large transaction during unusual hours")
        boost += 0.08
    
    # Rule 7: New user, large transaction
    if features.get("account_age_days", 999) < 30 and amount > 15000:
        reasons.append("⚠️ New account with large transaction")
        boost += 0.18
    
    # Rule 8: IP burst
    if features.get("ip_1h_tx", 0) > 10:
        reasons.append("⚠️ Multiple transactions from same IP")
        boost += 0.10
    
    return boost, reasons