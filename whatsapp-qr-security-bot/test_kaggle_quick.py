#!/usr/bin/env python3
"""
Quick test of Kaggle URLs - tests 10 URLs (5 malicious, 5 benign)
"""

import requests
import csv

SERVER_URL = 'http://localhost:5001'

def test_url(url, expected_type):
    """Test a single URL"""
    try:
        # Add http:// if needed
        if not url.startswith('http'):
            url = 'http://' + url
        
        response = requests.post(
            f'{SERVER_URL}/api/check-url',
            json={'url': url},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            is_malicious = expected_type in ['phishing', 'malware', 'defacement']
            detected_malicious = not result.get('is_safe', True) or result.get('risk') in ['HIGH', 'MEDIUM']
            
            return {
                'url': url,
                'expected': expected_type,
                'risk': result.get('risk', 'UNKNOWN'),
                'safe': result.get('is_safe', None),
                'correct': detected_malicious == is_malicious,
                'warnings': len(result.get('warnings', []))
            }
    except Exception as e:
        return {'url': url, 'error': str(e)}

# Test URLs from Kaggle dataset
test_cases = [
    # Malicious URLs
    ('br-icloud.com.br', 'phishing'),
    ('signin.eby.de.zukruygxctzmmqi.civpro.co.za', 'phishing'),
    ('http://www.marketingbyinternet.com/mo/e56508df639f6ce7d55c81ee3fcd5ba8/', 'phishing'),
    ('http://www.824555.com/app/member/SportOption.php?uid=guest&langx=gb', 'malware'),
    ('http://www.garage-pirenne.be/index.php?option=com_content&view=article&id=70&vsig70_0=15', 'defacement'),
    
    # Benign URLs
    ('espn.go.com/nba/player/_/id/3457/brandon-rush', 'benign'),
    ('en.wikipedia.org/wiki/North_Dakota', 'benign'),
    ('nytimes.com/1998/03/29/style/cuttings-oh-that-brazen-raucous-glorious-hibiscus.html', 'benign'),
    ('allmusic.com/album/crazy-from-the-heat-r16990', 'benign'),
    ('quickfacts.census.gov/qfd/maps/iowa_map.html', 'benign'),
]

print("\n" + "="*80)
print("🧪 Quick Kaggle URL Validation Test")
print("="*80)
print(f"Testing 10 URLs (5 malicious, 5 benign)")
print("="*80)

results = []
correct = 0

for i, (url, expected_type) in enumerate(test_cases, 1):
    print(f"\n[{i}/10] {url[:60]}")
    print(f"   Expected: {expected_type}")
    
    result = test_url(url, expected_type)
    results.append(result)
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   Risk: {result['risk']}, Safe: {result['safe']}, Warnings: {result['warnings']}")
        if result['correct']:
            print(f"   ✅ CORRECT")
            correct += 1
        else:
            print(f"   ❌ WRONG")

print("\n" + "="*80)
print("📊 RESULTS")
print("="*80)
print(f"Correct: {correct}/10 ({correct*10}%)")
print("="*80 + "\n")
