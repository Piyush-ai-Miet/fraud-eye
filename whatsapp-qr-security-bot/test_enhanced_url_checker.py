#!/usr/bin/env python3
"""
Test Enhanced URL Checker with Kaggle Database and Scraping
"""

import requests
import json

print("\n" + "="*60)
print("🧪 ENHANCED URL CHECKER TEST")
print("="*60 + "\n")

BASE_URL = "http://localhost:5001"

# Test cases including LinkedIn phishing and Kaggle URLs
test_cases = [
    {
        'name': 'LinkedIn Phishing (Fake Domain)',
        'url': 'uk.linkedin.com/pub/steve-rubenstein/8/718/755',
        'expected_risk': 'HIGH',
        'reason': 'LinkedIn in URL but not linkedin.com domain'
    },
    {
        'name': 'Real LinkedIn (Safe)',
        'url': 'https://www.linkedin.com/in/johndoe',
        'expected_risk': 'LOW',
        'reason': 'Official LinkedIn domain'
    },
    {
        'name': 'Kaggle Phishing URL',
        'url': 'mutanki.net',
        'expected_risk': 'HIGH',
        'reason': 'Known phishing site in Kaggle database'
    },
    {
        'name': 'Kaggle Malware URL',
        'url': 'awcookcement.com/',
        'expected_risk': 'HIGH',
        'reason': 'Known malware site in Kaggle database'
    },
    {
        'name': 'PHP Code Injection',
        'url': '<?php system($_GET["cmd"]);?>',
        'expected_risk': 'HIGH',
        'reason': 'PHP code injection pattern'
    },
    {
        'name': 'SQL Injection',
        'url': 'http://example.com/page?id=1 OR 1=1',
        'expected_risk': 'HIGH',
        'reason': 'SQL injection pattern'
    },
    {
        'name': 'Safe URL - Paytm',
        'url': 'https://paytm.com',
        'expected_risk': 'LOW',
        'reason': 'Official Paytm domain'
    },
]

print("Testing /api/check-url endpoint:\n")

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['name']}")
    print(f"   URL: {test['url'][:60]}...")
    print(f"   Reason: {test['reason']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/check-url",
            json={'url': test['url']},
            timeout=10
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
            if risk == test['expected_risk']:
                print(f"   ✅ CORRECT DETECTION")
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
