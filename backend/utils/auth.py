"""
Authentication and authorization utilities
"""

import os
import jwt
import time
from functools import wraps
from flask import request, jsonify, g

JWT_SECRET = os.getenv("JWT_SECRET", "change_me_in_production")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600 * 24  # 24 hours

API_TOKEN = os.getenv("API_TOKEN", "devtoken")

def create_token(payload: dict) -> str:
    """Create JWT token"""
    payload["exp"] = time.time() + JWT_EXP_DELTA_SECONDS
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def require_token(f):
    """Decorator to require API token or JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check API key
        api_key = request.headers.get("X-API-Key")
        if api_key == API_TOKEN:
            g.auth_method = "api_key"
            return f(*args, **kwargs)
        
        # Check JWT
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                g.user = payload
                g.auth_method = "jwt"
                return f(*args, **kwargs)
            except ValueError as e:
                return jsonify({"error": str(e)}), 401
        
        return jsonify({"error": "Unauthorized - provide X-API-Key or Authorization header"}), 401
    
    return decorated