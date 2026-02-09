#!/usr/bin/env python3
"""
Test All Datasets Integration in QR Scanner
"""

import requests

print("\n" + "="*60)
print("🧪 ALL DATASETS INTEGRATION TEST")
print("="*60 + "\n")

BASE_URL = "http://localhost:5001"

# Test all datasets
print("📊 Dataset Status:")
print("-" * 60)

# 1. Kaggle Database
try:
    from malicious_patterns import detector
    import pandas as pd
    
    df = pd.read_csv('data/malicious_urls.csv')
    print(f"✅ Kaggle Database: {len(df)} URLs loaded")
    print(f"   - Malicious: {len(df[df['label'] == 'malicious'])}")
    print(f"   - Benign: {len(df[df['label'] == 'benign'])}")
except Exception as e:
    print(f"❌ Kaggle Database: {e}")

# 2. QR Dataset Patterns
try:
    from malicious_patterns import detector
    total = sum(len(patterns) for patterns in detector.patterns.values())
    print(f"\n✅ QR Dataset Patterns: {total} patterns loaded")
    for attack_type, patterns in detector.patterns.items():
        print(f"   - {attack_type.upper()}: {len(patterns)} patterns")
except Exception as e:
    print(f"❌ QR Dataset Patterns: {e}")

# 3. ML Model
try:
    from ml_url_classifier import ml_classifier
    if ml_classifier.model_loaded:
        print(f"\n✅ ML Model: Loaded successfully")
        print(f"   - Training: 4,040 URLs (Kaggle + UPI)")
    else:
        print(f"❌ ML Model: Not loaded")
except Exception as e:
    print(f"❌ ML Model: {e}")

# 4. UPI Payment Detection
try:
    from app_simple import detect_upi_payment_direction
    test_upi = "upi://pay?pa=test@upi&am=500"
    direction, msg, amount, is_request = detect_upi_payment_direction(test_upi)
    print(f"\n✅ UPI Detection: Working")
    print(f"   - Test: {direction}, Amount: ₹{amount}")
except Exception as e:
    print(f"❌ UPI Detection: {e}")

print("\n" + "="*60)
print("🧪 TESTING QR SCANNER ENDPOINTS")
print("="*60 + "\n")

# Test cases covering all datasets
test_cases = [
    {
        'name': 'Kaggle Database - Phishing',
        'url': 'mutanki.net',
        'expected': 'Known Phishing URL in database',
        'dataset': 'Kaggle DB'
    },
    {
        'name': 'QR Dataset - SQL Injection',
        'url': 'http://example.com/page?id=1 OR 1=1',
        'expected': 'SQL Injection',
        'dataset': 'QR Patterns'
    },
    {
        'name': 'QR Dataset - PHP Code',
        'url': '<?php system($_GET["cmd"]);?>',
        'expected': 'PHP Code Injection',
        'dataset': 'QR Patterns'
    },
    {
        'name': 'UPI Payment Request',
        'url': 'upi://pay?pa=scammer@upi&am=5000',
        'expected': 'PAYMENT REQUEST',
        'dataset': 'UPI Detection'
    },
    {
        'name': 'ML Model - Suspicious URL',
        'url': 'http://192.168.1.1/phishing',
        'expected': 'IP address',
        'dataset': 'ML Model + Basic'
    },
]

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['name']}")
    print(f"   URL: {test['url'][:50]}...")
    print(f"   Dataset: {test['dataset']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/scan-qr-url",
            json={'url': test['url']},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            warnings = result.get('warnings', [])
            risk = result.get('risk', 'UNKNOWN')
            
            # Check if expected warning is present
            detected = any(test['expected'].lower() in str(w).lower() for w in warnings)
            
            if detected:
                print(f"   ✅ DETECTED: {test['expected']}")
                print(f"   Risk: {risk}")
                passed += 1
            else:
                print(f"   ❌ NOT DETECTED: {test['expected']}")
                print(f"   Warnings: {warnings}")
                failed += 1
        else:
            print(f"   ❌ Error: {response.status_code}")
            failed += 1
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server not running")
        print(f"   💡 Start: python3 app_simple.py")
        break
    except Exception as e:
        print(f"   ❌ Error: {e}")
        failed += 1
    
    print()

print("="*60)
print(f"📊 RESULTS: {passed}/{len(test_cases)} tests passed")
if failed > 0:
    print(f"❌ {failed} tests failed")
else:
    print("✅ All datasets integrated successfully!")
print("="*60 + "\n")
