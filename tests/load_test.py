"""
Load testing with Locust
Run: locust -f tests/load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between

class FraudDetectorUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Set up headers"""
        self.headers = {
            "X-API-Key": "devtoken",
            "Content-Type": "application/json"
        }
    
    @task(3)
    def predict_review(self):
        """Test review prediction"""
        payload = {
            "user_id": 1,
            "product_id": "PROD-123",
            "review_text": "Great product!",
            "rating": 5,
            "ip_address": "192.168.1.1",
            "device_fingerprint": "test123"
        }
        self.client.post("/predict/review", json=payload, headers=self.headers)
    
    @task(2)
    def predict_transaction(self):
        """Test transaction prediction"""
        payload = {
            "user_id": 1,
            "amount": 1000.00,
            "currency": "INR",
            "channel": "web",
            "ip_address": "192.168.1.1",
            "device_fingerprint": "test456"
        }
        self.client.post("/predict/transaction", json=payload, headers=self.headers)
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")