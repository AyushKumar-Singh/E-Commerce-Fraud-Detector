"""
Train fraudulent transaction detection model
Isolation Forest for anomaly detection
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATA_PATH = Path("data/processed/tx_train.parquet")
MODEL_PATH = Path("backend/models")
ARTIFACTS_PATH = Path("data/artifacts")
PLOTS_PATH = Path("reports/figures")

# Create directories
MODEL_PATH.mkdir(parents=True, exist_ok=True)
ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
PLOTS_PATH.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load processed transaction data"""
    print("📂 Loading data...")
    df = pd.read_parquet(DATA_PATH)
    
    if 'label_is_fraud' in df.columns:
        print(f"✅ Loaded {len(df)} transactions")
        print(f"   Fraud: {df['label_is_fraud'].sum()} ({df['label_is_fraud'].mean()*100:.1f}%)")
        print(f"   Legit: {(~df['label_is_fraud']).sum()} ({(~df['label_is_fraud']).mean()*100:.1f}%)")
    else:
        print(f"⚠️  No labels found - using unsupervised learning")
    
    return df

def build_pipeline(contamination=0.02):
    """Build Isolation Forest pipeline"""
    print(f"🔧 Building pipeline (contamination={contamination})...")
    
    # Features for anomaly detection
    num_features = [
        "amount", "hour_of_day", "is_night_time", "is_weekend",
        "account_age_days", "user_total_txs", "user_avg_amount",
        "user_max_amount", "user_std_amount", "amount_z",
        "user_1h_tx", "user_24h_tx", "user_7d_tx", "user_24h_amount",
        "ip_1h_tx", "ip_unique_users", "dev_switch_7d",
        "rolling_mean_diff", "rolling_std",
        "channel_mismatch", "channel_freq", "country_mismatch"
    ]
    
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("iforest", IsolationForest(
            n_estimators=300,
            contamination=contamination,
            max_samples='auto',
            max_features=1.0,
            random_state=42,
            n_jobs=-1
        ))
    ])
    
    return pipeline, num_features

def train_model(df, pipeline, features):
    """Train Isolation Forest"""
    print("🎯 Training Isolation Forest...")
    
    # Prepare features
    X = df[features].fillna(0)
    
    # If labels exist, split for evaluation
    if 'label_is_fraud' in df.columns:
        y = df['label_is_fraud'].astype(int)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        has_labels = True
    else:
        X_train = X
        X_test = None
        y_test = None
        has_labels = False
    
    print(f"   Training samples: {len(X_train)}")
    
    # Train (unsupervised)
    pipeline.fit(X_train)
    
    # Get anomaly scores
    train_scores = -pipeline.score_samples(X_train)  # higher = more anomalous
    
    print(f"   Anomaly score range: [{train_scores.min():.3f}, {train_scores.max():.3f}]")
    print(f"   Mean: {train_scores.mean():.3f}, Std: {train_scores.std():.3f}")
    
    # Evaluate if labels exist
    if has_labels:
        # Predictions (-1 for anomaly, 1 for normal)
        train_pred = pipeline.predict(X_train)
        train_pred_binary = (train_pred == -1).astype(int)
        
        test_pred = pipeline.predict(X_test)
        test_pred_binary = (test_pred == -1).astype(int)
        test_scores = -pipeline.score_samples(X_test)
        
        print("\n" + "="*60)
        print("TEST SET PERFORMANCE (if labels available)")
        print("="*60)
        print(classification_report(y_test, test_pred_binary, target_names=['Normal', 'Fraud']))
        
        # ROC-AUC using anomaly scores
        test_auc = roc_auc_score(y_test, test_scores)
        print(f"ROC-AUC (anomaly score): {test_auc:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, test_pred_binary)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', 
                   xticklabels=['Normal', 'Fraud'], yticklabels=['Normal', 'Fraud'])
        plt.title('Confusion Matrix - Transaction Fraud Detection')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(PLOTS_PATH / 'tx_confusion_matrix.png', dpi=300)
        print(f"✅ Saved confusion matrix to {PLOTS_PATH / 'tx_confusion_matrix.png'}")
        
        metrics = {
            "model": "IsolationForest",
            "contamination": pipeline.named_steps['iforest'].contamination,
            "test_roc_auc": float(test_auc),
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }
    else:
        metrics = {
            "model": "IsolationForest",
            "contamination": pipeline.named_steps['iforest'].contamination,
            "train_samples": len(X_train),
            "note": "Unsupervised - no labels for evaluation"
        }
    
    # Anomaly score distribution
    plt.figure(figsize=(10, 6))
    plt.hist(train_scores, bins=50, alpha=0.7, edgecolor='black')
    plt.axvline(train_scores.mean(), color='r', linestyle='--', label=f'Mean: {train_scores.mean():.3f}')
    plt.axvline(np.percentile(train_scores, 98), color='g', linestyle='--', 
               label=f'98th percentile: {np.percentile(train_scores, 98):.3f}')
    plt.xlabel('Anomaly Score')
    plt.ylabel('Frequency')
    plt.title('Distribution of Anomaly Scores')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'tx_anomaly_distribution.png', dpi=300)
    print(f"✅ Saved anomaly distribution to {PLOTS_PATH / 'tx_anomaly_distribution.png'}")
    
    # Save metrics
    with open(ARTIFACTS_PATH / 'tx_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return pipeline, metrics

def save_model(pipeline, features):
    """Save trained model and feature list"""
    print(f"\n💾 Saving model to {MODEL_PATH}/tx_model.pkl...")
    
    artifact = {
        "pipe": pipeline,
        "features": features
    }
    
    joblib.dump(artifact, MODEL_PATH / "tx_model.pkl")
    print("✅ Model saved successfully!")

def main():
    print("="*60)
    print("TRANSACTION FRAUD DETECTION - MODEL TRAINING")
    print("="*60 + "\n")
    
    # Load data
    df = load_data()
    
    # Build pipeline
    pipeline, features = build_pipeline(contamination=0.02)
    
    # Train
    trained_pipeline, metrics = train_model(df, pipeline, features)
    
    # Save
    save_model(trained_pipeline, features)
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"💾 Model saved to: {MODEL_PATH}/tx_model.pkl")
    print(f"📊 Features used: {len(features)}")

if __name__ == "__main__":
    main()