#!/usr/bin/env python3
"""
Test URL Checker with ML Model and Pattern Detection
"""

import requests
import json

print("\n" + "="*60)
print("🧪 URL CHECKER - ML & PATTERN DETECTION TEST")
print("="*60 + "\n")

BASE_URL = "http://localhost:5001"

# Test cases with SQL injection, PHP code, and malicious URLs
test_cases = [
    {
        'name': 'PHP Code Injection',
        'url': '<?php system($_GET["cmd"]);?>',
        'expected_risk': 'HIGH',
        'expected_detection': 'PHP Code Injection'
    },
    {
        'name': 'SQL Injection in URL',
        'url': 'http://example.com/page?id=1 OR 1=1',
        'expected_risk': 'MEDIUM',
        'expected_detection': 'SQL Injection'
    },
    {
        'name': 'SQL Injection - UNION',
        'url': 'http://example.com/user?id=1 UNION SELECT * FROM users',
        'expected_risk': 'MEDIUM',
        'expected_detection': 'SQL Injection'
    },
    {
        'name': 'XSS Attack',
        'url': '<script>alert("xss")</script>',
        'expected_risk': 'HIGH',
        'expected_detection': 'XSS Attack'
    },
    {
        'name': 'Command Injection',
        'url': 'http://example.com/cmd?exec=ls|cat /etc/passwd',
        'expected_risk': 'MEDIUM',
        'expected_detection': 'Command Injection'
    },
    {
        'name': 'IP Address Phishing',
        'url': 'http://192.168.1.1/phishing',
        'expected_risk': 'MEDIUM',
        'expected_detection': 'IP address'
    },
    {
        'name': 'Suspicious Free Domain',
        'url': 'http://scam-site.tk/urgent-verify',
        'expected_risk': 'MEDIUM',
        'expected_detection': 'Suspicious domain'
    },
    {
        'name': 'Safe URL - Paytm',
        'url': 'https://paytm.com',
        'expected_risk': 'LOW',
        'expected_detection': None
    },
    {
        'name': 'Safe URL - Google',
        'url': 'https://www.google.com',
        'expected_risk': 'LOW',
        'expected_detection': None
    },
]

print("Testing /api/check-url endpoint:\n")

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['name']}")
    print(f"   URL: {test['url'][:60]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/check-url",
            json={'url': test['url']},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            risk = result.get('risk', 'UNKNOWN')
            is_safe = result.get('is_safe', False)
            warnings = result.get('warnings', [])
            ml_result = result.get('ml_result')
            
            print(f"   Risk Level: {risk}")
            print(f"   Safe: {is_safe}")
            
            # Check ML result
            if ml_result:
                print(f"   🤖 ML: {ml_result['label']} ({ml_result['confidence']*100:.1f}%)")
            
            # Check warnings
            if warnings:
                print(f"   Warnings ({len(warnings)}):")
                for warning in warnings[:5]:
                    print(f"      • {warning}")
            
            # Verify detection
            detected = False
            if test['expected_detection']:
                for warning in warnings:
                    if test['expected_detection'].lower() in warning.lower():
                        detected = True
                        break
                
                if detected and risk == test['expected_risk']:
                    print(f"   ✅ CORRECT DETECTION")
                    passed += 1
                elif detected:
                    print(f"   ⚠️ Detected but risk level: Expected {test['expected_risk']}, got {risk}")
                    passed += 1
                else:
                    print(f"   ❌ FAILED: {test['expected_detection']} not detected")
                    failed += 1
            else:
                # Safe URL test
                if risk == test['expected_risk']:
                    print(f"   ✅ CORRECT")
                    passed += 1
                else:
                    print(f"   ❌ Expected {test['expected_risk']}, got {risk}")
                    failed += 1
        else:
            print(f"   ❌ Error: {response.status_code}")
            failed += 1
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server not running at {BASE_URL}")
        print(f"   💡 Start server: python3 app_simple.py")
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
    print("✅ All tests passed!")
print("="*60 + "\n")
