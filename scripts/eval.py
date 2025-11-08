"""
Evaluate trained models and generate performance reports
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score
)
import matplotlib.pyplot as plt

MODEL_PATH = Path("backend/models")
DATA_PATH = Path("data/processed")
REPORTS_PATH = Path("reports")

REPORTS_PATH.mkdir(exist_ok=True)

def evaluate_reviews():
    """Evaluate review model on validation set"""
    print("📊 Evaluating review model...")
    
    # Load model and data
    model = joblib.load(MODEL_PATH / "review_model.pkl")
    df = pd.read_parquet(DATA_PATH / "reviews_valid.parquet")
    
    X = df.drop(columns=["label_is_fake"])
    y = df["label_is_fake"].astype(int)
    
    # Predictions
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)[:, 1]
    
    # Metrics
    print("\n" + "="*60)
    print("REVIEW MODEL - VALIDATION SET")
    print("="*60)
    print(classification_report(y, y_pred, target_names=['Real', 'Fake']))
    print(f"ROC-AUC: {roc_auc_score(y, y_proba):.4f}")
    print(f"Average Precision: {average_precision_score(y, y_proba):.4f}")
    
    # Save report
    report = {
        "roc_auc": float(roc_auc_score(y, y_proba)),
        "avg_precision": float(average_precision_score(y, y_proba))
    }
    
    with open(REPORTS_PATH / "review_eval.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Saved report to {REPORTS_PATH}/review_eval.json")

def evaluate_transactions():
    """Evaluate transaction model"""
    print("📊 Evaluating transaction model...")
    
    # Load model and data
    artifact = joblib.load(MODEL_PATH / "tx_model.pkl")
    model = artifact["pipe"]
    features = artifact["features"]
    
    df = pd.read_parquet(DATA_PATH / "tx_valid.parquet")
    
    X = df[features].fillna(0)
    
    if 'label_is_fraud' in df.columns:
        y = df['label_is_fraud'].astype(int)
        
        scores = -model.score_samples(X)
        pred = model.predict(X)
        pred_binary = (pred == -1).astype(int)
        
        print("\n" + "="*60)
        print("TRANSACTION MODEL - VALIDATION SET")
        print("="*60)
        print(classification_report(y, pred_binary, target_names=['Normal', 'Fraud']))
        print(f"ROC-AUC: {roc_auc_score(y, scores):.4f}")
        
        report = {
            "roc_auc": float(roc_auc_score(y, scores))
        }
        
        with open(REPORTS_PATH / "tx_eval.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Saved report to {REPORTS_PATH}/tx_eval.json")
    else:
        print("⚠️  No labels in validation set - skipping evaluation")

if __name__ == "__main__":
    evaluate_reviews()
    evaluate_transactions()
    print("\n✅ Evaluation complete!")