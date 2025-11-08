"""
Add synthetic fraud labels to existing processed data
Uses heuristic rules based on known fraud patterns
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_fraud_score(df):
    """
    Calculate fraud likelihood score (0-1) based on features
    Higher score = more likely to be fake
    """
    score = pd.Series(0.0, index=df.index)
    
    # === TEXT-BASED INDICATORS ===
    
    # 1. Excessive uppercase (SHOUTING)
    score += (df['upper_ratio'] > 0.3).astype(float) * 0.15
    score += (df['upper_ratio'] > 0.5).astype(float) * 0.10  # Extra penalty
    
    # 2. Too many exclamation marks
    score += (df['exclaim_ratio'] > 0.05).astype(float) * 0.10
    score += (df['exclaim_ratio'] > 0.10).astype(float) * 0.10
    
    # 3. Very short reviews with extreme ratings
    short_extreme = ((df['text_len'] < 20) & 
                     ((df['rating'] == 1) | (df['rating'] == 5)))
    score += short_extreme.astype(float) * 0.15
    
    # 4. Very long reviews (potential spam)
    score += (df['text_len'] > 1000).astype(float) * 0.08
    
    # 5. Low unique word ratio (repetitive text)
    score += (df['unique_word_ratio'] < 0.3).astype(float) * 0.12
    
    # 6. Has URL (potential spam)
    score += df['has_url'].astype(float) * 0.20
    
    # 7. Has email (solicitation)
    score += df['has_email'].astype(float) * 0.25
    
    # 8. Repeated characters (e.g., "soooo goood")
    score += (df['repeated_chars'] > 5).astype(float) * 0.10
    
    # === BEHAVIORAL INDICATORS ===
    
    # 9. New account with high activity
    new_and_active = ((df['account_age_days'] < 7) & 
                      (df['user_30d_review_count'] > 10))
    score += new_and_active.astype(float) * 0.20
    
    # 10. Review burst (too many reviews in short time)
    score += (df['user_7d_review_count'] > 15).astype(float) * 0.15
    score += (df['user_1h_review_count'] > 3).astype(float) * 0.20
    
    # 11. IP address with many reviews
    score += (df['ip_30d_review_count'] > 50).astype(float) * 0.18
    score += (df['ip_30d_review_count'] > 100).astype(float) * 0.12
    
    # 12. Multiple users from same IP
    score += (df['ip_unique_users'] > 10).astype(float) * 0.15
    
    # 13. Device used for many reviews
    score += (df['device_review_count'] > 100).astype(float) * 0.15
    
    # 14. Multiple users on same device
    score += (df['device_unique_users'] > 5).astype(float) * 0.12
    
    # 15. Rating deviation (inconsistent with user's history)
    score += (df['rating_deviation'].abs() > 2.0).astype(float) * 0.10
    score += (df['rating_deviation'].abs() > 3.0).astype(float) * 0.08
    
    # Cap score at 1.0
    score = score.clip(0, 1)
    
    return score


def assign_labels(df, strategy='balanced', custom_threshold=None):
    """
    Assign binary labels based on fraud score
    
    Args:
        df: DataFrame with features
        strategy: 'conservative', 'balanced', or 'aggressive'
        custom_threshold: Override with custom threshold (0-1)
    
    Returns:
        DataFrame with label_is_fake column
    """
    print(f"\n🎯 Creating labels with '{strategy}' strategy...")
    
    # Calculate fraud scores
    df['fraud_score'] = create_fraud_score(df)
    
    # Define thresholds for each strategy
    thresholds = {
        'conservative': 0.70,  # ~5-10% flagged (high precision)
        'balanced': 0.50,      # ~10-20% flagged (balanced)
        'aggressive': 0.35     # ~20-30% flagged (high recall)
    }
    
    threshold = custom_threshold if custom_threshold is not None else thresholds.get(strategy, 0.50)
    
    # Assign binary labels
    df['label_is_fake'] = (df['fraud_score'] >= threshold).astype(int)
    
    # Statistics
    n_fake = df['label_is_fake'].sum()
    pct_fake = n_fake / len(df) * 100
    
    print(f"\n📊 Label Distribution:")
    print(f"   Total reviews: {len(df):,}")
    print(f"   Fake: {n_fake:,} ({pct_fake:.2f}%)")
    print(f"   Real: {len(df) - n_fake:,} ({100-pct_fake:.2f}%)")
    print(f"   Threshold used: {threshold:.2f}")
    print(f"\n   Score distribution:")
    print(f"   Min:  {df['fraud_score'].min():.3f}")
    print(f"   25%:  {df['fraud_score'].quantile(0.25):.3f}")
    print(f"   50%:  {df['fraud_score'].quantile(0.50):.3f}")
    print(f"   75%:  {df['fraud_score'].quantile(0.75):.3f}")
    print(f"   Max:  {df['fraud_score'].max():.3f}")
    
    return df, threshold


def analyze_labeled_data(df):
    """Analyze the quality of synthetic labels"""
    print("\n🔍 Label Quality Analysis:")
    print("=" * 60)
    
    fake_reviews = df[df['label_is_fake'] == 1]
    real_reviews = df[df['label_is_fake'] == 0]
    
    print("\n📈 Feature Comparison (Fake vs Real):")
    print("-" * 60)
    
    features_to_compare = [
        'upper_ratio', 'exclaim_ratio', 'text_len', 'rating',
        'user_30d_review_count', 'ip_30d_review_count', 
        'account_age_days', 'rating_deviation'
    ]
    
    for feat in features_to_compare:
        if feat in df.columns:
            fake_mean = fake_reviews[feat].mean()
            real_mean = real_reviews[feat].mean()
            diff = ((fake_mean - real_mean) / real_mean * 100) if real_mean != 0 else 0
            
            print(f"{feat:25s} | Fake: {fake_mean:8.2f} | Real: {real_mean:8.2f} | Diff: {diff:+6.1f}%")
    
    print("\n⭐ Rating Distribution:")
    print("-" * 60)
    print("Fake reviews:")
    print(fake_reviews['rating'].value_counts().sort_index())
    print("\nReal reviews:")
    print(real_reviews['rating'].value_counts().sort_index())


def save_labeled_data(df, output_path, include_score=False):
    """Save labeled data"""
    # Optionally keep fraud_score for analysis
    if not include_score and 'fraud_score' in df.columns:
        df = df.drop(columns=['fraud_score'])
    
    # Ensure label is integer
    df['label_is_fake'] = df['label_is_fake'].astype(int)
    
    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    
    print(f"\n✅ Saved labeled data to: {output_path}")
    print(f"   Shape: {df.shape}")
    print(f"   Columns: {len(df.columns)}")


def main():
    print("=" * 70)
    print("SYNTHETIC LABEL GENERATOR FOR FRAUD DETECTION")
    print("=" * 70)
    
    # Load processed data
    input_path = "data/processed/reviews_train.parquet"
    print(f"\n📂 Loading data from: {input_path}")
    
    df = pd.read_parquet(input_path)
    print(f"✅ Loaded {len(df):,} reviews")
    print(f"   Features: {df.shape[1]}")
    
    # Choose strategy
    print("\n🎯 Label Generation Strategies:")
    print("   1. Conservative (5-10% fake)  - High precision, low false positives")
    print("   2. Balanced (10-20% fake)     - Balanced precision/recall")
    print("   3. Aggressive (20-30% fake)   - High recall, catches more fraud")
    print("   4. Custom threshold")
    
    choice = input("\nSelect strategy (1/2/3/4) [default: 2]: ").strip() or "2"
    
    strategy_map = {
        '1': 'conservative',
        '2': 'balanced',
        '3': 'aggressive'
    }
    
    if choice == '4':
        threshold = float(input("Enter custom threshold (0.0-1.0): "))
        df_labeled, used_threshold = assign_labels(df, custom_threshold=threshold)
    else:
        strategy = strategy_map.get(choice, 'balanced')
        df_labeled, used_threshold = assign_labels(df, strategy=strategy)
    
    # Analyze
    analyze_labeled_data(df_labeled)
    
    # Save options
    print("\n💾 Save Options:")
    print("   1. Overwrite original file (recommended for training)")
    print("   2. Save as new file (keep original)")
    print("   3. Save both versions (with and without fraud_score)")
    
    save_choice = input("\nSelect option (1/2/3) [default: 1]: ").strip() or "1"
    
    if save_choice == '1':
        save_labeled_data(df_labeled, input_path, include_score=False)
    elif save_choice == '2':
        output_path = input_path.replace('.parquet', '_labeled.parquet')
        save_labeled_data(df_labeled, output_path, include_score=False)
    else:
        # Save training version
        save_labeled_data(df_labeled, input_path, include_score=False)
        # Save analysis version with scores
        analysis_path = input_path.replace('.parquet', '_with_scores.parquet')
        save_labeled_data(df_labeled, analysis_path, include_score=True)
        print(f"✅ Also saved version with fraud scores to: {analysis_path}")
    
    # Save threshold info
    threshold_file = "data/artifacts/label_generation_info.json"
    Path(threshold_file).parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(threshold_file, 'w') as f:
        json.dump({
            'threshold': used_threshold,
            'total_reviews': len(df_labeled),
            'fake_count': int(df_labeled['label_is_fake'].sum()),
            'fake_percentage': float(df_labeled['label_is_fake'].mean() * 100),
            'timestamp': pd.Timestamp.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📝 Label generation info saved to: {threshold_file}")
    
    print("\n" + "=" * 70)
    print("✅ LABELING COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("   1. Review the labeled data quality")
    print("   2. Train model: python scripts/train_reviews.py")
    print("   3. Evaluate and adjust threshold if needed")


if __name__ == "__main__":
    main()