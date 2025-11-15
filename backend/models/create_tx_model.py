"""
Create a dummy transaction model for testing
Replace this with your actual trained model
"""

import joblib
import os
from sklearn.ensemble import IsolationForest
import numpy as np

# Create dummy training data
np.random.seed(42)
X_train = np.random.randn(1000, 10)

# Train Isolation Forest
model = IsolationForest(
    contamination=0.1,
    random_state=42,
    n_estimators=100
)
model.fit(X_train)

# Feature names
feature_names = [
    'amount',
    'hour',
    'day_of_week',
    'user_tx_count',
    'user_avg_amount',
    'amount_vs_avg',
    'velocity_1h',
    'velocity_24h',
    'ip_risk_score',
    'device_risk_score'
]

# Save model artifact
artifact = {
    'pipe': model,
    'features': feature_names
}

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'tx_model.pkl')

joblib.dump(artifact, output_path)
print(f"Transaction model saved to: {output_path}")
print(f"Features: {feature_names}")