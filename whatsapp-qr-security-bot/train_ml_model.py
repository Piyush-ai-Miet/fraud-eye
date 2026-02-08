import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import re

# Load dataset
df = pd.read_csv('data/malicious_urls.csv')

# Feature extraction function
def extract_features(url):
    features = {}
    
    # Length features
    features['url_length'] = len(url)
    features['domain_length'] = len(url.split('/')[2]) if len(url.split('/')) > 2 else 0
    
    # Character counts
    features['dot_count'] = url.count('.')
    features['slash_count'] = url.count('/')
    features['dash_count'] = url.count('-')
    features['at_count'] = url.count('@')
    features['question_count'] = url.count('?')
    features['ampersand_count'] = url.count('&')
    
    # Suspicious patterns
    features['has_ip'] = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0
    features['has_https'] = 1 if url.startswith('https://') else 0
    features['has_http'] = 1 if url.startswith('http://') else 0
    
    # Suspicious keywords
    suspicious_keywords = ['verify', 'urgent', 'otp', 'pin', 'cvv', 'suspended', 'blocked', 
                          'confirm', 'update', 'claim', 'prize', 'free', 'refund']
    features['suspicious_keyword_count'] = sum(1 for kw in suspicious_keywords if kw in url.lower())
    
    # Free domains
    free_domains = ['.tk', '.ml', '.ga', '.cf', '.gq']
    features['has_free_domain'] = 1 if any(domain in url.lower() for domain in free_domains) else 0
    
    # URL shorteners
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co']
    features['is_shortened'] = 1 if any(short in url.lower() for short in shorteners) else 0
    
    return features

# Extract features for all URLs
print("Extracting features...")
feature_list = []
for url in df['url']:
    feature_list.append(extract_features(url))

feature_df = pd.DataFrame(feature_list)
X = feature_df.values

# Labels: malicious/suspicious=1, safe=0 (binary classification)
y = df['label'].apply(lambda x: 1 if x in ['malicious', 'suspicious'] else 0).values

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train Random Forest
print("\nTraining Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
print(f"\n{'='*60}")
print(f"MODEL PERFORMANCE")
print(f"{'='*60}")
print(f"Accuracy: {accuracy*100:.2f}%")
print(f"\nTest Set Size: {len(y_test)} URLs")
print(f"Training Set Size: {len(y_train)} URLs")

# Detailed metrics
print(f"\n{'='*60}")
print("CLASSIFICATION REPORT")
print(f"{'='*60}")
print(classification_report(y_test, y_pred, target_names=['Safe', 'Malicious/Suspicious']))

# Confusion Matrix
print(f"\n{'='*60}")
print("CONFUSION MATRIX")
print(f"{'='*60}")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Feature importance
print(f"\n{'='*60}")
print("TOP 10 IMPORTANT FEATURES")
print(f"{'='*60}")
feature_names = feature_df.columns
importances = model.feature_importances_
indices = np.argsort(importances)[::-1][:10]

for i, idx in enumerate(indices, 1):
    print(f"{i}. {feature_names[idx]}: {importances[idx]:.4f}")

# Save model
print(f"\n{'='*60}")
print("SAVING MODEL")
print(f"{'='*60}")
joblib.dump(model, 'models/url_classifier.pkl')
joblib.dump(feature_names.tolist(), 'models/feature_names.pkl')
print("✅ Model saved: models/url_classifier.pkl")
print("✅ Features saved: models/feature_names.pkl")

# Test on sample URLs
print(f"\n{'='*60}")
print("TESTING ON SAMPLE URLs")
print(f"{'='*60}")

test_urls = [
    "https://paytm.com/payment",
    "http://192.168.1.1/verify-otp",
    "http://fake-sbi.tk/urgent-login",
    "https://google.com",
    "http://bit.ly/free-money"
]

for url in test_urls:
    features = extract_features(url)
    X_sample = pd.DataFrame([features]).values
    prediction = model.predict(X_sample)[0]
    proba = model.predict_proba(X_sample)[0]
    
    label = "MALICIOUS/SUSPICIOUS" if prediction == 1 else "SAFE"
    confidence = proba[1] if prediction == 1 else proba[0]
    
    print(f"\nURL: {url}")
    print(f"Prediction: {label} (confidence: {confidence*100:.1f}%)")

print(f"\n{'='*60}")
print("TRAINING COMPLETE!")
print(f"{'='*60}\n")
