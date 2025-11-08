"""
Generate sample data for testing - COMPLETE VERSION
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_reviews(n=5000):
    """Generate fake review dataset WITH REAL TEXT CONTENT"""
    print(f"📝 Generating {n} sample reviews...")
    
    # Fake review patterns (obvious fraud signals)
    fake_patterns = [
        "AMAZING!!! BEST PRODUCT EVER!!! BUY NOW!!!",
        "Worst thing I ever bought!!! TERRIBLE!!! WASTE OF MONEY!!!",
        "Five stars!!!!! Perfect!!!!! Highly recommend!!!!! MUST BUY!!!!!",
        "⭐⭐⭐⭐⭐ GREAT PRODUCT EVERYONE SHOULD BUY THIS",
        "TERRIBLE DO NOT BUY!!! SCAM!!! HORRIBLE!!!",
        "PERFECT PRODUCT!!! AMAZING QUALITY!!! BUY NOW!!!",
        "Best purchase ever!!!! So happy!!!! Love it!!!!",
        "Absolutely horrible product! Never buy! Worst ever!",
        "HIGHLY RECOMMEND THIS!!! AMAZING!!! FANTASTIC!!!",
        "Five star product! Perfect! Everyone needs this!",
        "BEST EVER!!!!! AWESOME!!!!! BUY IT NOW!!!!!",
        "HORRIBLE PRODUCT DO NOT WASTE YOUR MONEY!!!",
    ]
    
    # Real review patterns (genuine, balanced)
    real_patterns = [
        "Good product, works as expected. Delivery was on time and packaging was secure.",
        "Decent quality for the price. Would recommend to others looking for value.",
        "It's okay, nothing special but gets the job done well enough for daily use.",
        "Nice purchase, happy with it. Good value for money and arrived quickly.",
        "Works well, arrived on time. Packaging could be better but product is fine.",
        "Quality is good, though packaging could be improved. Overall satisfied.",
        "Satisfied with the purchase. Does what it says on the box without issues.",
        "Pretty good product. Met my expectations overall and seems durable.",
        "Fair quality for the price point. Would buy again if needed.",
        "Solid product, no complaints. Shipping was fast and item as described.",
        "Does the job. Nothing fancy but works fine for what I need.",
        "Good value. Simple and functional as described in the listing.",
        "Works as advertised. Happy with this purchase and would recommend.",
        "Decent product. Does what I needed it to do without problems.",
        "No issues so far. Seems to be good quality and well made.",
        "Satisfied customer. Product arrived in good condition and works well.",
        "Good product for everyday use. Recommend it to others.",
        "Works perfectly. Exactly what I was looking for at this price.",
        "Nice quality. Better than I expected for the price point.",
        "Simple and effective. Does what it's supposed to do reliably.",
        "Product is fine. No complaints. Gets the job done.",
        "Happy with my purchase. Good quality and fair price.",
        "Works as expected. Nothing extraordinary but solid product.",
        "Decent buy. Does what it claims and arrived on time.",
        "Good enough for the price. No issues so far after a week of use.",
    ]
    
    reviews = []
    
    for i in range(n):
        is_fake = random.random() < 0.15  # 15% fake reviews
        
        # Select review text
        if is_fake:
            review_text = random.choice(fake_patterns)
            # Add variations to fake reviews
            if random.random() < 0.4:
                review_text += " " + random.choice(["!!!", "BUY IT!", "BEST EVER!", "AMAZING!", "PERFECT!"])
        else:
            review_text = random.choice(real_patterns)
            # Add natural variations to real reviews
            if random.random() < 0.3:
                variations = [
                    " The color is nice.",
                    " Material feels durable.",
                    " Size is accurate.",
                    " Fast shipping.",
                    " Good customer service.",
                    " Instructions were clear.",
                    " Easy to use.",
                ]
                review_text += random.choice(variations)
        
        # Create review record
        review = {
            "user_id": random.randint(1, 500),
            "product_id": f"PROD-{random.randint(1, 100)}",
            "review_text": review_text,  # ACTUAL TEXT CONTENT
            "rating": random.choice([1, 5] if is_fake else [3, 4, 5]),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "device_fingerprint": f"device_{random.randint(1, 200)}",
            "label_is_fake": int(is_fake)  # Ground truth label
        }
        reviews.append(review)
    
    df = pd.DataFrame(reviews)
    
    # Create output directory
    os.makedirs("data/raw", exist_ok=True)
    
    # Save to CSV
    df.to_csv("data/raw/reviews.csv", index=False)
    
    # Statistics
    fake_count = df['label_is_fake'].sum()
    real_count = len(df) - fake_count
    
    print(f"✅ Generated {len(df):,} reviews")
    print(f"   Fake: {fake_count:,} ({fake_count/len(df)*100:.1f}%)")
    print(f"   Real: {real_count:,} ({real_count/len(df)*100:.1f}%)")
    print(f"   Saved to: data/raw/reviews.csv")
    
    # Show samples
    print(f"\n📋 Sample FAKE reviews:")
    for idx, text in enumerate(df[df['label_is_fake'] == 1]['review_text'].head(3), 1):
        print(f"   {idx}. '{text[:80]}{'...' if len(text) > 80 else ''}'")
    
    print(f"\n📋 Sample REAL reviews:")
    for idx, text in enumerate(df[df['label_is_fake'] == 0]['review_text'].head(3), 1):
        print(f"   {idx}. '{text[:80]}{'...' if len(text) > 80 else ''}'")
    
    # Verify text is not empty
    empty_count = (df['review_text'].str.len() == 0).sum()
    if empty_count > 0:
        print(f"\n⚠️  WARNING: {empty_count} empty reviews found!")
    else:
        print(f"\n✅ All reviews have text content")
        print(f"   Average text length: {df['review_text'].str.len().mean():.1f} characters")
    
    return df


def generate_transactions(n=10000):
    """Generate transaction dataset"""
    print(f"\n💳 Generating {n} sample transactions...")
    
    transactions = []
    
    for i in range(n):
        is_fraud = random.random() < 0.05  # 5% fraudulent
        
        tx = {
            "user_id": random.randint(1, 300),
            "amount": random.uniform(5000, 100000) if is_fraud else random.uniform(100, 10000),
            "currency": "INR",
            "channel": random.choice(["web", "app", "mobile"]),
            "created_at": (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
            "ip_address": f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "device_fingerprint": f"device_{random.randint(1, 150)}",
            "label_is_fraud": int(is_fraud)
        }
        transactions.append(tx)
    
    df = pd.DataFrame(transactions)
    
    # Create output directory
    os.makedirs("data/raw", exist_ok=True)
    
    # Save to CSV
    df.to_csv("data/raw/transactions.csv", index=False)
    
    # Statistics
    fraud_count = df['label_is_fraud'].sum()
    legit_count = len(df) - fraud_count
    
    print(f"✅ Generated {len(df):,} transactions")
    print(f"   Fraudulent: {fraud_count:,} ({fraud_count/len(df)*100:.1f}%)")
    print(f"   Legitimate: {legit_count:,} ({legit_count/len(df)*100:.1f}%)")
    print(f"   Saved to: data/raw/transactions.csv")
    
    return df


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample fraud detection data")
    parser.add_argument("--reviews", type=int, default=5000, help="Number of reviews (default: 5000)")
    parser.add_argument("--transactions", type=int, default=10000, help="Number of transactions (default: 10000)")
    args = parser.parse_args()
    
    print("=" * 70)
    print("FRAUD DETECTION - SAMPLE DATA GENERATOR")
    print("=" * 70)
    print()
    
    # Generate reviews
    reviews_df = generate_reviews(args.reviews)
    
    # Generate transactions
    transactions_df = generate_transactions(args.transactions)
    
    print()
    print("=" * 70)
    print("✅ DATA GENERATION COMPLETE!")
    print("=" * 70)
    print()
    print("📊 Summary:")
    print(f"   Reviews: {len(reviews_df):,} (with actual text content)")
    print(f"   Transactions: {len(transactions_df):,}")
    print()
    print("📁 Files created:")
    print(f"   - data/raw/reviews.csv")
    print(f"   - data/raw/transactions.csv")
    print()
    print("🚀 Next steps:")
    print("   1. python scripts/prepare_data.py")
    print("   2. python scripts/train_reviews.py")
    print("   3. python scripts/train_tx.py")
    print()