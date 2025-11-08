"""
E-Commerce Fraud Detector - Main API
Production-ready Flask application with fraud detection endpoints
"""

import os
import json
import joblib
import logging
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from db.models import Base, Review, Transaction, User
from utils.auth import require_token, create_token
from utils.xai import assemble_decision
from utils.logging_conf import setup_logging
from rules.rule_engine import review_rules, tx_rules
from pipelines.review_pipeline import engineer_review_features
from pipelines.tx_pipeline import engineer_tx_features

# Load environment
load_dotenv()

# Initialize Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max payload

# Setup logging
logger = setup_logging()

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/frauddb")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

# Model configuration
REVIEW_THR = float(os.getenv("REVIEW_THR", "0.65"))
TX_THR = float(os.getenv("TX_THR", "0.50"))
MODEL_PATH = os.getenv("MODEL_PATH", "backend/models")

# Load ML models
try:
    review_model = joblib.load(f"{MODEL_PATH}/review_model.pkl")
    tx_artifact = joblib.load(f"{MODEL_PATH}/tx_model.pkl")
    tx_model = tx_artifact["pipe"]
    tx_features = tx_artifact["features"]
    logger.info("✅ Models loaded successfully")
except Exception as e:
    logger.error(f"❌ Model loading failed: {e}")
    review_model = None
    tx_model = None
    tx_features = []

# ==================== DATABASE HELPERS ====================

def get_db():
    """Get database session for request"""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database session after request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ==================== HEALTH & AUTH ====================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models_loaded": review_model is not None and tx_model is not None
    }), 200

@app.route("/auth/token", methods=["POST"])
@limiter.limit("5 per minute")
def get_token():
    """Generate API token (for demo - use proper OAuth in production)"""
    data = request.get_json()
    if not data or data.get("secret") != os.getenv("ADMIN_SECRET", "change_me"):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = create_token({"user": "admin"})
    return jsonify({"token": token}), 200

# ==================== PREDICTION ENDPOINTS ====================

@app.route("/predict/review", methods=["POST"])
@limiter.limit("30 per minute")
@require_token
def predict_review():
    """
    Predict if a review is fake
    
    Expected payload:
    {
        "user_id": 123,
        "product_id": "PROD-456",
        "review_text": "Amazing product! Best ever!!!",
        "rating": 5,
        "ip_address": "192.168.1.1",
        "device_fingerprint": "abc123"
    }
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        payload = request.get_json()
        
        # Validate required fields
        required = ["user_id", "review_text", "rating"]
        missing = [f for f in required if f not in payload]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400
        
        db = get_db()
        
        # Engineer features
        features = engineer_review_features(payload, db)
        
        # Model prediction
        if review_model is None:
            return jsonify({"error": "Model not loaded"}), 503
        
        proba = float(review_model.predict_proba([features])[0, 1])
        
        # Apply business rules
        boost, reasons = review_rules(features)
        
        # Assemble decision
        decision = assemble_decision(proba, REVIEW_THR, boost, reasons)
        
        # Store in database
        review = Review(
            user_id=payload["user_id"],
            product_id=payload.get("product_id"),
            review_text=payload["review_text"],
            rating=payload["rating"],
            ip_address=payload.get("ip_address"),
            device_fingerprint=payload.get("device_fingerprint"),
            is_fake_pred=decision["decision"],
            fake_score=decision["score_final"],
            decision_json=decision
        )
        db.add(review)
        db.commit()
        
        logger.info(f"Review prediction: user={payload['user_id']}, score={decision['score_final']:.3f}, fake={decision['decision']}")
        
        return jsonify({
            "review_id": review.id,
            **decision
        }), 200
        
    except Exception as e:
        logger.error(f"Review prediction error: {e}", exc_info=True)
        db.rollback()
        return jsonify({"error": "Internal server error"}), 500

@app.route("/predict/transaction", methods=["POST"])
@limiter.limit("30 per minute")
@require_token
def predict_transaction():
    """
    Predict if a transaction is fraudulent
    
    Expected payload:
    {
        "user_id": 123,
        "amount": 5000.00,
        "currency": "INR",
        "channel": "web",
        "ip_address": "192.168.1.1",
        "device_fingerprint": "xyz789"
    }
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        payload = request.get_json()
        
        # Validate required fields
        required = ["user_id", "amount"]
        missing = [f for f in required if f not in payload]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400
        
        db = get_db()
        
        # Engineer features
        features = engineer_tx_features(payload, db)
        
        # Model prediction (Isolation Forest returns anomaly scores)
        if tx_model is None:
            return jsonify({"error": "Model not loaded"}), 503
        
        X = [[features.get(f, 0) for f in tx_features]]
        anomaly_score = float(-tx_model.score_samples(X)[0])
        
        # Convert to pseudo-probability (0-1 scale)
        import math
        pseudo_prob = 1 / (1 + math.exp(-(anomaly_score - 0.5) * 5))
        
        # Apply business rules
        boost, reasons = tx_rules(features)
        
        # Assemble decision
        decision = assemble_decision(pseudo_prob, TX_THR, boost, reasons)
        
        # Store in database
        transaction = Transaction(
            user_id=payload["user_id"],
            amount=payload["amount"],
            currency=payload.get("currency", "INR"),
            channel=payload.get("channel"),
            ip_address=payload.get("ip_address"),
            device_fingerprint=payload.get("device_fingerprint"),
            is_fraud_pred=decision["decision"],
            fraud_score=decision["score_final"],
            decision_json=decision
        )
        db.add(transaction)
        db.commit()
        
        logger.info(f"Transaction prediction: user={payload['user_id']}, amount={payload['amount']}, score={decision['score_final']:.3f}, fraud={decision['decision']}")
        
        return jsonify({
            "transaction_id": transaction.id,
            **decision
        }), 200
        
    except Exception as e:
        logger.error(f"Transaction prediction error: {e}", exc_info=True)
        db.rollback()
        return jsonify({"error": "Internal server error"}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded", "message": str(e.description)}), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "Payload too large"}), 413

# ==================== STARTUP ====================

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("🚀 Starting Fraud Detector API...")
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")