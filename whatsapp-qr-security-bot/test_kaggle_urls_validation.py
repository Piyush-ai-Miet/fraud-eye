#!/usr/bin/env python3
"""
Test Kaggle malicious URLs against our detection system
Validates if our system correctly identifies malicious vs benign URLs
"""

import requests
import csv
import time
from collections import defaultdict

# Test configuration
SERVER_URL = 'http://localhost:5001'
TEST_LIMIT = 50  # Test first 50 URLs from dataset
DELAY_BETWEEN_REQUESTS = 0.5  # seconds

def load_kaggle_urls(limit=50):
    """Load URLs from Kaggle dataset"""
    urls = []
    try:
        with open('data/kaggle_malicious_urls.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                url = row['url']
                url_type = row['type']
                
                # Add http:// if not present
                if not url.startswith('http://') and not url.startswith('https://'):
                    url = 'http://' + url
                
                urls.append({
                    'url': url,
                    'actual_type': url_type,
                    'is_malicious': url_type in ['phishing', 'malware', 'defacement']
                })
    except Exception as e:
        print(f"Error loading dataset: {e}")
    
    return urls

def test_url(url_data):
    """Test a single URL against our system"""
    try:
        response = requests.post(
            f'{SERVER_URL}/api/check-url',
            json={'url': url_data['url']},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Determine if our system detected it as malicious
            detected_as_malicious = not result.get('is_safe', True) or result.get('risk', 'LOW') in ['HIGH', 'MEDIUM']
            
            return {
                'url': url_data['url'],
                'actual_type': url_data['actual_type'],
                'is_malicious': url_data['is_malicious'],
                'detected_as_malicious': detected_as_malicious,
                'risk_level': result.get('risk', 'UNKNOWN'),
                'is_safe': result.get('is_safe', None),
                'warnings': result.get('warnings', []),
                'correct': detected_as_malicious == url_data['is_malicious']
            }
        else:
            return {
                'url': url_data['url'],
                'error': f'HTTP {response.status_code}',
                'correct': False
            }
    
    except Exception as e:
        return {
            'url': url_data['url'],
            'error': str(e),
            'correct': False
        }

def main():
    print("\n" + "="*80)
    print("🧪 Testing Kaggle Malicious URLs Dataset")
    print("="*80)
    print(f"Server: {SERVER_URL}")
    print(f"Testing first {TEST_LIMIT} URLs from dataset")
    print("="*80)
    
    # Load URLs
    print("\n📂 Loading URLs from Kaggle dataset...")
    urls = load_kaggle_urls(TEST_LIMIT)
    print(f"✅ Loaded {len(urls)} URLs")
    
    # Count by type
    type_counts = defaultdict(int)
    for url_data in urls:
        type_counts[url_data['actual_type']] += 1
    
    print(f"\n📊 Dataset Breakdown:")
    for url_type, count in sorted(type_counts.items()):
        print(f"   {url_type}: {count}")
    
    # Test each URL
    print(f"\n🔍 Testing URLs...")
    print("="*80)
    
    results = []
    correct_count = 0
    false_positives = 0  # Benign detected as malicious
    false_negatives = 0  # Malicious detected as benign
    
    for i, url_data in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Testing: {url_data['url'][:60]}...")
        print(f"   Actual Type: {url_data['actual_type']}")
        
        result = test_url(url_data)
        results.append(result)
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   Detected Risk: {result['risk_level']}")
            print(f"   Detected Safe: {result['is_safe']}")
            
            if result['correct']:
                correct_count += 1
                print(f"   ✅ CORRECT")
            else:
                if url_data['is_malicious'] and not result['detected_as_malicious']:
                    false_negatives += 1
                    print(f"   ❌ FALSE NEGATIVE (Missed malicious URL!)")
                elif not url_data['is_malicious'] and result['detected_as_malicious']:
                    false_positives += 1
                    print(f"   ⚠️ FALSE POSITIVE (Flagged benign as malicious)")
            
            # Show warnings if any
            if result.get('warnings'):
                print(f"   Warnings: {len(result['warnings'])}")
                for warning in result['warnings'][:3]:  # Show first 3
                    print(f"      - {warning}")
        
        # Delay to avoid overwhelming server
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Calculate statistics
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    
    total_tested = len([r for r in results if 'error' not in r])
    accuracy = (correct_count / total_tested * 100) if total_tested > 0 else 0
    
    print(f"\n✅ Total URLs Tested: {total_tested}")
    print(f"✅ Correctly Identified: {correct_count}")
    print(f"❌ Incorrectly Identified: {total_tested - correct_count}")
    print(f"\n📈 Accuracy: {accuracy:.1f}%")
    
    print(f"\n🔍 Error Analysis:")
    print(f"   False Positives (Benign → Malicious): {false_positives}")
    print(f"   False Negatives (Malicious → Benign): {false_negatives}")
    
    # Breakdown by actual type
    print(f"\n📊 Accuracy by URL Type:")
    type_accuracy = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    for result in results:
        if 'error' not in result:
            url_type = result['actual_type']
            type_accuracy[url_type]['total'] += 1
            if result['correct']:
                type_accuracy[url_type]['correct'] += 1
    
    for url_type in sorted(type_accuracy.keys()):
        stats = type_accuracy[url_type]
        acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"   {url_type}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")
    
    # Show some examples of false negatives (most critical)
    if false_negatives > 0:
        print(f"\n⚠️ FALSE NEGATIVES (Malicious URLs we MISSED):")
        fn_count = 0
        for result in results:
            if 'error' not in result and not result['correct'] and result['is_malicious']:
                fn_count += 1
                if fn_count <= 5:  # Show first 5
                    print(f"\n   {fn_count}. {result['url'][:70]}")
                    print(f"      Type: {result['actual_type']}")
                    print(f"      Detected as: {result['risk_level']} (Safe: {result['is_safe']})")
    
    # Show some examples of false positives
    if false_positives > 0:
        print(f"\n⚠️ FALSE POSITIVES (Benign URLs flagged as malicious):")
        fp_count = 0
        for result in results:
            if 'error' not in result and not result['correct'] and not result['is_malicious']:
                fp_count += 1
                if fp_count <= 5:  # Show first 5
                    print(f"\n   {fp_count}. {result['url'][:70]}")
                    print(f"      Type: {result['actual_type']}")
                    print(f"      Detected as: {result['risk_level']} (Safe: {result['is_safe']})")
                    if result.get('warnings'):
                        print(f"      Warnings: {result['warnings'][0]}")
    
    print("\n" + "="*80)
    print("✅ Test Complete!")
    print("="*80)
    
    # Overall verdict
    if accuracy >= 90:
        print("\n🎉 EXCELLENT! System is working very well!")
    elif accuracy >= 75:
        print("\n✅ GOOD! System is working well with room for improvement.")
    elif accuracy >= 60:
        print("\n⚠️ FAIR! System needs improvement.")
    else:
        print("\n❌ POOR! System needs significant improvement.")
    
    print(f"\n💡 Note: False negatives are more critical than false positives")
    print(f"   (Missing malicious URLs is worse than flagging benign ones)")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
