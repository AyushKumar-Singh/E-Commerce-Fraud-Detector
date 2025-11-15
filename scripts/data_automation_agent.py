"""
Complete Data Engineering Automation Agent - FIXED VERSION
Handles NumPy types and correct file paths
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from dotenv import load_dotenv
from sqlalchemy import inspect
from sqlalchemy.exc import ProgrammingError, IntegrityError

from db.models import Base, User, Review, Transaction, get_session
from pipelines.review_pipeline import batch_engineer_reviews
from pipelines.tx_pipeline import batch_engineer_transactions

# Load environment
load_dotenv(PROJECT_ROOT / ".env")

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def convert_to_python_types(value):
    """Convert NumPy types to native Python types"""
    if pd.isna(value):
        return None
    elif isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    else:
        return value


class FraudDetectionAutomationAgent:
    """Complete automation for fraud detection pipeline"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("❌ DATABASE_URL not found in .env file!")
        
        self.engine, self.SessionFactory = get_session(self.db_url)
        self.stats = {
            'tables_created': 0,
            'csv_generated': 0,
            'users_created': 0,
            'reviews_inserted': 0,
            'transactions_inserted': 0,
            'features_engineered': 0,
            'errors': []
        }
    
    def log(self, emoji, message, level='info'):
        """Structured logging"""
        msg = f"{emoji} {message}"
        print(msg)
        if level == 'info':
            logger.info(message)
        elif level == 'error':
            logger.error(message)
            self.stats['errors'].append(message)
    
    # ==================== PHASE 1: SCHEMA VALIDATION ====================
    
    def phase1_validate_schema(self):
        """Validate and create database schema"""
        self.log("🔍", "=" * 70)
        self.log("🔍", "PHASE 1: SCHEMA VALIDATION")
        self.log("🔍", "=" * 70)
        
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            self.log("📋", f"Existing tables: {existing_tables}")
            
            required_tables = ['users', 'reviews', 'transactions', 'labels']
            missing = [t for t in required_tables if t not in existing_tables]
            
            if missing:
                self.log("⚙️", f"Creating missing tables: {missing}")
                Base.metadata.create_all(self.engine)
                
                # Verify
                inspector = inspect(self.engine)
                created = inspector.get_table_names()
                
                for table in missing:
                    if table in created:
                        self.log("✅", f"Table created: {table}")
                        self.stats['tables_created'] += 1
                    else:
                        self.log("❌", f"Failed to create: {table}", 'error')
                        return False
            else:
                self.log("✅", "All required tables exist")
            
            # Verify reviews table structure
            if 'reviews' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('reviews')]
                required_cols = ['id', 'user_id', 'review_text', 'rating', 'created_at']
                missing_cols = [c for c in required_cols if c not in columns]
                
                if missing_cols:
                    self.log("❌", f"Reviews table missing columns: {missing_cols}", 'error')
                    self.log("💡", "Recommendation: Drop and recreate the table")
                    return False
                
                self.log("✅", "Reviews table schema validated")
            
            return True
            
        except Exception as e:
            self.log("❌", f"Schema validation failed: {e}", 'error')
            return False
    
    # ==================== PHASE 2: DATA GENERATION ====================
    
    def phase2_generate_data(self, n_reviews=5000, n_transactions=10000):
        """Generate sample CSV data"""
        self.log("📝", "=" * 70)
        self.log("📝", "PHASE 2: DATA GENERATION")
        self.log("📝", "=" * 70)
        
        try:
            # Import generation functions
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from generate_sample_data import generate_reviews, generate_transactions
            
            self.log("⚙️", f"Generating {n_reviews:,} reviews...")
            reviews_df = generate_reviews(n_reviews)
            self.stats['csv_generated'] += len(reviews_df)
            
            self.log("⚙️", f"Generating {n_transactions:,} transactions...")
            transactions_df = generate_transactions(n_transactions)
            self.stats['csv_generated'] += len(transactions_df)
            
            # FIXED PATHS - Use scripts/data/raw/
            reviews_path = PROJECT_ROOT / "scripts" / "data" / "raw" / "reviews.csv"
            tx_path = PROJECT_ROOT / "scripts" / "data" / "raw" / "transactions.csv"
            
            if not reviews_path.exists():
                self.log("❌", f"Reviews CSV not found: {reviews_path}", 'error')
                return False
            
            if not tx_path.exists():
                self.log("❌", f"Transactions CSV not found: {tx_path}", 'error')
                return False
            
            self.log("✅", f"CSV files generated at: {reviews_path.parent}")
            return True
            
        except Exception as e:
            self.log("❌", f"Data generation failed: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False
    
    # ==================== PHASE 3: DATABASE INGESTION ====================
    
    def validate_csv(self, csv_path, required_cols):
        """Validate CSV structure"""
        try:
            if not csv_path.exists():
                self.log("❌", f"CSV not found: {csv_path}", 'error')
                self.log("💡", f"Searched at: {csv_path.absolute()}")
                return None
            
            df = pd.read_csv(csv_path)
            self.log("📂", f"Loaded: {csv_path.name} ({len(df):,} rows)")
            
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                self.log("❌", f"Missing columns: {missing}", 'error')
                self.log("📋", f"Available columns: {list(df.columns)}")
                return None
            
            self.log("✅", f"CSV validated")
            return df
            
        except Exception as e:
            self.log("❌", f"CSV validation failed: {e}", 'error')
            return None
    
    def clean_data(self, df):
        """Clean and normalize data + convert NumPy types"""
        initial = len(df)
        
        # Convert types and handle NumPy
        if 'review_text' in df.columns:
            df['review_text'] = df['review_text'].fillna('').astype(str).str.strip()
            df = df[df['review_text'].str.len() > 0]
        
        if 'user_id' in df.columns:
            # Convert to native Python int (not NumPy)
            df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce')
            df = df.dropna(subset=['user_id'])
            df['user_id'] = df['user_id'].astype('int64')  # Pandas int
        
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]
            df['rating'] = df['rating'].astype('float64')  # Pandas float
        
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df[df['amount'] > 0]
            df['amount'] = df['amount'].astype('float64')
        
        # Handle timestamps
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        df = df.drop_duplicates()
        
        removed = initial - len(df)
        self.log("🧹", f"Cleaned: {len(df):,} rows kept, {removed:,} removed")
        
        return df
    
    def create_all_users(self, user_ids):
        """Pre-create ALL users before inserting reviews/transactions"""
        session = self.SessionFactory()
        try:
            unique_users = sorted(set(user_ids))
            self.log("👥", f"Pre-creating {len(unique_users):,} users...")
            
            created = 0
            batch_size = 500
            
            for i, user_id in enumerate(unique_users):
                # Convert to Python int
                uid = int(user_id)
                
                # Check if exists
                existing = session.query(User).filter(User.id == uid).first()
                if not existing:
                    user = User(
                        id=uid,
                        email=f"user{uid}@example.com"
                    )
                    session.add(user)
                    created += 1
                
                # Batch commit
                if (i + 1) % batch_size == 0:
                    session.commit()
                    self.log("⏳", f"Created {created:,} users...")
            
            session.commit()
            self.stats['users_created'] = created
            self.log("✅", f"Users created: {created:,} new, {len(unique_users) - created:,} existing")
            return True
            
        except Exception as e:
            session.rollback()
            self.log("❌", f"User creation failed: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
    
    def phase3_ingest_data(self):
        """Ingest CSV data into PostgreSQL"""
        self.log("💾", "=" * 70)
        self.log("💾", "PHASE 3: DATABASE INGESTION")
        self.log("💾", "=" * 70)
        
        # FIXED PATH - Use scripts/data/raw/
        reviews_path = PROJECT_ROOT / "scripts" / "data" / "raw" / "reviews.csv"
        tx_path = PROJECT_ROOT / "scripts" / "data" / "raw" / "transactions.csv"
        
        # === VALIDATE CSVs ===
        df_reviews = self.validate_csv(reviews_path, ['user_id', 'review_text', 'rating'])
        if df_reviews is None:
            return False
        
        df_tx = self.validate_csv(tx_path, ['user_id', 'amount'])
        if df_tx is None:
            return False
        
        # === CLEAN DATA ===
        df_reviews = self.clean_data(df_reviews)
        df_tx = self.clean_data(df_tx)
        
        # === PRE-CREATE ALL USERS (CRITICAL!) ===
        all_user_ids = set(df_reviews['user_id'].unique()) | set(df_tx['user_id'].unique())
        if not self.create_all_users(all_user_ids):
            return False
        
        # === INGEST REVIEWS ===
        self.log("📚", "Ingesting reviews...")
        
        session = self.SessionFactory()
        try:
            inserted = 0
            batch_size = 500
            
            for idx, row in df_reviews.iterrows():
                # Convert ALL values to native Python types
                review = Review(
                    user_id=int(row['user_id']),  # Python int
                    product_id=str(row.get('product_id', 'UNKNOWN')),
                    review_text=str(row['review_text']),
                    rating=float(row['rating']),  # Python float
                    ip_address=str(row.get('ip_address', '')) if pd.notna(row.get('ip_address')) else None,
                    device_fingerprint=str(row.get('device_fingerprint', '')) if pd.notna(row.get('device_fingerprint')) else None,
                    created_at=row.get('created_at') if pd.notna(row.get('created_at')) else None
                )
                session.add(review)
                inserted += 1
                
                if inserted % batch_size == 0:
                    session.commit()
                    self.log("⏳", f"Inserted {inserted:,} reviews...")
            
            session.commit()
            self.stats['reviews_inserted'] = inserted
            
            total = session.query(Review).count()
            self.log("✅", f"Reviews inserted: {inserted:,}")
            self.log("📊", f"Total in database: {total:,}")
            
        except IntegrityError as e:
            session.rollback()
            self.log("❌", f"Integrity error: {e}", 'error')
            self.log("💡", "Likely cause: User foreign key violation")
            return False
        except Exception as e:
            session.rollback()
            self.log("❌", f"Review insertion failed: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
        
        # === INGEST TRANSACTIONS ===
        self.log("💳", "Ingesting transactions...")
        
        session = self.SessionFactory()
        try:
            inserted = 0
            batch_size = 500
            
            for idx, row in df_tx.iterrows():
                # Convert ALL values to native Python types
                tx = Transaction(
                    user_id=int(row['user_id']),  # Python int
                    amount=float(row['amount']),  # Python float
                    currency=str(row.get('currency', 'INR')),
                    channel=str(row.get('channel', 'web')),
                    ip_address=str(row.get('ip_address', '')) if pd.notna(row.get('ip_address')) else None,
                    device_fingerprint=str(row.get('device_fingerprint', '')) if pd.notna(row.get('device_fingerprint')) else None,
                    created_at=row.get('created_at') if pd.notna(row.get('created_at')) else None
                )
                session.add(tx)
                inserted += 1
                
                if inserted % batch_size == 0:
                    session.commit()
                    self.log("⏳", f"Inserted {inserted:,} transactions...")
            
            session.commit()
            self.stats['transactions_inserted'] = inserted
            
            total = session.query(Transaction).count()
            self.log("✅", f"Transactions inserted: {inserted:,}")
            self.log("📊", f"Total in database: {total:,}")
            
        except Exception as e:
            session.rollback()
            self.log("❌", f"Transaction insertion failed: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
        
        return True
    
    # ==================== PHASE 4: FEATURE ENGINEERING ====================
    
    def phase4_prepare_data(self):
        """Run feature engineering pipeline"""
        self.log("⚙️", "=" * 70)
        self.log("⚙️", "PHASE 4: FEATURE ENGINEERING")
        self.log("⚙️", "=" * 70)
        
        session = self.SessionFactory()
        
        try:
            # FIXED PATH - Use scripts/data/raw/
            reviews_path = PROJECT_ROOT / "scripts" / "data" / "raw" / "reviews.csv"
            tx_path = PROJECT_ROOT / "scripts" / "data" / "raw" / "transactions.csv"
            
            # === PREPARE REVIEWS ===
            self.log("📊", "Preparing review features...")
            
            if not reviews_path.exists():
                self.log("❌", f"Reviews CSV not found: {reviews_path}", 'error')
                return False
            
            df_reviews = pd.read_csv(reviews_path)
            
            self.log("⚙️", f"Engineering features for {len(df_reviews):,} reviews...")
            df_features = batch_engineer_reviews(df_reviews, session)
            
            # Save to data/processed (not scripts/data/processed)
            output_path = PROJECT_ROOT / "data" / "processed" / "reviews_train.parquet"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_features.to_parquet(output_path, index=False)
            
            self.stats['features_engineered'] += len(df_features)
            self.log("✅", f"Saved {len(df_features):,} processed reviews")
            self.log("📈", f"Features: {df_features.shape[1]}")
            self.log("💾", f"Output: {output_path}")
            
            # Verify text preserved
            if 'review_text' not in df_features.columns:
                self.log("❌", "review_text missing from features!", 'error')
                return False
            
            avg_len = df_features['review_text'].str.len().mean()
            self.log("✅", f"Text preserved: avg length = {avg_len:.1f} chars")
            
            # === PREPARE TRANSACTIONS ===
            self.log("📊", "Preparing transaction features...")
            
            if not tx_path.exists():
                self.log("❌", f"Transactions CSV not found: {tx_path}", 'error')
                return False
            
            df_tx = pd.read_csv(tx_path)
            
            self.log("⚙️", f"Engineering features for {len(df_tx):,} transactions...")
            df_tx_features = batch_engineer_transactions(df_tx, session)
            
            output_path_tx = PROJECT_ROOT / "data" / "processed" / "tx_train.parquet"
            df_tx_features.to_parquet(output_path_tx, index=False)
            
            self.stats['features_engineered'] += len(df_tx_features)
            self.log("✅", f"Saved {len(df_tx_features):,} processed transactions")
            self.log("📈", f"Features: {df_tx_features.shape[1]}")
            self.log("💾", f"Output: {output_path_tx}")
            
            return True
            
        except Exception as e:
            self.log("❌", f"Feature engineering failed: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
    
    # ==================== PHASE 5: VERIFICATION ====================
    
    def phase5_verify(self):
        """Verify complete pipeline"""
        self.log("🔍", "=" * 70)
        self.log("🔍", "PHASE 5: VERIFICATION")
        self.log("🔍", "=" * 70)
        
        session = self.SessionFactory()
        all_ok = True
        
        try:
            # Check database
            review_count = session.query(Review).count()
            tx_count = session.query(Transaction).count()
            user_count = session.query(User).count()
            
            self.log("📊", "Database Statistics:")
            print(f"   Users: {user_count:,}")
            print(f"   Reviews: {review_count:,}")
            print(f"   Transactions: {tx_count:,}")
            
            if review_count == 0:
                self.log("❌", "No reviews in database!", 'error')
                all_ok = False
            
            # Check processed files
            reviews_parquet = PROJECT_ROOT / "data" / "processed" / "reviews_train.parquet"
            tx_parquet = PROJECT_ROOT / "data" / "processed" / "tx_train.parquet"
            
            if reviews_parquet.exists():
                df = pd.read_parquet(reviews_parquet)
                self.log("✅", f"Reviews parquet: {len(df):,} rows, {df.shape[1]} features")
                
                if 'review_text' not in df.columns:
                    self.log("❌", "review_text missing!", 'error')
                    all_ok = False
                elif df['review_text'].str.len().mean() < 10:
                    self.log("❌", "review_text is empty or too short!", 'error')
                    all_ok = False
                else:
                    self.log("✅", f"Text quality OK: avg {df['review_text'].str.len().mean():.1f} chars")
                
                if 'label_is_fake' not in df.columns:
                    self.log("⚠️", "No labels - you'll need to add them for training")
                else:
                    fake_count = df['label_is_fake'].sum()
                    self.log("✅", f"Labels present: {fake_count:,} fake ({fake_count/len(df)*100:.1f}%)")
            else:
                self.log("❌", f"Reviews parquet not found: {reviews_parquet}", 'error')
                all_ok = False
            
            if tx_parquet.exists():
                df_tx = pd.read_parquet(tx_parquet)
                self.log("✅", f"Transactions parquet: {len(df_tx):,} rows, {df_tx.shape[1]} features")
            else:
                self.log("❌", f"Transactions parquet not found: {tx_parquet}", 'error')
                all_ok = False
            
            # Sample review
            sample = session.query(Review).first()
            if sample:
                self.log("📋", "Sample review from database:")
                print(f"   ID: {sample.id}")
                print(f"   User: {sample.user_id}")
                print(f"   Text: '{sample.review_text[:80]}...'")
                print(f"   Rating: {sample.rating}")
            
            return all_ok
            
        except Exception as e:
            self.log("❌", f"Verification failed: {e}", 'error')
            import traceback
            traceback.print_exc()
            return False
        finally:
            session.close()
    
    # ==================== MAIN EXECUTION ====================
    
    def run(self, n_reviews=5000, n_transactions=10000):
        """Execute complete automation pipeline"""
        start_time = datetime.now()
        
        print("\n" + "=" * 70)
        print("🤖 FRAUD DETECTION AUTOMATION AGENT v2.0")
        print("=" * 70)
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {self.db_url[:50]}...")
        print("=" * 70 + "\n")
        
        # Execute phases
        phases = [
            ("Schema Validation", self.phase1_validate_schema),
            ("Data Generation", lambda: self.phase2_generate_data(n_reviews, n_transactions)),
            ("Database Ingestion", self.phase3_ingest_data),
            ("Feature Engineering", self.phase4_prepare_data),
            ("Verification", self.phase5_verify)
        ]
        
        for phase_name, phase_func in phases:
            success = phase_func()
            if not success:
                self.log("❌", f"PIPELINE ABORTED at: {phase_name}", 'error')
                self.print_summary()
                return False
            print()  # Spacing between phases
        
        # Success!
        self.print_summary()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print("\n🚀 Ready for model training:")
        print("   1. python scripts/train_reviews.py")
        print("   2. python scripts/train_tx.py")
        print("\n🌐 Start API server:")
        print("   cd backend && python app.py")
        print("=" * 70 + "\n")
        
        return True
    
    def print_summary(self):
        """Print execution summary"""
        print("\n" + "=" * 70)
        print("📊 EXECUTION SUMMARY")
        print("=" * 70)
        print(f"✅ Tables created: {self.stats['tables_created']}")
        print(f"✅ CSV records generated: {self.stats['csv_generated']:,}")
        print(f"✅ Users created: {self.stats['users_created']:,}")
        print(f"✅ Reviews inserted: {self.stats['reviews_inserted']:,}")
        print(f"✅ Transactions inserted: {self.stats['transactions_inserted']:,}")
        print(f"✅ Features engineered: {self.stats['features_engineered']:,}")
        print(f"❌ Errors: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\n⚠️  Error Details:")
            for i, err in enumerate(self.stats['errors'][:3], 1):
                print(f"   {i}. {err}")
            if len(self.stats['errors']) > 3:
                print(f"   ... and {len(self.stats['errors']) - 3} more")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fraud Detection Automation Agent v2.0")
    parser.add_argument("--reviews", type=int, default=5000, help="Number of reviews to generate")
    parser.add_argument("--transactions", type=int, default=10000, help="Number of transactions")
    args = parser.parse_args()
    
    try:
        agent = FraudDetectionAutomationAgent()
        success = agent.run(n_reviews=args.reviews, n_transactions=args.transactions)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)