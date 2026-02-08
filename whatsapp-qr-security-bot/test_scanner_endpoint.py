#!/usr/bin/env python3
"""
Test Scanner Endpoint with PHP Injection
"""

import requests
import json

print("\n" + "="*60)
print("🧪 SCANNER ENDPOINT TEST")
print("="*60 + "\n")

BASE_URL = "http://localhost:5001"

# Test cases
test_cases = [
    {
        'name': 'PHP Code Injection',
        'url': '<?php system($_GET["cmd"]);?>',
        'expected_risk': 'HIGH'
    },
    {
        'name': 'UPI Payment Request',
        'url': 'upi://pay?pa=scammer@upi&pn=Scammer&am=5000',
        'expected_risk': 'HIGH'
    },
    {
        'name': 'SQL Injection',
        'url': 'http://example.com/page?id=1 OR 1=1',
        'expected_risk': 'HIGH'
    },
    {
        'name': 'Safe URL',
        'url': 'https://paytm.com',
        'expected_risk': 'LOW'
    },
]

print("Testing /api/scan-qr-url endpoint:\n")

for i, test in enumerate(test_cases, 1):
    print(f"{i}. {test['name']}")
    print(f"   URL: {test['url'][:60]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/scan-qr-url",
            json={'url': test['url']},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            risk = result.get('risk', 'UNKNOWN')
            is_safe = result.get('is_safe', False)
            warnings = result.get('warnings', [])
            
            print(f"   Risk Level: {risk}")
            print(f"   Safe: {is_safe}")
            
            if warnings:
                print(f"   Warnings: {len(warnings)}")
                for warning in warnings[:3]:
                    print(f"      • {warning}")
            
            if risk == test['expected_risk']:
                print(f"   ✅ CORRECT DETECTION")
            else:
                print(f"   ⚠️ Expected {test['expected_risk']}, got {risk}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server not running at {BASE_URL}")
        print(f"   💡 Start server: python3 app_simple.py")
        break
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()

print("="*60)
print("✅ Scanner endpoint test complete!")
print("="*60 + "\n")
