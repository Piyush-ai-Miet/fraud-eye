#!/usr/bin/env python3
"""
Retrain ML Model with UPI Payment Request Data
Combines existing Kaggle dataset with UPI-specific patterns
"""

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import re

def extract_url_features(url):
    """Extract features from URL"""
    features = []
    
    # Length
    features.append(len(url))
    
    # Count special characters
    features.append(url.count('.'))
    features.append(url.count('/'))
    features.append(url.count('?'))
    features.append(url.count('='))
    features.append(url.count('&'))
    features.append(url.count('-'))
    features.append(url.count('_'))
    
    # UPI-specific features
    features.append(1 if 'upi://' in url.lower() else 0)
    features.append(1 if 'am=' in url.lower() else 0)  # Amount parameter
    features.append(1 if 'mode=02' in url.lower() else 0)  # Collect mode
    features.append(1 if 'purpose=' in url.lower() else 0)
    features.append(1 if 'orgid=' in url.lower() else 0)
    
    # Has HTTPS
    features.append(1 if url.startswith('https://') else 0)
    
    # Has IP address
    features.append(1 if re.match(r'.*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*', url) else 0)
    
    # Suspicious TLDs
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq']
    features.append(1 if any(tld in url.lower() for tld in suspicious_tlds) else 0)
    
    return features

print("\n" + "="*60)
print("🔄 Retraining ML Model with UPI Payment Request Data")
print("="*60 + "\n")

# Load existing Kaggle dataset
print("📂 Loading existing Kaggle dataset...")
try:
    kaggle_df = pd.read_csv('data/kaggle_balanced_urls.csv')
    print(f"   ✅ Loaded {len(kaggle_df)} URLs from Kaggle dataset")
except:
    print("   ⚠️ Kaggle dataset not found, using only UPI data")
    kaggle_df = pd.DataFrame(columns=['url', 'label'])

# Load UPI payment request dataset
print("📂 Loading UPI payment request dataset...")
upi_df = pd.read_csv('data/upi_payment_requests.csv')
print(f"   ✅ Loaded {len(upi_df)} UPI URLs")

# Combine datasets
print("\n🔗 Combining datasets...")
combined_df = pd.concat([kaggle_df, upi_df], ignore_index=True)
print(f"   ✅ Total URLs: {len(combined_df)}")
print(f"   - Malicious: {len(combined_df[combined_df['label'] == 'malicious'])}")
print(f"   - Benign: {len(combined_df[combined_df['label'] == 'benign'])}")

# Extract features
print("\n🔧 Extracting features...")
X = []
y = []

for idx, row in combined_df.iterrows():
    features = extract_url_features(row['url'])
    X.append(features)
    y.append(1 if row['label'] == 'malicious' else 0)

print(f"   ✅ Extracted features for {len(X)} URLs")

# Split data
print("\n✂️ Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"   ✅ Train: {len(X_train)}, Test: {len(X_test)}")

# Train model
print("\n🤖 Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print("   ✅ Model trained!")

# Evaluate
print("\n📊 Evaluating model...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   ✅ Accuracy: {accuracy*100:.2f}%")

# Test on UPI examples
print("\n🧪 Testing on UPI examples...")
test_urls = [
    ('upi://pay?pa=scammer@phonepe&am=5000&cu=INR', 'malicious'),
    ('upi://pay?pa=myshop@paytm&pn=MyShop', 'benign'),
    ('upi://pay?pa=fraud@paytm&am=2000&mode=02', 'malicious'),
]

for url, expected in test_urls:
    features = extract_url_features(url)
    prediction = model.predict([features])[0]
    result = 'malicious' if prediction == 1 else 'benign'
    status = '✅' if result == expected else '❌'
    print(f"   {status} {url[:50]}... → {result}")

# Save model
print("\n💾 Saving enhanced model...")
with open('models/url_classifier_kaggle_enhanced.pkl', 'wb') as f:
    pickle.dump(model, f)
print("   ✅ Model saved: models/url_classifier_kaggle_enhanced.pkl")

# Save feature names for reference
feature_names = [
    'url_length', 'dot_count', 'slash_count', 'question_count', 
    'equals_count', 'ampersand_count', 'dash_count', 'underscore_count',
    'is_upi', 'has_amount', 'has_mode_02', 'has_purpose', 'has_orgid',
    'has_https', 'has_ip', 'has_suspicious_tld'
]

with open('models/feature_names_enhanced.pkl', 'wb') as f:
    pickle.dump(feature_names, f)

print("\n" + "="*60)
print("✅ Model Retraining Complete!")
print("="*60)
print("\n📝 Summary:")
print(f"   - Total URLs trained: {len(combined_df)}")
print(f"   - UPI URLs added: {len(upi_df)}")
print(f"   - Final accuracy: {accuracy*100:.2f}%")
print(f"   - Model file: models/url_classifier_kaggle_enhanced.pkl")
print("\n" + "="*60 + "\n")
