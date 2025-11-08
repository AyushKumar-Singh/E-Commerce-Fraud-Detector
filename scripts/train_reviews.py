"""
Train fake review detection model
Logistic Regression with TF-IDF + engineered features
"""

import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, confusion_matrix, f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATA_PATH = Path("data/processed/reviews_train.parquet")
MODEL_PATH = Path("backend/models")
ARTIFACTS_PATH = Path("data/artifacts")
PLOTS_PATH = Path("reports/figures")

# Create directories
MODEL_PATH.mkdir(parents=True, exist_ok=True)
ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
PLOTS_PATH.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load processed review data"""
    print("📂 Loading data...")
    df = pd.read_parquet(DATA_PATH)
    
    # Assume 'label_is_fake' is the target column
    if 'label_is_fake' not in df.columns:
        raise ValueError("Missing target column 'label_is_fake'")
    
    print(f"✅ Loaded {len(df)} reviews")
    print(f"   Fake: {df['label_is_fake'].sum()} ({df['label_is_fake'].mean()*100:.1f}%)")
    print(f"   Real: {(~df['label_is_fake']).sum()} ({(~df['label_is_fake']).mean()*100:.1f}%)")
    
    return df

def build_pipeline():
    """Build ML pipeline"""
    print("🔧 Building pipeline...")
    
    # Text features
    text_features = "review_text"
    
    # Numerical features
    num_features = [
        "rating", "text_len", "word_count", "upper_ratio", "digit_ratio",
        "punct_ratio", "exclaim_ratio", "question_ratio", "avg_word_len",
        "unique_word_ratio", "has_url", "has_email", "repeated_chars",
        "rating_deviation", "user_avg_rating", "account_age_days",
        "user_30d_review_count", "user_7d_review_count", "user_1h_review_count",
        "ip_30d_review_count", "ip_unique_users",
        "device_review_count", "device_unique_users",
        "product_review_count", "product_avg_rating"
    ]
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=10000,
                min_df=3,
                max_df=0.8,
                sublinear_tf=True
            ), text_features),
            ("num", StandardScaler(), num_features)
        ],
        remainder="drop",
        sparse_threshold=0.3
    )
    
    # Full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(
            max_iter=500,
            class_weight="balanced",
            random_state=42,
            solver='saga',
            penalty='elasticnet',
            l1_ratio=0.5
        ))
    ])
    
    return pipeline, num_features

def train_model(df, pipeline):
    """Train and evaluate model"""
    print("🎯 Training model...")
    
    # Prepare data
    X = df.drop(columns=["label_is_fake"])
    y = df["label_is_fake"].astype(int)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   Train: {len(X_train)} samples")
    print(f"   Test: {len(X_test)} samples")
    
    # Cross-validation
    print("📊 Cross-validation...")
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='roc_auc', n_jobs=-1)
    print(f"   CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    # Train on full training set
    print("🚀 Training on full training set...")
    pipeline.fit(X_train, y_train)
    
    # Predictions
    y_train_pred = pipeline.predict(X_train)
    y_train_proba = pipeline.predict_proba(X_train)[:, 1]
    
    y_test_pred = pipeline.predict(X_test)
    y_test_proba = pipeline.predict_proba(X_test)[:, 1]
    
    # Metrics
    print("\n" + "="*60)
    print("TRAINING SET PERFORMANCE")
    print("="*60)
    print(classification_report(y_train, y_train_pred, target_names=['Real', 'Fake']))
    print(f"ROC-AUC: {roc_auc_score(y_train, y_train_proba):.4f}")
    
    print("\n" + "="*60)
    print("TEST SET PERFORMANCE")
    print("="*60)
    print(classification_report(y_test, y_test_pred, target_names=['Real', 'Fake']))
    test_auc = roc_auc_score(y_test, y_test_proba)
    print(f"ROC-AUC: {test_auc:.4f}")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
    plt.title('Confusion Matrix - Review Detection')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'review_confusion_matrix.png', dpi=300)
    print(f"✅ Saved confusion matrix to {PLOTS_PATH / 'review_confusion_matrix.png'}")
    
    # ROC Curve
    fpr, tpr, thresholds = roc_curve(y_test, y_test_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {test_auc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Fake Review Detection')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'review_roc_curve.png', dpi=300)
    print(f"✅ Saved ROC curve to {PLOTS_PATH / 'review_roc_curve.png'}")
    
    # Precision-Recall Curve
    precision, recall, pr_thresholds = precision_recall_curve(y_test, y_test_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, label='PR Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'review_pr_curve.png', dpi=300)
    print(f"✅ Saved PR curve to {PLOTS_PATH / 'review_pr_curve.png'}")
    
    # Optimal threshold
    f1_scores = [f1_score(y_test, y_test_proba >= t) for t in pr_thresholds]
    optimal_idx = np.argmax(f1_scores)
    optimal_threshold = pr_thresholds[optimal_idx]
    print(f"\n📌 Optimal threshold (max F1): {optimal_threshold:.4f}")
    print(f"   F1 Score at optimal threshold: {f1_scores[optimal_idx]:.4f}")
    
    # Save metrics
    metrics = {
        "model": "LogisticRegression",
        "cv_roc_auc_mean": float(cv_scores.mean()),
        "cv_roc_auc_std": float(cv_scores.std()),
        "test_roc_auc": float(test_auc),
        "optimal_threshold": float(optimal_threshold),
        "optimal_f1": float(f1_scores[optimal_idx]),
        "train_samples": len(X_train),
        "test_samples": len(X_test)
    }
    
    with open(ARTIFACTS_PATH / 'review_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return pipeline, optimal_threshold, metrics

def save_model(pipeline, threshold):
    """Save trained model"""
    print(f"\n💾 Saving model to {MODEL_PATH}/review_model.pkl...")
    joblib.dump(pipeline, MODEL_PATH / "review_model.pkl")
    
    # Save threshold separately
    with open(MODEL_PATH / "review_threshold.txt", "w") as f:
        f.write(str(threshold))
    
    print("✅ Model saved successfully!")

def main():
    print("="*60)
    print("FAKE REVIEW DETECTION - MODEL TRAINING")
    print("="*60 + "\n")
    
    # Load data
    df = load_data()
    
    # Build pipeline
    pipeline, features = build_pipeline()
    
    # Train
    trained_pipeline, threshold, metrics = train_model(df, pipeline)
    
    # Save
    save_model(trained_pipeline, threshold)
    
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"📊 Test ROC-AUC: {metrics['test_roc_auc']:.4f}")
    print(f"🎯 Optimal Threshold: {threshold:.4f}")
    print(f"💾 Model saved to: {MODEL_PATH}/review_model.pkl")

if __name__ == "__main__":
    main()