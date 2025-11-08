def build_pipeline():
    """Build ML pipeline with robust text handling"""
    print("🔧 Building pipeline...")
    
    # Text features
    text_features = "review_text"
    
    # Numerical features
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
    
    # Preprocessor with robust TfidfVectorizer settings
    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,          # Reduced from 10000
                min_df=2,                    # Reduced from 3
                max_df=0.9,                  # Increased from 0.8
                sublinear_tf=True,
                strip_accents='unicode',
                lowercase=True,
                token_pattern=r'\b[a-zA-Z]{2,}\b',  # Only words with 2+ letters
                stop_words=None              # Don't filter stop words initially
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
            max_iter=1000,              # Increased from 500
            class_weight="balanced",
            random_state=42,
            solver='lbfgs',             # Changed from 'saga'
            penalty='l2',               # Changed from 'elasticnet'
            C=1.0
        ))
    ])
    
    return pipeline, potential_num_features


def train_model(df, pipeline):
    """Train and evaluate model with better error handling"""
    print("🎯 Training model...")
    
    # ========== DATA CLEANING ==========
    print("\n🧹 Cleaning data...")
    
    # Ensure review_text is string and not empty
    df['review_text'] = df['review_text'].astype(str)
    df['review_text'] = df['review_text'].str.strip()
    
    # Remove rows with empty or very short text
    initial_len = len(df)
    df = df[df['review_text'].str.len() > 5]
    removed = initial_len - len(df)
    if removed > 0:
        print(f"   ⚠️  Removed {removed} rows with invalid text")
    
    # Fill NaN values in numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # ========== PREPARE DATA ==========
    X = df.drop(columns=["label_is_fake"])
    y = df["label_is_fake"].astype(int)
    
    # Check class distribution
    class_dist = y.value_counts()
    print(f"\n   Class distribution:")
    print(f"   Real (0): {class_dist.get(0, 0):,} ({class_dist.get(0, 0)/len(y)*100:.1f}%)")
    print(f"   Fake (1): {class_dist.get(1, 0):,} ({class_dist.get(1, 0)/len(y)*100:.1f}%)")
    
    if class_dist.get(1, 0) < 10:
        print("\n   ⚠️  WARNING: Very few positive samples!")
    
    # Check for minimum samples
    if len(df) < 100:
        print("\n   ⚠️  WARNING: Very small dataset! Results may not be reliable.")
    
    # ========== SPLIT DATA ==========
    # Use stratified split with error handling
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError as e:
        print(f"   ⚠️  Stratified split failed: {e}")
        print("   Using non-stratified split...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 