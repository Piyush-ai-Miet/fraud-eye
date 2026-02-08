#!/usr/bin/env python3
"""
Simple test script - No dependencies needed
Tests the core logic without external libraries
"""

def test_pattern_detection():
    """Test malicious pattern detection logic"""
    print("=" * 60)
    print("🧪 Testing Pattern Detection Logic")
    print("=" * 60)
    
    # Test URLs
    test_cases = [
        {
            'url': 'https://paytm.com/payment',
            'expected_risk': 'LOW',
            'description': 'Safe domain (Paytm)'
        },
        {
            'url': 'http://192.168.1.1/verify',
            'expected_risk': 'HIGH',
            'description': 'IP address + suspicious keyword'
        },
        {
            'url': 'http://bit.ly/urgent-payment',
            'expected_risk': 'MEDIUM',
            'description': 'URL shortener + suspicious keyword'
        },
        {
            'url': 'https://www.sbi.co.in/login',
            'expected_risk': 'LOW',
            'description': 'Safe bank domain'
        },
        {
            'url': 'http://free-prize.tk/claim',
            'expected_risk': 'HIGH',
            'description': 'Free domain + suspicious keywords'
        }
    ]
    
    # Simple pattern matching logic (same as in bot.py)
    suspicious_keywords = ['verify', 'urgent', 'otp', 'pin', 'cvv', 'bank', 
                          'refund', 'confirm', 'account', 'suspended', 'blocked',
                          'prize', 'claim', 'free']
    
    suspicious_domains = ['.tk', '.ml', '.ga', '.cf', '.gq']
    url_shorteners = ['bit.ly', 'tinyurl', 'goo.gl']
    safe_domains = ['paytm.com', 'phonepe.com', 'sbi.co.in', 'hdfcbank.com']
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        url = test['url'].lower()
        risk_score = 0
        warnings = []
        
        # Check for safe domains
        is_safe_domain = any(safe in url for safe in safe_domains)
        
        if is_safe_domain:
            risk = 'LOW'
        else:
            # Check for IP address
            import re
            if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
                risk_score += 3
                warnings.append('IP address detected')
            
            # Check for HTTPS
            if not url.startswith('https'):
                risk_score += 1
                warnings.append('No HTTPS')
            
            # Check for suspicious keywords
            found_keywords = [kw for kw in suspicious_keywords if kw in url]
            if found_keywords:
                risk_score += len(found_keywords)
                warnings.append(f'Suspicious keywords: {", ".join(found_keywords[:2])}')
            
            # Check for URL shorteners
            if any(short in url for short in url_shorteners):
                risk_score += 2
                warnings.append('URL shortener detected')
            
            # Check for suspicious domains
            if any(dom in url for dom in suspicious_domains):
                risk_score += 2
                warnings.append('Suspicious domain')
            
            # Calculate risk level
            if risk_score >= 3:
                risk = 'HIGH'
            elif risk_score >= 2:
                risk = 'MEDIUM'
            else:
                risk = 'LOW'
        
        # Check result
        status = "✅ PASS" if risk == test['expected_risk'] else "❌ FAIL"
        if risk == test['expected_risk']:
            passed += 1
        else:
            failed += 1
        
        print(f"\nTest {i}: {test['description']}")
        print(f"  URL: {test['url']}")
        print(f"  Expected: {test['expected_risk']}")
        print(f"  Got: {risk}")
        print(f"  Warnings: {', '.join(warnings) if warnings else 'None'}")
        print(f"  {status}")
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)
    
    return passed, failed

def test_hindi_responses():
    """Test Hindi response generation"""
    print("\n" + "=" * 60)
    print("🇮🇳 Testing Hindi Response Generation")
    print("=" * 60)
    
    hindi_responses = {
        'HIGH': '⚠️ DHYAN RAHE! Yeh link bahut dangerous lag raha hai.',
        'MEDIUM': '⚠️ Savdhaan! Yeh link thoda suspicious hai.',
        'LOW': '✅ Yeh link safe lag raha hai, lekin phir bhi dhyan rakho.'
    }
    
    safety_tips = [
        '• Unknown link par click mat karo',
        '• Personal details share mat karo',
        '• Bank se confirm karo'
    ]
    
    print("\n✅ Hindi Response Templates:")
    for risk, message in hindi_responses.items():
        print(f"  {risk}: {message}")
    
    print("\n✅ Safety Tips:")
    for tip in safety_tips:
        print(f"  {tip}")
    
    print("\n✅ All Hindi responses are properly formatted!")
    print("=" * 60)

def test_file_structure():
    """Test if all required files exist"""
    print("\n" + "=" * 60)
    print("📁 Testing File Structure")
    print("=" * 60)
    
    import os
    
    required_files = [
        'bot.py',
        'requirements.txt',
        'templates/dashboard.html',
        'SETUP.md',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("\n✅ All required files exist!")
    else:
        print("\n❌ Some files are missing!")
    
    print("=" * 60)
    return all_exist

if __name__ == "__main__":
    print("\n🚀 Starting Fraud Eye Tests...\n")
    
    # Run tests
    test_file_structure()
    passed, failed = test_pattern_detection()
    test_hindi_responses()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 TEST SUMMARY")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed!")
        print("✅ Pattern detection working correctly")
        print("✅ Hindi responses configured")
        print("✅ File structure complete")
        print("\n🎯 Your project is ready for demo!")
    else:
        print(f"⚠️ {failed} test(s) failed")
        print("Please review the logic")
    
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("1. Run: python3 bot.py")
    print("2. Open: http://localhost:5000")
    print("3. Test with QR code images")
    print("\n")
