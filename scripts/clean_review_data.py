"""
Clean review data - ULTRA SAFE VERSION
"""
import pandas as pd
import numpy as np

print("="*70)
print("REVIEW DATA CLEANING (SAFE MODE)")
print("="*70)

# Load data
df = pd.read_parquet("data/processed/reviews_train.parquet")
print(f"\n📂 Loaded {len(df):,} reviews")
print(f"   Columns: {df.shape[1]}")

initial_count = len(df)

# Check what type review_text is
print(f"\n🔍 Review text info:")
print(f"   Data type: {df['review_text'].dtype}")
print(f"   Sample value type: {type(df['review_text'].iloc[0])}")
print(f"   Sample value: {repr(df['review_text'].iloc[0])[:100]}")

# === SAFE CONVERSION ===
print("\n🧹 Converting to string safely...")

# Only convert if not already string
if df['review_text'].dtype != 'object':
    df['review_text'] = df['review_text'].astype(str)
    print("   ✅ Converted to string")
else:
    # Already object type, but might contain non-strings
    # Convert each value safely
    df['review_text'] = df['review_text'].apply(lambda x: str(x) if pd.notna(x) else '')
    print("   ✅ Ensured all values are strings")

# Check lengths BEFORE any filtering
lengths_before = df['review_text'].str.len()
print(f"\n📏 Text lengths BEFORE cleaning:")
print(f"   Min: {lengths_before.min()}")
print(f"   Max: {lengths_before.max()}")
print(f"   Mean: {lengths_before.mean():.1f}")
print(f"   Median: {lengths_before.median():.1f}")
print(f"   Length 0: {(lengths_before == 0).sum():,}")
print(f"   Length 1-5: {((lengths_before > 0) & (lengths_before <= 5)).sum():,}")
print(f"   Length 6+: {(lengths_before > 5).sum():,}")

# === MINIMAL CLEANING (Don't remove too much!) ===
print("\n🗑️  Minimal cleaning...")

# Only remove truly empty reviews
df_clean = df[df['review_text'].str.len() > 0].copy()  # Keep anything with length > 0
removed = initial_count - len(df_clean)

print(f"   Removed {removed:,} completely empty reviews")
print(f"   Remaining: {len(df_clean):,}")

# If we lost too many, something is wrong
if removed > initial_count * 0.5:
    print("\n   ⚠️  WARNING: More than 50% removed!")
    print("   Stopping to investigate...")
    
    print("\n   Sample of removed reviews:")
    removed_df = df[df['review_text'].str.len() == 0]
    for i in range(min(5, len(removed_df))):
        print(f"   {i+1}. '{repr(removed_df['review_text'].iloc[i])}'")
    
    # Don't save, exit
    exit(1)

df = df_clean

# === STRIP WHITESPACE ===
df['review_text'] = df['review_text'].str.strip()

# Re-check after stripping
df = df[df['review_text'].str.len() > 0].copy()
print(f"   After stripping: {len(df):,}")

# === FILL NUMERIC NaNs ===
print("\n🔢 Filling numeric NaNs...")
numeric_cols = df.select_dtypes(include=[np.number]).columns
nan_count = df[numeric_cols].isna().sum().sum()
if nan_count > 0:
    print(f"   Found {nan_count:,} NaN values")
    df[numeric_cols] = df[numeric_cols].fillna(0)

# === STATISTICS ===
print("\n📊 Final Text Statistics:")
lengths_after = df['review_text'].str.len()
print(f"   Min length: {lengths_after.min()}")
print(f"   Max length: {lengths_after.max()}")
print(f"   Avg length: {lengths_after.mean():.1f}")
print(f"   Median: {lengths_after.median():.1f}")

print(f"\n   Length distribution:")
print(f"   1-10 chars: {((lengths_after > 0) & (lengths_after <= 10)).sum():,}")
print(f"   11-50 chars: {((lengths_after > 10) & (lengths_after <= 50)).sum():,}")
print(f"   51-200 chars: {((lengths_after > 50) & (lengths_after <= 200)).sum():,}")
print(f"   200+ chars: {(lengths_after > 200).sum():,}")

# === LABELS ===
if 'label_is_fake' in df.columns:
    print("\n🏷️  Label Distribution:")
    label_counts = df['label_is_fake'].value_counts()
    total = len(df)
    print(f"   Real (0): {label_counts.get(0, 0):,} ({label_counts.get(0, 0)/total*100:.1f}%)")
    print(f"   Fake (1): {label_counts.get(1, 0):,} ({label_counts.get(1, 0)/total*100:.1f}%)")
else:
    print("\n⚠️  No label column found!")

# === SAMPLES ===
print("\n📋 Sample Reviews:")
for i in range(min(5, len(df))):
    text = df['review_text'].iloc[i]
    label = df['label_is_fake'].iloc[i] if 'label_is_fake' in df.columns else 'N/A'
    print(f"\n   {i+1}. Label: {label}, Length: {len(text)}")
    print(f"      '{text[:100]}{'...' if len(text) > 100 else ''}'")

# === SAVE ===
if len(df) > 0:
    print(f"\n💾 Saving cleaned data...")
    df.to_parquet("data/processed/reviews_train.parquet", index=False)
    print(f"✅ Saved {len(df):,} reviews")
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Original: {initial_count:,}")
    print(f"Cleaned: {len(df):,}")
    print(f"Removed: {initial_count - len(df):,} ({(initial_count-len(df))/initial_count*100:.1f}%)")
    print("="*70)
else:
    print("\n❌ No data remaining after cleaning!")
    print("   Check the diagnostic output above.")