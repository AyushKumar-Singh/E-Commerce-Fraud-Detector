"""
ETL script to prepare raw data for training
Run this to transform raw CSVs into feature-engineered parquet files
"""

import pandas as pd
import sys
import os
from pathlib import Path
from dotenv import load_dotenv  # ✅ Load environment variables

# ---------------------------------------------------------------------
# Load environment variables from the project root .env file
# ---------------------------------------------------------------------
project_root = Path(__file__).parent.parent  # one level up from /scripts/
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# ---------------------------------------------------------------------
# Add backend folder to system path (so imports work properly)
# ---------------------------------------------------------------------
sys.path.insert(0, str(project_root / "backend"))

from db.models import get_session
from pipelines.review_pipeline import batch_engineer_reviews
from pipelines.tx_pipeline import batch_engineer_transactions


def prepare_reviews():
    """Prepare review training data"""
    print("📊 Preparing review data...")

    # Load raw data
    raw_path = project_root / "scripts" / "data" / "raw" / "reviews.csv"
    if not raw_path.exists():
        print(f"❌ {raw_path} not found")
        return

    df = pd.read_csv(raw_path)
    print(f"✅ Loaded {len(df)} raw reviews")

    # Get database session using DATABASE_URL from .env
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env file")
        return

    engine, Session = get_session(db_url)
    session = Session()

    try:
        # Engineer features
        df_features = batch_engineer_reviews(df, session)

        # Save processed data
        output_path = "data" / "raw" / "reviews.csv"
        os.makedirs(output_path.parent, exist_ok=True)
        df_features.to_parquet(output_path, index=False)

        print(f"✅ Saved {len(df_features)} processed reviews to {output_path}")
        print(f"📈 Features: {list(df_features.columns)}")

    finally:
        session.close()


def prepare_transactions():
    """Prepare transaction training data"""
    print("📊 Preparing transaction data...")

    # Load raw data
    raw_path = project_root / "scripts" / "data" / "raw" / "transactions.csv"
    if not raw_path.exists():
        print(f"❌ {raw_path} not found")
        return

    df = pd.read_csv(raw_path)
    print(f"✅ Loaded {len(df)} raw transactions")

    # Get database session using DATABASE_URL from .env
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env file")
        return

    engine, Session = get_session(db_url)
    session = Session()

    try:
        # Engineer features
        df_features = batch_engineer_transactions(df, session)

        # Save processed data
        output_path = project_root / "data" / "processed" / "tx_train.parquet"
        os.makedirs(output_path.parent, exist_ok=True)
        df_features.to_parquet(output_path, index=False)

        print(f"✅ Saved {len(df_features)} processed transactions to {output_path}")
        print(f"📈 Features: {list(df_features.columns)}")

    finally:
        session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare training data")
    parser.add_argument("--type", choices=["reviews", "transactions", "all"], default="all")
    args = parser.parse_args()

    if args.type in ["reviews", "all"]:
        prepare_reviews()

    if args.type in ["transactions", "all"]:
        prepare_transactions()

    print("✅ Data preparation complete!")
