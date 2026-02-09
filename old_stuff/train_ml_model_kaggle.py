import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import re

print("="*60)
print("TRAINING ML MODEL WITH KAGGLE DATASET")
print("="*60)

df = pd.read_csv('data/kaggle_balanced_urls.csv')

print(f"\nDataset: {len(df)} URLs")
print(f"Labels: {df['type'].unique()}")
print(f"\nDistribution:")
print(df['type'].value_counts())

def extract_features(url):
    features = {}
    
    features['url_length'] = len(url)
    features['domain_length'] = len(url.split('/')[2]) if len(url.split('/')) > 2 else len(url)
    
    features['dot_count'] = url.count('.')
    features['slash_count'] = url.count('/')
    features['dash_count'] = url.count('-')
    features['at_count'] = url.count('@')
    features['question_count'] = url.count('?')
    features['ampersand_count'] = url.count('&')
    features['equal_count'] = url.count('=')
    features['underscore_count'] = url.count('_')
    
    features['has_ip'] = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url) else 0
    features['has_https'] = 1 if url.startswith('https://') else 0
    features['has_http'] = 1 if url.startswith('http://') else 0
    
    suspicious_keywords = ['verify', 'urgent', 'otp', 'pin', 'cvv', 'suspended', 'blocked', 
                          'confirm', 'update', 'claim', 'prize', 'free', 'refund', 'login',
                          'signin', 'account', 'secure', 'banking', 'password']
    features['suspicious_keyword_count'] = sum(1 for kw in suspicious_keywords if kw in url.lower())
    
    free_domains = ['.tk', '.ml', '.ga', '.cf', '.gq']
    features['has_free_domain'] = 1 if any(domain in url.lower() for domain in free_domains) else 0
    
    shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
    features['is_shortened'] = 1 if any(short in url.lower() for short in shorteners) else 0
    
    return features

print("\n" + "-"*60)
print("EXTRACTING FEATURES")
print("-"*60)

feature_list = []
for url in df['url']:
    feature_list.append(extract_features(url))

feature_df = pd.DataFrame(feature_list)
X = feature_df.values

# Binary classification: malicious (phishing, malware, defacement) vs benign
y = df['type'].apply(lambda x: 0 if x == 'benign' else 1).values

print(f"Features extracted: {feature_df.shape[1]}")
print(f"Malicious URLs: {sum(y)}")
print(f"Benign URLs: {len(y) - sum(y)}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n" + "-"*60)
print("TRAINING RANDOM FOREST MODEL")
print("-"*60)

model = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=15, min_samples_split=5)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*60}")
print(f"MODEL PERFORMANCE")
print(f"{'='*60}")
print(f"Training Set: {len(y_train)} URLs")
print(f"Test Set: {len(y_test)} URLs")
print(f"Accuracy: {accuracy*100:.2f}%")

print(f"\n{'='*60}")
print("CLASSIFICATION REPORT")
print(f"{'='*60}")
print(classification_report(y_test, y_pred, target_names=['Benign', 'Malicious']))

print(f"\n{'='*60}")
print("CONFUSION MATRIX")
print(f"{'='*60}")
cm = confusion_matrix(y_test, y_pred)
print(cm)
print(f"\nTrue Negatives (Benign correctly identified): {cm[0][0]}")
print(f"False Positives (Benign marked as Malicious): {cm[0][1]}")
print(f"False Negatives (Malicious marked as Benign): {cm[1][0]}")
print(f"True Positives (Malicious correctly identified): {cm[1][1]}")

print(f"\n{'='*60}")
print("TOP 10 IMPORTANT FEATURES")
print(f"{'='*60}")
feature_names = feature_df.columns
importances = model.feature_importances_
indices = np.argsort(importances)[::-1][:10]

for i, idx in enumerate(indices, 1):
    print(f"{i}. {feature_names[idx]}: {importances[idx]:.4f}")

print(f"\n{'='*60}")
print("SAVING MODEL")
print(f"{'='*60}")
joblib.dump(model, 'models/url_classifier_kaggle.pkl')
joblib.dump(feature_names.tolist(), 'models/feature_names_kaggle.pkl')
print("✅ Model saved: models/url_classifier_kaggle.pkl")
print("✅ Features saved: models/feature_names_kaggle.pkl")

print(f"\n{'='*60}")
print("TESTING ON SAMPLE URLs")
print(f"{'='*60}")

test_urls = [
    "https://paytm.com/payment",
    "http://192.168.1.1/verify-otp",
    "http://fake-sbi.tk/urgent-login",
    "https://google.com",
    "http://bit.ly/free-money",
    "br-icloud.com.br",
    "signin.eby.de.zukruygxctzmmqi.civpro.co.za"
]

for url in test_urls:
    features = extract_features(url)
    X_sample = pd.DataFrame([features]).values
    prediction = model.predict(X_sample)[0]
    proba = model.predict_proba(X_sample)[0]
    
    label = "MALICIOUS" if prediction == 1 else "BENIGN"
    confidence = proba[1] if prediction == 1 else proba[0]
    
    print(f"\nURL: {url}")
    print(f"Prediction: {label} (confidence: {confidence*100:.1f}%)")

print(f"\n{'='*60}")
print("TRAINING COMPLETE!")
print(f"{'='*60}\n")
