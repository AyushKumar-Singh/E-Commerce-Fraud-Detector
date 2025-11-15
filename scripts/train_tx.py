"""
Train fake review detection model - PRODUCTION VERSION
Logistic Regression with TF-IDF + engineered features
Compatible with data_automation_agent.py output
"""

import pandas as pd
import numpy as np
import joblib
import json
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, confusion_matrix, f1_score
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration - Aligned with automation agent
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "reviews_train.parquet"
MODEL_PATH = PROJECT_ROOT / "backend" / "models"
ARTIFACTS_PATH = PROJECT_ROOT / "data" / "artifacts"
PLOTS_PATH = PROJECT_ROOT / "reports" / "figures"

# Create directories
MODEL_PATH.mkdir(parents=True, exist_ok=True)
ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
PLOTS_PATH.mkdir(parents=True, exist_ok=True)


def log(emoji, message):
    """Consistent logging with automation agent"""
    print(f"{emoji} {message}")


def validate_data(df):
    """Validate processed data quality"""
    log("🔍", "Validating data quality...")
    
    issues = []
    
    # Check required columns
    required_cols = ['review_text', 'rating', 'label_is_fake']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        issues.append(f"Missing columns: {missing}")
    
    # Check review_text
    if 'review_text' in df.columns:
        empty_text = (df['review_text'].str.len() == 0).sum()
        if empty_text > 0:
            issues.append(f"{empty_text} reviews have empty text")
        
        avg_len = df['review_text'].str.len().mean()
        if avg_len < 10:
            issues.append(f"Text too short (avg {avg_len:.1f} chars)")
        else:
            log("✅", f"Text quality OK (avg {avg_len:.1f} chars)")
    
    # Check labels
    if 'label_is_fake' in df.columns:
        fake_count = df['label_is_fake'].sum()
        fake_pct = fake_count / len(df) * 100
        
        if fake_count < 10:
            issues.append(f"Too few fake samples ({fake_count})")
        elif fake_count > len(df) - 10:
            issues.append(f"Too few real samples")
        else:
            log("✅", f"Labels balanced: {fake_count:,} fake ({fake_pct:.1f}%)")
    
    # Check for NaN
    nan_counts = df.isnull().sum()
    if nan_counts.sum() > 0:
        log("⚠️", f"Found {nan_counts.sum()} NaN values")
    
    if issues:
        log("❌", "Data validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    log("✅", "Data validation passed")
    return True


def load_data():
    """Load processed review data with validation"""
    log("📂", "=" * 70)
    log("📂", "LOADING DATA")
    log("📂", "=" * 70)
    
    if not DATA_PATH.exists():
        log("❌", f"Data file not found: {DATA_PATH}")
        log("💡", "Run first: python scripts/data_automation_agent.py")
        sys.exit(1)
    
    log("📂", f"Loading from: {DATA_PATH}")
    df = pd.read_parquet(DATA_PATH)
    
    log("✅", f"Loaded {len(df):,} reviews")
    log("📊", f"Features: {df.shape[1]} columns")
    
    # Validate
    if not validate_data(df):
        log("❌", "Data validation failed - cannot proceed")
        sys.exit(1)
    
    # Statistics
    if 'label_is_fake' in df.columns:
        fake_count = df['label_is_fake'].sum()
        real_count = len(df) - fake_count
        print(f"   Fake: {fake_count:,} ({fake_count/len(df)*100:.1f}%)")
        print(f"   Real: {real_count:,} ({real_count/len(df)*100:.1f}%)")
    
    return df


def build_pipeline():
    """Build ML pipeline with robust settings"""
    log("🔧", "=" * 70)
    log("🔧", "BUILDING PIPELINE")
    log("🔧", "=" * 70)
    
    # Text features
    text_features = "review_text"
    
    # Numerical features (all that might exist)
    potential_num_features = [
        "rating", "text_len", "word_count", "upper_ratio", "digit_ratio",
        "punct_ratio", "exclaim_ratio", "question_ratio", "avg_word_len",
        "unique_word_ratio", "has_url", "has_email", "repeated_chars",
        "rating_deviation", "user_avg_rating", "account_age_days",
        "user_30d_review_count", "user_7d_review_count", "user_1h_review_count",
        "ip_30d_review_count", "ip_unique_users",
        "device_review_count", "device_unique_users",
        "product_review_count", "product_avg_rating"
    ]
    
    log("⚙️", f"Text feature: {text_features}")
    log("⚙️", f"Numerical features: {len(potential_num_features)} available")
    
    # Preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,      # Reduced for stability
                min_df=2,                # More lenient
                max_df=0.9,
                sublinear_tf=True,
                strip_accents='unicode',
                lowercase=True,
                token_pattern=r'\b[a-zA-Z]{2,}\b'
            ), text_features),
            ("num", StandardScaler(), potential_num_features)
        ],
        remainder="drop",
        sparse_threshold=0.3
    )
    
    # Full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(
            max_iter=1000,           # Increased
            class_weight="balanced",
            random_state=42,
            solver='lbfgs',          # More stable than saga
            penalty='l2',
            C=1.0,
            n_jobs=-1
        ))
    ])
    
    log("✅", "Pipeline built successfully")
    
    return pipeline, potential_num_features


def train_model(df, pipeline):
    """Train and evaluate model with comprehensive metrics"""
    log("🎯", "=" * 70)
    log("🎯", "TRAINING MODEL")
    log("🎯", "=" * 70)
    
    # Prepare data
    X = df.drop(columns=["label_is_fake"])
    y = df["label_is_fake"].astype(int)
    
    # Check class distribution
    class_counts = y.value_counts()
    log("📊", f"Class distribution:")
    print(f"   Real (0): {class_counts.get(0, 0):,}")
    print(f"   Fake (1): {class_counts.get(1, 0):,}")
    
    # Split with stratification
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        log("✅", "Stratified split successful")
    except ValueError as e:
        log("⚠️", f"Stratification failed: {e}")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    
    print(f"   Train: {len(X_train):,} samples")
    print(f"   Test: {len(X_test):,} samples")
    
    # Cross-validation
    log("📊", "Running 5-fold cross-validation...")
    try:
        cv_scores = cross_val_score(
            pipeline, X_train, y_train, 
            cv=5, 
            scoring='roc_auc', 
            n_jobs=-1
        )
        log("✅", f"CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    except Exception as e:
        log("⚠️", f"Cross-validation failed: {e}")
        cv_scores = np.array([0.5])
    
    # Train on full training set
    log("🚀", "Training on full training set...")
    pipeline.fit(X_train, y_train)
    log("✅", "Training completed")
    
    # Predictions
    y_train_pred = pipeline.predict(X_train)
    y_train_proba = pipeline.predict_proba(X_train)[:, 1]
    
    y_test_pred = pipeline.predict(X_test)
    y_test_proba = pipeline.predict_proba(X_test)[:, 1]
    
    # Metrics
    print("\n" + "=" * 70)
    print("📈 TRAINING SET PERFORMANCE")
    print("=" * 70)
    print(classification_report(y_train, y_train_pred, target_names=['Real', 'Fake'], zero_division=0))
    train_auc = roc_auc_score(y_train, y_train_proba)
    print(f"ROC-AUC: {train_auc:.4f}")
    
    print("\n" + "=" * 70)
    print("📈 TEST SET PERFORMANCE")
    print("=" * 70)
    print(classification_report(y_test, y_test_pred, target_names=['Real', 'Fake'], zero_division=0))
    test_auc = roc_auc_score(y_test, y_test_proba)
    print(f"ROC-AUC: {test_auc:.4f}")
    
    # Visualizations
    log("📊", "Generating visualizations...")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
    plt.title('Confusion Matrix - Fake Review Detection')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'review_confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    log("✅", f"Saved: {PLOTS_PATH / 'review_confusion_matrix.png'}")
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_test_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, linewidth=2, label=f'ROC Curve (AUC = {test_auc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Fake Review Detection')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'review_roc_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    log("✅", f"Saved: {PLOTS_PATH / 'review_roc_curve.png'}")
    
    # Precision-Recall Curve
    precision, recall, pr_thresholds = precision_recall_curve(y_test, y_test_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, linewidth=2, label='PR Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_PATH / 'review_pr_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    log("✅", f"Saved: {PLOTS_PATH / 'review_pr_curve.png'}")
    
    # Optimal threshold
    if len(pr_thresholds) > 0:
        f1_scores = [f1_score(y_test, y_test_proba >= t, zero_division=0) for t in pr_thresholds]
        optimal_idx = np.argmax(f1_scores)
        optimal_threshold = pr_thresholds[optimal_idx]
        optimal_f1 = f1_scores[optimal_idx]
    else:
        optimal_threshold = 0.5
        optimal_f1 = f1_score(y_test, y_test_pred, zero_division=0)
    
    log("📌", f"Optimal threshold: {optimal_threshold:.4f} (F1={optimal_f1:.4f})")
    
    # Save metrics
    metrics = {
        "model": "LogisticRegression",
        "cv_roc_auc_mean": float(cv_scores.mean()),
        "cv_roc_auc_std": float(cv_scores.std()),
        "train_roc_auc": float(train_auc),
        "test_roc_auc": float(test_auc),
        "optimal_threshold": float(optimal_threshold),
        "optimal_f1": float(optimal_f1),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "n_features": X_train.shape[1]
    }
    
    with open(ARTIFACTS_PATH / 'review_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    log("✅", f"Saved metrics: {ARTIFACTS_PATH / 'review_metrics.json'}")
    
    return pipeline, optimal_threshold, metrics


def save_model(pipeline, threshold):
    """Save trained model and threshold"""
    log("💾", "=" * 70)
    log("💾", "SAVING MODEL")
    log("💾", "=" * 70)
    
    model_file = MODEL_PATH / "review_model.pkl"
    threshold_file = MODEL_PATH / "review_threshold.txt"
    
    joblib.dump(pipeline, model_file)
    log("✅", f"Model saved: {model_file}")
    
    with open(threshold_file, "w") as f:
        f.write(str(threshold))
    log("✅", f"Threshold saved: {threshold_file}")


def main():
    """Main training workflow"""
    print("\n" + "=" * 70)
    print("🤖 FAKE REVIEW DETECTION - MODEL TRAINING")
    print("=" * 70)
    print(f"Data: {DATA_PATH}")
    print(f"Output: {MODEL_PATH}")
    print("=" * 70 + "\n")
    
    try:
        # Load data
        df = load_data()
        print()
        
        # Build pipeline
        pipeline, features = build_pipeline()
        print()
        
        # Train
        trained_pipeline, threshold, metrics = train_model(df, pipeline)
        print()
        
        # Save
        save_model(trained_pipeline, threshold)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE!")
        print("=" * 70)
        print(f"📊 Test ROC-AUC: {metrics['test_roc_auc']:.4f}")
        print(f"🎯 Optimal Threshold: {threshold:.4f}")
        print(f"💾 Model: {MODEL_PATH / 'review_model.pkl'}")
        print(f"📈 Metrics: {ARTIFACTS_PATH / 'review_metrics.json'}")
        print(f"📊 Plots: {PLOTS_PATH}/")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        log("❌", f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())