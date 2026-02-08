#!/usr/bin/env python3
"""
Test Enhanced ML Model with UPI Payment Requests
"""

from ml_url_classifier import ml_classifier

test_urls = [
    ('upi://pay?pa=scammer@phonepe&am=5000&cu=INR', 'Should be MALICIOUS'),
    ('upi://pay?pa=fraud@paytm&am=2000&mode=02', 'Should be MALICIOUS'),
    ('upi://pay?pa=myshop@paytm&pn=MyShop', 'Should be SAFE'),
    ('https://paytm.com/payment', 'Should be SAFE'),
    ('http://192.168.1.1/verify-kyc', 'Should be MALICIOUS'),
]

print("\n" + "="*60)
print("🧪 Testing Enhanced ML Model")
print("="*60 + "\n")

for url, expected in test_urls:
    result = ml_classifier.predict(url)
    if result:
        status = '✅' if (result['is_malicious'] and 'MALICIOUS' in expected) or (not result['is_malicious'] and 'SAFE' in expected) else '❌'
        print(f"{status} {url[:50]}...")
        print(f"   Prediction: {result['label']} ({result['confidence']*100:.1f}% confidence)")
        print(f"   Expected: {expected}")
        print()
    else:
        print(f"❌ {url[:50]}... - Model failed")
        print()

print("="*60 + "\n")
