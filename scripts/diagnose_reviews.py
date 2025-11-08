"""
Diagnose what's in the review_text column
"""
import pandas as pd

df = pd.read_parquet("data/processed/reviews_train.parquet")

print("="*70)
print("REVIEW TEXT DIAGNOSTIC")
print("="*70)

print(f"\n📊 Basic Info:")
print(f"   Total rows: {len(df):,}")
print(f"   Columns: {df.shape[1]}")

print(f"\n📝 review_text Column:")
print(f"   Data type: {df['review_text'].dtype}")
print(f"   NaN count: {df['review_text'].isna().sum()}")
print(f"   Unique values: {df['review_text'].nunique():,}")

print(f"\n🔍 First 10 raw values:")
for i in range(min(10, len(df))):
    val = df['review_text'].iloc[i]
    print(f"   {i+1}. Type: {type(val).__name__:15s} | Value: {repr(val)[:80]}")

print(f"\n📏 After converting to string:")
df_test = df.copy()
df_test['review_text'] = df_test['review_text'].astype(str)
for i in range(min(5, len(df_test))):
    val = df_test['review_text'].iloc[i]
    print(f"   {i+1}. Length: {len(val):5d} | Value: '{val[:80]}'")

print(f"\n📊 String length distribution:")
lengths = df_test['review_text'].str.len()
print(f"   Min: {lengths.min()}")
print(f"   Max: {lengths.max()}")
print(f"   Mean: {lengths.mean():.1f}")
print(f"   25%: {lengths.quantile(0.25):.0f}")
print(f"   50%: {lengths.quantile(0.50):.0f}")
print(f"   75%: {lengths.quantile(0.75):.0f}")

print(f"\n🎯 Distribution of length categories:")
print(f"   Length 0: {(lengths == 0).sum():,}")
print(f"   Length 1-5: {((lengths > 0) & (lengths <= 5)).sum():,}")
print(f"   Length 6-20: {((lengths > 5) & (lengths <= 20)).sum():,}")
print(f"   Length 21-100: {((lengths > 20) & (lengths <= 100)).sum():,}")
print(f"   Length 100+: {(lengths > 100).sum():,}")

print(f"\n📋 Sample of different lengths:")
for length_category in [0, 1, 5, 10, 20, 50]:
    sample = df_test[lengths == length_category]
    if len(sample) > 0:
        print(f"\n   Length {length_category}: {len(sample):,} rows")
        print(f"   Example: '{sample['review_text'].iloc[0]}'")