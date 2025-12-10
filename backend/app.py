"""
E-Commerce Fraud Detector - Main API
Production-ready Flask application with fraud detection endpoints
"""

import os
import sys
import json
import joblib
import logging
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from db.models import Base, Review, Transaction, User, get_session
from utils.auth import require_token, create_token
from utils.xai import assemble_decision
from utils.logging_conf import setup_logging
from rules.rule_engine import review_rules, tx_rules
from pipelines.review_pipeline import engineer_review_features
from pipelines.tx_pipeline import engineer_tx_features

# Load environment from root .env (parent directory of backend)
import pathlib
root_env = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(root_env)

# Initialize Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max payload

# Enable CORS for frontend
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "https://yourdomain.com",  # CHANGE: Add your production domain
            "https://www.yourdomain.com"  # CHANGE: Add www version if needed
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-Key", "Authorization"]
    }
})

# Setup logging
logger = setup_logging()

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Get absolute paths - THIS IS THE KEY FIX
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Model configuration
REVIEW_THR = float(os.getenv("REVIEW_THR", "0.65"))
TX_THR = float(os.getenv("TX_THR", "0.50"))

# Log the actual paths being used
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Model directory: {MODEL_DIR}")
logger.info(f"Current working directory: {os.getcwd()}")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/frauddb")

try:
    engine, SessionLocal = get_session(DATABASE_URL)
    SessionLocal = scoped_session(SessionLocal)
    logger.info("Database connection established successfully")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    raise

# Load ML models with proper error handling
review_model = None
tx_model = None
tx_features = []

# CatBoost model for Kaggle Credit Card Fraud Detection
catboost_model = None
catboost_scaler = None
catboost_features = []
catboost_metrics = {}

def load_models():
    """Load ML models with proper path resolution and error handling"""
    global review_model, tx_model, tx_features
    global catboost_model, catboost_scaler, catboost_features, catboost_metrics
    
    review_model_path = os.path.join(MODEL_DIR, "review_model.pkl")
    tx_model_path = os.path.join(MODEL_DIR, "tx_model.pkl")
    catboost_model_path = os.path.join(MODEL_DIR, "catboost_model.pkl")
    catboost_metrics_path = os.path.join(MODEL_DIR, "catboost_metrics.json")
    
    try:
        # Check if model directory exists
        if not os.path.exists(MODEL_DIR):
            logger.error(f"Model directory does not exist: {MODEL_DIR}")
            logger.info("Please ensure models are in the correct location")
            return False
        
        # List all files in model directory
        logger.info(f"Files in model directory: {os.listdir(MODEL_DIR)}")
        
        # Load review model
        if os.path.exists(review_model_path):
            review_model = joblib.load(review_model_path)
            logger.info(f"Review model loaded successfully from: {review_model_path}")
        else:
            logger.warning(f"Review model not found at: {review_model_path}")
        
        # Load transaction model (Isolation Forest - legacy)
        if os.path.exists(tx_model_path):
            tx_artifact = joblib.load(tx_model_path)
            tx_model = tx_artifact["pipe"]
            tx_features = tx_artifact["features"]
            logger.info(f"Transaction model loaded successfully from: {tx_model_path}")
        else:
            logger.warning(f"Transaction model not found at: {tx_model_path}")
        
        # Load CatBoost model (Kaggle Credit Card Fraud Detection)
        if os.path.exists(catboost_model_path):
            catboost_artifact = joblib.load(catboost_model_path)
            catboost_model = catboost_artifact["model"]
            catboost_scaler = catboost_artifact["scaler"]
            catboost_features = catboost_artifact["features"]
            logger.info(f"CatBoost model loaded successfully from: {catboost_model_path}")
            
            # Load metrics if available
            if os.path.exists(catboost_metrics_path):
                with open(catboost_metrics_path, 'r') as f:
                    catboost_metrics = json.load(f)
                logger.info(f"CatBoost metrics loaded: {catboost_metrics.get('accuracy', 'N/A')}% accuracy")
        else:
            logger.warning(f"CatBoost model not found at: {catboost_model_path}")
        
        if review_model is not None and (tx_model is not None or catboost_model is not None):
            logger.info("All models loaded successfully")
            return True
        else:
            logger.warning("Some models failed to load")
            return False
            
    except Exception as e:
        logger.error(f"Model loading failed: {e}", exc_info=True)
        return False

# Load models on startup
models_loaded = load_models()

# Register blueprints
from dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

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
        "models_loaded": {
            "review_model": review_model is not None,
            "tx_model": tx_model is not None,
            "catboost_model": catboost_model is not None
        },
        "catboost_metrics": catboost_metrics if catboost_model else None,
        "database": "connected"
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
            return jsonify({"error": "Review model not loaded"}), 503
        
        # Convert features dict to DataFrame (sklearn Pipeline expects DataFrame)
        import pandas as pd
        features_df = pd.DataFrame([features])
        proba = float(review_model.predict_proba(features_df)[0, 1])
        
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
        db = get_db()
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
            return jsonify({"error": "Transaction model not loaded"}), 503
        
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
        db = get_db()
        db.rollback()
        return jsonify({"error": "Internal server error"}), 500

@app.route("/predict/transaction-kaggle", methods=["POST"])
@limiter.limit("30 per minute")
@require_token
def predict_transaction_kaggle():
    """
    Predict if a transaction is fraudulent using CatBoost model
    Trained on Kaggle Credit Card Fraud Detection dataset
    
    Expected payload:
    {
        "Time": 0,
        "V1": -1.35, "V2": -0.07, ... "V28": 0.01,
        "Amount": 149.62
    }
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        payload = request.get_json()
        
        # Check if CatBoost model is loaded
        if catboost_model is None:
            return jsonify({"error": "CatBoost model not loaded"}), 503
        
        # Validate required fields
        required_pca = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
        missing = [f for f in required_pca if f not in payload]
        
        # If missing PCA features, provide defaults (zeros)
        if missing:
            logger.warning(f"Missing features, using defaults: {missing}")
            for f in missing:
                payload[f] = 0.0
        
        # Prepare features
        import numpy as np
        features = np.array([[payload.get(f, 0.0) for f in catboost_features]])
        
        # Scale Time and Amount
        if catboost_scaler:
            features[:, [0, 29]] = catboost_scaler.transform(features[:, [0, 29]])
        
        # Model prediction
        proba = float(catboost_model.predict_proba(features)[0, 1])
        is_fraud = proba >= TX_THR
        
        # Determine risk level
        if proba >= 0.8:
            confidence = "HIGH"
            risk_level = "critical"
        elif proba >= 0.5:
            confidence = "MEDIUM"
            risk_level = "high"
        elif proba >= 0.3:
            confidence = "LOW"
            risk_level = "medium"
        else:
            confidence = "VERY_LOW"
            risk_level = "low"
        
        # Get top contributing features
        reasons = []
        feature_importances = catboost_model.get_feature_importance()
        top_features = sorted(
            zip(catboost_features, feature_importances, [payload.get(f, 0) for f in catboost_features]),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for name, importance, value in top_features:
            if abs(value) > 1.5:  # Anomalous value
                reasons.append(f"{name} anomaly")
        
        if proba >= TX_THR:
            if len(reasons) == 0:
                reasons = ["Pattern matches fraud signature"]
        
        decision = {
            "decision": is_fraud,
            "score_final": round(proba, 4),
            "score_model": round(proba, 4),
            "confidence": confidence,
            "risk_level": risk_level,
            "reasons": reasons,
            "model": "CatBoostClassifier",
            "dataset": "Kaggle Credit Card Fraud Detection"
        }
        
        # Store in database
        db = get_db()
        transaction = Transaction(
            user_id=payload.get("user_id", 0),
            amount=payload.get("Amount", 0),
            currency="USD",
            channel="kaggle_test",
            ip_address=payload.get("ip_address"),
            device_fingerprint=payload.get("device_fingerprint"),
            is_fraud_pred=is_fraud,
            fraud_score=proba,
            decision_json=decision
        )
        db.add(transaction)
        db.commit()
        
        logger.info(f"CatBoost prediction: Amount={payload.get('Amount', 0)}, score={proba:.3f}, fraud={is_fraud}")
        
        return jsonify({
            "transaction_id": transaction.id,
            **decision
        }), 200
        
    except Exception as e:
        logger.error(f"CatBoost prediction error: {e}", exc_info=True)
        db = get_db()
        db.rollback()
        return jsonify({"error": "Internal server error"}), 500

@app.route("/")
def home():
    """Root endpoint"""
    return jsonify({
        "status": "Fraud Detector API is running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "auth": "/auth/token",
            "review_prediction": "/predict/review",
            "transaction_prediction": "/predict/transaction"
        }
    }), 200

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
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    logger.info("=" * 60)
    logger.info("Starting Fraud Detector API...")
    logger.info(f"Models loaded: {models_loaded}")
    logger.info(f"Database: Connected")
    logger.info(f"Listening on: http://0.0.0.0:8000")
    logger.info("=" * 60)
    
    app.run(
        host="0.0.0.0", 
        port=8000, 
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )