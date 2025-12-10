"""
CatBoost Credit Card Fraud Detection Model Training
Uses the Kaggle Credit Card Fraud Detection dataset (creditcard.csv)

Dataset columns:
- Time: seconds since first transaction
- V1-V28: anonymized PCA components (represents hidden risk patterns)
- Amount: transaction amount
- Class: 1 = Fraud, 0 = Safe
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler

# Get paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset", "creditcard.csv")
MODEL_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "catboost_model.pkl")
METRICS_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "catboost_metrics.json")

def load_dataset():
    """Load and preprocess the Credit Card Fraud Detection dataset"""
    print(f"📂 Loading dataset from: {DATASET_PATH}")
    
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")
    
    df = pd.read_csv(DATASET_PATH)
    print(f"✅ Dataset loaded: {df.shape[0]:,} transactions, {df.shape[1]} features")
    
    # Check class distribution
    fraud_count = df['Class'].sum()
    safe_count = len(df) - fraud_count
    print(f"📊 Class distribution:")
    print(f"   - Safe (0): {safe_count:,} ({safe_count/len(df)*100:.2f}%)")
    print(f"   - Fraud (1): {fraud_count:,} ({fraud_count/len(df)*100:.4f}%)")
    
    return df

def prepare_features(df):
    """Prepare features and target"""
    # Feature columns: Time, V1-V28, Amount
    feature_cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount']
    
    X = df[feature_cols].copy()
    y = df['Class'].copy()
    
    # Scale Amount and Time (V1-V28 are already scaled via PCA)
    scaler = StandardScaler()
    X[['Time', 'Amount']] = scaler.fit_transform(X[['Time', 'Amount']])
    
    return X, y, feature_cols, scaler

def train_model(X_train, y_train, X_val, y_val):
    """Train CatBoost classifier with optimal parameters for imbalanced data"""
    print("\n🚀 Training CatBoost model...")
    
    # Calculate class weight for imbalanced dataset
    fraud_ratio = y_train.sum() / len(y_train)
    scale_pos_weight = (1 - fraud_ratio) / fraud_ratio
    
    print(f"   Scale positive weight: {scale_pos_weight:.2f}")
    
    model = CatBoostClassifier(
        iterations=500,
        learning_rate=0.05,
        depth=6,
        loss_function='Logloss',
        eval_metric='AUC',
        scale_pos_weight=scale_pos_weight,
        random_seed=42,
        verbose=100,
        early_stopping_rounds=50,
        task_type='CPU'  # Use 'GPU' if available
    )
    
    model.fit(
        X_train, y_train,
        eval_set=(X_val, y_val),
        use_best_model=True
    )
    
    return model

def evaluate_model(model, X_test, y_test, feature_cols):
    """Evaluate model and return metrics"""
    print("\n📈 Evaluating model...")
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    metrics = {
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
        'precision': round(precision_score(y_test, y_pred) * 100, 2),
        'recall': round(recall_score(y_test, y_pred) * 100, 2),
        'f1_score': round(f1_score(y_test, y_pred) * 100, 2),
        'auc_roc': round(roc_auc_score(y_test, y_pred_proba) * 100, 2),
        'trained_at': datetime.now().isoformat(),
        'dataset_size': len(y_test),
        'model_type': 'CatBoostClassifier'
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics['confusion_matrix'] = {
        'true_negatives': int(cm[0, 0]),
        'false_positives': int(cm[0, 1]),
        'false_negatives': int(cm[1, 0]),
        'true_positives': int(cm[1, 1])
    }
    
    # Feature importance
    importances = model.get_feature_importance()
    feature_importance = sorted(
        zip(feature_cols, importances),
        key=lambda x: x[1],
        reverse=True
    )[:10]  # Top 10 features
    metrics['top_features'] = [{'name': f, 'importance': round(i, 2)} for f, i in feature_importance]
    
    print("\n" + "="*60)
    print("📊 MODEL PERFORMANCE")
    print("="*60)
    print(f"   Accuracy:  {metrics['accuracy']}%")
    print(f"   Precision: {metrics['precision']}%")
    print(f"   Recall:    {metrics['recall']}%")
    print(f"   F1-Score:  {metrics['f1_score']}%")
    print(f"   AUC-ROC:   {metrics['auc_roc']}%")
    print("="*60)
    
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Safe', 'Fraud']))
    
    print("\n🔝 Top 5 Important Features:")
    for f, i in feature_importance[:5]:
        print(f"   - {f}: {i:.2f}")
    
    return metrics

def save_model(model, scaler, feature_cols, metrics):
    """Save model artifact"""
    artifact = {
        'model': model,
        'scaler': scaler,
        'features': feature_cols,
        'metrics': metrics
    }
    
    joblib.dump(artifact, MODEL_OUTPUT_PATH)
    print(f"\n💾 Model saved to: {MODEL_OUTPUT_PATH}")
    
    # Save metrics separately for frontend access
    with open(METRICS_OUTPUT_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"📄 Metrics saved to: {METRICS_OUTPUT_PATH}")

def main():
    print("="*60)
    print("🎯 CatBoost Credit Card Fraud Detection Model Training")
    print("="*60)
    
    # Load dataset
    df = load_dataset()
    
    # Prepare features
    X, y, feature_cols, scaler = prepare_features(df)
    
    # Split data: 70% train, 15% validation, 15% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp  # 0.176 of 0.85 ≈ 0.15
    )
    
    print(f"\n📊 Data splits:")
    print(f"   - Training:   {len(X_train):,} samples")
    print(f"   - Validation: {len(X_val):,} samples")
    print(f"   - Test:       {len(X_test):,} samples")
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, feature_cols)
    
    # Save model
    save_model(model, scaler, feature_cols, metrics)
    
    print("\n✅ Training complete!")
    return metrics

if __name__ == "__main__":
    metrics = main()
