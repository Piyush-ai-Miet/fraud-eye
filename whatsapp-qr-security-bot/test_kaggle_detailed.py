#!/usr/bin/env python3
"""
Detailed test to see why malicious URLs are not being detected
"""

import requests
import json

SERVER_URL = 'http://localhost:5001'

# Test one known phishing URL
test_url = 'http://br-icloud.com.br'

print(f"\n🔍 Testing: {test_url}")
print(f"Expected: PHISHING (should be HIGH RISK)")
print("="*80)

try:
    response = requests.post(
        f'{SERVER_URL}/api/check-url',
        json={'url': test_url},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n📊 Result:")
        print(json.dumps(result, indent=2))
        
        print(f"\n🎯 Key Findings:")
        print(f"   Risk Level: {result.get('risk')}")
        print(f"   Is Safe: {result.get('is_safe')}")
        print(f"   Domain: {result.get('domain')}")
        
        print(f"\n⚠️ Warnings ({len(result.get('warnings', []))}):")
        for warning in result.get('warnings', []):
            print(f"   - {warning}")
        
        print(f"\n🌐 Third-Party API Results:")
        if result.get('realtime_result'):
            rt = result['realtime_result']
            print(f"   Overall Verdict: {rt.get('overall_verdict')}")
            print(f"   Risk Level: {rt.get('risk_level')}")
            
            for service, check in rt.get('checks', {}).items():
                print(f"\n   {service.upper()}:")
                print(f"      Verdict: {check.get('verdict')}")
                print(f"      Message: {check.get('message')}")
                if 'is_malicious' in check:
                    print(f"      Is Malicious: {check.get('is_malicious')}")
        
        print(f"\n💡 Educational Explanations:")
        for exp in result.get('educational_explanations', []):
            print(f"   - {exp[:100]}...")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
