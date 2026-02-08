from ml_url_classifier import ml_classifier
from app_simple import checker

print("="*60)
print("ML URL CLASSIFIER - INTEGRATION TEST")
print("="*60)

test_urls = [
    "https://paytm.com/payment",
    "http://192.168.1.1/verify-otp",
    "http://fake-sbi.tk/urgent-login",
    "https://google.com",
    "http://bit.ly/free-money",
    "http://sbi-verify.ml/otp-confirm",
    "https://phonepe.com/pay",
    "http://paytm-refund.tk/claim-prize"
]

print(f"\nML Model Status: {'✅ Loaded' if ml_classifier.model_loaded else '❌ Not Available'}\n")

for i, url in enumerate(test_urls, 1):
    print(f"\n{i}. Testing: {url}")
    print("-" * 60)
    
    # ML prediction
    ml_result = ml_classifier.predict(url)
    if ml_result:
        print(f"   ML Prediction: {ml_result['label']}")
        print(f"   ML Confidence: {ml_result['confidence']*100:.1f}%")
    
    # Full check
    result = checker.check_url_safety(url)
    print(f"   Final Risk: {result['risk']}")
    print(f"   Safe: {'✅ YES' if result['is_safe'] else '❌ NO'}")
    print(f"   Message: {result['message_hi']}")
    if result['warnings']:
        print(f"   Warnings: {', '.join(result['warnings'])}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
