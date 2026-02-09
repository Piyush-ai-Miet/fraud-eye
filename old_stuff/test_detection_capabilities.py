#!/usr/bin/env python3
"""
Test our detection capabilities with various attack patterns
"""

import requests
import json

SERVER_URL = 'http://localhost:5001'

test_cases = [
    {
        'name': 'SQL Injection Attack',
        'url': "http://example.com/page?id=1' OR '1'='1",
        'should_detect': 'SQL Injection'
    },
    {
        'name': 'XSS Attack',
        'url': 'http://example.com/search?q=<script>alert("XSS")</script>',
        'should_detect': 'XSS'
    },
    {
        'name': 'Suspicious Free Domain (.tk)',
        'url': 'http://free-money-scam.tk',
        'should_detect': 'Suspicious domain'
    },
    {
        'name': 'IP Address URL',
        'url': 'http://192.168.1.1/login',
        'should_detect': 'IP address'
    },
    {
        'name': 'No HTTPS',
        'url': 'http://banking-site.com/login',
        'should_detect': 'No HTTPS'
    },
    {
        'name': 'Legitimate Site (Google)',
        'url': 'https://google.com',
        'should_detect': 'SAFE'
    }
]

print("\n" + "="*80)
print("🧪 Testing Detection Capabilities")
print("="*80)

for i, test in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] {test['name']}")
    print(f"   URL: {test['url']}")
    print(f"   Should Detect: {test['should_detect']}")
    
    try:
        response = requests.post(
            f'{SERVER_URL}/api/check-url',
            json={'url': test['url']},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n   Result:")
            print(f"      Risk: {result.get('risk')}")
            print(f"      Safe: {result.get('is_safe')}")
            
            warnings = result.get('warnings', [])
            print(f"      Warnings: {len(warnings)}")
            
            # Check if expected pattern was detected
            detected = False
            for warning in warnings:
                print(f"         - {warning}")
                if test['should_detect'].lower() in warning.lower():
                    detected = True
            
            if test['should_detect'] == 'SAFE':
                if result.get('is_safe'):
                    print(f"   ✅ CORRECT - Detected as safe")
                else:
                    print(f"   ❌ WRONG - Should be safe")
            else:
                if detected or not result.get('is_safe'):
                    print(f"   ✅ CORRECT - Detected threat")
                else:
                    print(f"   ❌ WRONG - Missed threat")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("✅ Test Complete")
print("="*80 + "\n")
