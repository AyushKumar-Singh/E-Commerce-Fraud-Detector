"""
Feature engineering tests
"""

import pytest
import pandas as pd
from backend.pipelines.review_pipeline import engineer_review_features
from backend.pipelines.tx_pipeline import engineer_tx_features

def test_review_text_features():
    """Test text feature extraction"""
    from unittest.mock import MagicMock
    
    payload = {
        "review_text": "AMAZING!!! Best product EVER!!!",
        "rating": 5,
        "user_id": 1
    }
    
    db = MagicMock()
    db.query().filter().scalar.return_value = None
    
    features = engineer_review_features(payload, db)
    
    assert features["text_len"] == len(payload["review_text"])
    assert features["upper_ratio"] > 0.3  # Lots of uppercase
    assert features["exclaim_ratio"] > 0  # Has exclamation marks

def test_review_edge_cases():
    """Test edge cases in review features"""
    from unittest.mock import MagicMock
    
    # Empty text
    payload = {"review_text": "", "rating": 3, "user_id": 1}
    db = MagicMock()
    db.query().filter().scalar.return_value = None
    
    features = engineer_review_features(payload, db)
    assert features["text_len"] == 0
    assert features["upper_ratio"] == 0

def test_transaction_features():
    """Test transaction feature extraction"""
    from unittest.mock import MagicMock
    
    payload = {
        "user_id": 1,
        "amount": 5000.00,
        "currency": "INR",
        "channel": "web"
    }
    
    db = MagicMock()
    db.query().filter().all.return_value = []
    db.query().filter().scalar.return_value = 0
    
    features = engineer_tx_features(payload, db)
    
    assert features["amount"] == 5000.00
    assert "hour_of_day" in features
    assert "account_age_days" in features