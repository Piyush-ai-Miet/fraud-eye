import requests
import json

BASE_URL = "http://localhost:5001"

test_urls = [
    ("https://paytm.com/payment", "SAFE"),
    ("http://fake-sbi.tk/urgent-login", "MALICIOUS"),
    ("http://192.168.1.1/verify-otp", "MALICIOUS"),
    ("http://sbi-verify.ml/otp-confirm", "MALICIOUS"),
    ("https://google.com", "SAFE")
]

print("="*60)
print("WEB API TEST - ML INTEGRATION")
print("="*60)
print("\nMake sure server is running: python3 app_simple.py")
print("Testing URL: http://localhost:5001/api/check-url\n")

for url, expected in test_urls:
    print(f"\nTesting: {url}")
    print(f"Expected: {expected}")
    print("-" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/check-url",
            json={"url": url},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"   Risk: {result.get('risk', 'N/A')}")
            print(f"   Safe: {result.get('is_safe', 'N/A')}")
            print(f"   Message: {result.get('message_hi', 'N/A')}")
            
            if result.get('warnings'):
                print(f"   Warnings:")
                for warning in result['warnings']:
                    print(f"      - {warning}")
            
            if result.get('ml_result'):
                ml = result['ml_result']
                print(f"   ML Result: {ml.get('label')} ({ml.get('confidence', 0)*100:.1f}%)")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Server not running!")
        print("   Start server: python3 app_simple.py")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
