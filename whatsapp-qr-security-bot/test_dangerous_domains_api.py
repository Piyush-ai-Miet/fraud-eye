#!/usr/bin/env python3
"""
Test dangerous.domains API integration with main app
"""

import requests
import json

# Test URLs
test_urls = [
    {
        'url': 'https://google.com',
        'expected': 'SAFE',
        'description': 'Legitimate website'
    },
    {
        'url': 'https://paytm.com',
        'expected': 'SAFE',
        'description': 'Legitimate payment site'
    },
    {
        'url': 'http://malicious-phishing-site.tk',
        'expected': 'SUSPICIOUS',
        'description': 'Suspicious free domain'
    }
]

print("\n" + "="*60)
print("🧪 Testing Dangerous.domains API Integration")
print("="*60)

for test in test_urls:
    print(f"\n📝 Testing: {test['description']}")
    print(f"   URL: {test['url']}")
    print(f"   Expected: {test['expected']}")
    
    try:
        response = requests.post(
            'http://localhost:5001/api/check-url',
            json={'url': test['url']},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n   ✅ Result:")
            print(f"      Risk: {result.get('risk', 'N/A')}")
            print(f"      Safe: {result.get('is_safe', 'N/A')}")
            print(f"      Message: {result.get('message_hi', 'N/A')}")
            
            # Check if third-party API was used
            if result.get('realtime_result'):
                rt = result['realtime_result']
                print(f"\n   🌐 Third-Party API Results:")
                print(f"      Overall Verdict: {rt.get('overall_verdict', 'N/A')}")
                print(f"      Total Checks: {rt.get('summary', {}).get('total_checks', 0)}")
                
                # Show individual service results
                for service, check in rt.get('checks', {}).items():
                    print(f"\n      {service.upper()}:")
                    print(f"         Verdict: {check.get('verdict', 'N/A')}")
                    print(f"         Message: {check.get('message', 'N/A')}")
            
            # Show warnings
            if result.get('warnings'):
                print(f"\n   ⚠️ Warnings:")
                for warning in result['warnings']:
                    print(f"      - {warning}")
            
            print(f"\n   {'✅ PASS' if result.get('risk') == test['expected'] or (test['expected'] == 'SAFE' and result.get('is_safe')) else '⚠️ DIFFERENT THAN EXPECTED'}")
        else:
            print(f"   ❌ Error: HTTP {response.status_code}")
            print(f"      {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception: {e}")

print("\n" + "="*60)
print("✅ Test Complete!")
print("="*60)
print("\n💡 Note: dangerous.domains API is working if you see")
print("   'dangerous_domains' in the Third-Party API Results")
print("="*60 + "\n")
