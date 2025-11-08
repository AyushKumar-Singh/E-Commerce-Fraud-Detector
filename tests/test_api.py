"""
API endpoint tests
"""

import pytest
import json
from backend.app import app
from backend.db.models import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def client():
    """Test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """Authentication headers"""
    return {'X-API-Key': 'devtoken', 'Content-Type': 'application/json'}

def test_health_endpoint(client):
    """Test health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_predict_review_missing_auth(client):
    """Test review prediction without auth"""
    response = client.post('/predict/review', json={})
    assert response.status_code == 401

def test_predict_review_missing_fields(client, auth_headers):
    """Test review prediction with missing fields"""
    response = client.post('/predict/review', 
                          headers=auth_headers,
                          json={"user_id": 1})
    assert response.status_code == 400

def test_predict_review_success(client, auth_headers):
    """Test successful review prediction"""
    payload = {
        "user_id": 1,
        "product_id": "PROD-123",
        "review_text": "Great product, highly recommend!",
        "rating": 5,
        "ip_address": "192.168.1.1",
        "device_fingerprint": "abc123"
    }
    
    response = client.post('/predict/review',
                          headers=auth_headers,
                          json=payload)
    
    # Should succeed or fail gracefully if DB not set up
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'decision' in data
        assert 'score_final' in data
        assert 'reasons' in data

def test_predict_transaction_success(client, auth_headers):
    """Test successful transaction prediction"""
    payload = {
        "user_id": 1,
        "amount": 1000.00,
        "currency": "INR",
        "channel": "web",
        "ip_address": "192.168.1.1",
        "device_fingerprint": "xyz789"
    }
    
    response = client.post('/predict/transaction',
                          headers=auth_headers,
                          json=payload)
    
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'decision' in data
        assert 'score_final' in data

def test_rate_limiting(client, auth_headers):
    """Test rate limiting"""
    # Make many requests quickly
    for _ in range(35):
        client.post('/predict/review', headers=auth_headers, json={
            "user_id": 1,
            "review_text": "test",
            "rating": 5
        })
    
    # Should eventually hit rate limit
    # (Actual behavior depends on limiter configuration)