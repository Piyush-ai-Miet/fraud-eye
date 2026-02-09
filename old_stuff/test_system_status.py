#!/usr/bin/env python3
"""
System Status Checker - Check all modules and ML models
"""

print("\n" + "="*60)
print("🔍 FRAUD EYE - SYSTEM STATUS CHECK")
print("="*60 + "\n")

# 1. Check Scan Logger
try:
    from scan_logger import log_scan, get_scan_history, get_scan_stats
    print("✅ Scan Logger: LOADED")
except Exception as e:
    print(f"❌ Scan Logger: FAILED - {e}")

# 2. Check Face Auth
try:
    from face_auth import verify_face, create_session, verify_session, logout_session
    print("✅ Face Authentication: LOADED")
except Exception as e:
    print(f"❌ Face Authentication: FAILED - {e}")

# 3. Check 2-Step Auth
try:
    from admin_credentials import verify_credentials, is_face_registered, mark_face_registered
    from face_recognition_simple import register_admin_face_multi, verify_face as verify_face_opencv, get_registration_status
    print("✅ 2-Step Authentication: LOADED")
except Exception as e:
    print(f"❌ 2-Step Authentication: FAILED - {e}")

# 4. Check QR Scanner
try:
    from simple_qr_scanner import scan_qr_from_upload, QR_SCANNING_AVAILABLE
    if QR_SCANNING_AVAILABLE:
        print("✅ QR Code Scanner: LOADED")
    else:
        print("⚠️  QR Code Scanner: LOADED (but dependencies missing)")
except Exception as e:
    print(f"❌ QR Code Scanner: FAILED - {e}")

# 5. Check Pattern Detector
try:
    from malicious_patterns import detector as pattern_detector
    print("✅ Malicious Pattern Detector: LOADED")
    print(f"   └─ Kaggle Database: {len(pattern_detector.kaggle_urls) if hasattr(pattern_detector, 'kaggle_urls') else 0} URLs")
except Exception as e:
    print(f"❌ Malicious Pattern Detector: FAILED - {e}")

# 6. Check ML URL Classifier
try:
    from ml_url_classifier import ml_classifier
    if ml_classifier.model_loaded:
        print("✅ ML URL Classifier: LOADED")
        print(f"   └─ Model Type: Enhanced with UPI")
    else:
        print("❌ ML URL Classifier: Model not loaded")
except Exception as e:
    print(f"❌ ML URL Classifier: FAILED - {e}")

# 7. Check Real-time URL Checker
try:
    from realtime_url_checker import realtime_checker
    print("✅ Real-time URL Checker: LOADED")
    print(f"   └─ APIs: VirusTotal, Dangerous.domains, URLScan.io")
except Exception as e:
    print(f"❌ Real-time URL Checker: FAILED - {e}")

# 8. Check Audio Fraud Classifier
try:
    from audio_fraud_classifier import audio_classifier
    if audio_classifier.model_loaded:
        print("✅ Audio Fraud Classifier: LOADED")
        print(f"   └─ Model: Scikit-learn based")
    else:
        print("⚠️  Audio Fraud Classifier: LOADED (but model not found)")
except Exception as e:
    print(f"❌ Audio Fraud Classifier: FAILED - {e}")

# 9. Check ML Models Files
import os
print("\n" + "="*60)
print("📦 ML MODEL FILES")
print("="*60)

models_dir = "models"
if os.path.exists(models_dir):
    models = os.listdir(models_dir)
    for model in sorted(models):
        if model.endswith('.pkl'):
            size = os.path.getsize(os.path.join(models_dir, model))
            size_mb = size / (1024 * 1024)
            print(f"✅ {model:<40} ({size_mb:.2f} MB)")
else:
    print("❌ Models directory not found")

# 10. Check Data Files
print("\n" + "="*60)
print("📁 DATA FILES")
print("="*60)

data_files = [
    "data/kaggle_balanced_urls.csv",
    "data/malicious_urls.csv",
    "data/latest_scams.json",
    "data/scan_history.json",
    "data/indian_scam_patterns.txt",
    "data/phishing_keywords.txt"
]

for file in data_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        size_kb = size / 1024
        print(f"✅ {file:<40} ({size_kb:.2f} KB)")
    else:
        print(f"❌ {file:<40} (NOT FOUND)")

print("\n" + "="*60)
print("✅ SYSTEM STATUS CHECK COMPLETE")
print("="*60 + "\n")
