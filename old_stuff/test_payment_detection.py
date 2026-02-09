#!/usr/bin/env python3
"""
Test Payment Request Detection
"""

# Test UPI URLs
test_urls = [
    {
        'name': 'Payment Request with Amount',
        'url': 'upi://pay?pa=merchant@paytm&pn=MerchantName&am=500&cu=INR',
        'expected': 'SEND',
        'expected_amount': '500',
        'expected_risk': True
    },
    {
        'name': 'Payment Request without Amount',
        'url': 'upi://pay?pa=scammer@phonepe&pn=Scammer&cu=INR&mode=02',
        'expected': 'SEND',
        'expected_amount': None,
        'expected_risk': True
    },
    {
        'name': 'Normal Receive QR',
        'url': 'upi://pay?pa=myshop@paytm&pn=MyShop',
        'expected': 'RECEIVE',
        'expected_amount': None,
        'expected_risk': False
    },
    {
        'name': 'Regular URL',
        'url': 'https://paytm.com/payment',
        'expected': 'UNKNOWN',
        'expected_amount': None,
        'expected_risk': False
    }
]

def test_payment_detection():
    """Test payment direction detection"""
    from app_simple import detect_upi_payment_direction
    
    print("\n" + "="*60)
    print("🧪 Testing Payment Request Detection")
    print("="*60 + "\n")
    
    passed = 0
    failed = 0
    
    for test in test_urls:
        print(f"\n📝 Test: {test['name']}")
        print(f"   URL: {test['url'][:60]}...")
        
        direction, message, amount, is_payment_request = detect_upi_payment_direction(test['url'])
        
        print(f"   Direction: {direction}")
        print(f"   Amount: {amount}")
        print(f"   Is Payment Request: {is_payment_request}")
        print(f"   Message: {message}")
        
        # Verify results
        if direction == test['expected'] and is_payment_request == test['expected_risk']:
            if test['expected_amount']:
                if amount == test['expected_amount']:
                    print("   ✅ PASSED")
                    passed += 1
                else:
                    print(f"   ❌ FAILED - Expected amount: {test['expected_amount']}, Got: {amount}")
                    failed += 1
            else:
                print("   ✅ PASSED")
                passed += 1
        else:
            print(f"   ❌ FAILED - Expected: {test['expected']}, Got: {direction}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = test_payment_detection()
    exit(0 if success else 1)
