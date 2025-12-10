"""
Seed test data for demo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.models import get_session, User, Base
from dotenv import load_dotenv
import pathlib

# Load env from parent directory
root_env = pathlib.Path(__file__).parent.parent / ".env"
load_dotenv(root_env)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/fraud_detector_db")
print(f"Database URL: {DATABASE_URL[:50]}...")

engine, SessionLocal = get_session(DATABASE_URL)
db = SessionLocal()

try:
    # Create test user
    user = db.query(User).filter(User.id == 12345).first()
    if not user:
        user = User(id=12345, email="testuser@example.com")
        db.add(user)
        db.commit()
        print("✅ Test user 12345 created successfully!")
    else:
        print("✅ User 12345 already exists")
    
    # List all users
    all_users = db.query(User).all()
    print(f"\n📋 All users ({len(all_users)}):")
    for u in all_users[:5]:
        print(f"  - ID: {u.id}, Email: {u.email}")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
