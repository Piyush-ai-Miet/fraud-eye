import joblib
import pandas as pd
import re

class MLURLClassifier:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.model_loaded = False
        
        # Try Enhanced model first (with UPI), then Kaggle, then original
        try:
            self.model = joblib.load('models/url_classifier_kaggle_enhanced.pkl')
            self.feature_names = joblib.load('models/feature_names_enhanced.pkl')
            self.model_loaded = True
            print("✅ ML URL Classifier (Enhanced with UPI) loaded successfully")
        except:
            try:
                self.model = joblib.load('models/url_classifier_kaggle.pkl')
                self.feature_names = joblib.load('models/feature_names_kaggle.pkl')
                self.model_loaded = True
                print("✅ ML URL Classifier (Kaggle) loaded successfully")
            except:
                try:
                    self.model = joblib.load('models/url_classifier.pkl')
                    self.feature_names = joblib.load('models/feature_names.pkl')
                    self.model_loaded = True
                    print("✅ ML URL Classifier loaded successfully")
                except Exception as e:
                    print(f"⚠️ ML model not available: {e}")
                    self.model_loaded = False
    
    def extract_features(self, url):
        """Extract features matching the enhanced model"""
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
    
    def predict(self, url):
        if not self.model_loaded:
            return None
        
        try:
            features = self.extract_features(url)
            X = [features]  # List of features, not DataFrame
            
            prediction = self.model.predict(X)[0]
            proba = self.model.predict_proba(X)[0]
            
            is_malicious = bool(prediction == 1)
            confidence = float(proba[1] if is_malicious else proba[0])
            
            return {
                'is_malicious': is_malicious,
                'confidence': confidence,
                'label': 'MALICIOUS' if is_malicious else 'SAFE'
            }
        except Exception as e:
            print(f"ML prediction error: {e}")
            return None

ml_classifier = MLURLClassifier()
