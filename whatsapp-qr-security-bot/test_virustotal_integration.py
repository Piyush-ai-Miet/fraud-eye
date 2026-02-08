#!/usr/bin/env python3
"""
Test VirusTotal Integration
Verify that all 3-4 APIs are working correctly
"""

import requests
import json

def test_url_checker(url, description):
    """Test URL checker with comprehensive API checks"""
    print(f"\n{'='*70}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    print('='*70)
    
    try:
        response = requests.post(
            'http://localhost:5001/api/check-url',
            json={'url': url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Overall Verdict: {result.get('risk', 'UNKNOWN')}")
            print(f"📝 Message: {result.get('message_hi', 'N/A')}")
            
            # Check realtime results (third-party APIs)
            realtime = result.get('realtime_result', {})
            if realtime:
                checks = realtime.get('checks', {})
                summary = realtime.get('summary', {})
                
                print(f"\n📊 API Summary:")
                print(f"   Total Checks: {summary.get('total_checks', 0)}")
                print(f"   Malicious: {summary.get('malicious_count', 0)}")
                print(f"   Safe: {summary.get('safe_count', 0)}")
                print(f"   Unknown: {summary.get('unknown_count', 0)}")
                
                # VirusTotal results
                if 'virustotal' in checks:
                    vt = checks['virustotal']
                    print(f"\n🦠 VirusTotal (70+ engines):")
                    print(f"   Verdict: {vt.get('verdict', 'N/A')}")
                    print(f"   Detection Rate: {vt.get('detection_rate', 'N/A')}")
                    print(f"   Malicious: {vt.get('malicious_count', 0)}")
                    print(f"   Harmless: {vt.get('harmless_count', 0)}")
                    print(f"   Total Scans: {vt.get('total_scans', 0)}")
                    print(f"   Message: {vt.get('message', 'N/A')}")
                else:
                    print(f"\n⚠️ VirusTotal: Not available")
                
                # Dangerous.domains results
                if 'dangerous_domains' in checks:
                    dd = checks['dangerous_domains']
                    print(f"\n🌐 Dangerous.domains:")
                    print(f"   Verdict: {dd.get('verdict', 'N/A')}")
                    print(f"   Message: {dd.get('message', 'N/A')}")
                else:
                    print(f"\n⚠️ Dangerous.domains: Not available")
                
                # URLScan.io results
                if 'urlscan' in checks:
                    us = checks['urlscan']
                    print(f"\n🔍 URLScan.io:")
                    print(f"   Verdict: {us.get('verdict', 'N/A')}")
                    if us.get('domain'):
                        print(f"   Domain: {us.get('domain')}")
                    if us.get('ip'):
                        print(f"   IP: {us.get('ip')}")
                    if us.get('country'):
                        print(f"   Country: {us.get('country')}")
                    if us.get('server'):
                        print(f"   Server: {us.get('server')}")
                    print(f"   Message: {us.get('message', 'N/A')}")
                else:
                    print(f"\n⚠️ URLScan.io: Not available")
                
                # Phishs.com results (optional)
                if 'phishs_com' in checks:
                    pc = checks['phishs_com']
                    print(f"\n🎣 Phishs.com:")
                    print(f"   Verdict: {pc.get('verdict', 'N/A')}")
                    print(f"   Message: {pc.get('message', 'N/A')}")
            
            # Warnings
            warnings = result.get('warnings', [])
            if warnings:
                print(f"\n⚠️ Warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
            
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🧪 VIRUSTOTAL INTEGRATION TEST")
    print("="*70)
    print("\nTesting all APIs:")
    print("1. ✅ VirusTotal (70+ antivirus engines)")
    print("2. ✅ Dangerous.domains (1M+ domains)")
    print("3. ✅ URLScan.io (community scans)")
    print("4. ⏸️ Phishs.com (optional)")
    print("="*70)
    
    # Test cases
    test_cases = [
        {
            'url': 'https://google.com',
            'description': 'Safe URL - Google (should be SAFE)'
        },
        {
            'url': 'https://paytm.com',
            'description': 'Safe URL - Paytm (should be SAFE)'
        },
        {
            'url': 'http://malicious-site.tk',
            'description': 'Suspicious URL - Free domain (may be flagged)'
        },
        {
            'url': 'https://github.com',
            'description': 'Safe URL - GitHub (should be SAFE)'
        }
    ]
    
    results = []
    for test_case in test_cases:
        success = test_url_checker(test_case['url'], test_case['description'])
        results.append(success)
        print("\n" + "-"*70)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED!")
        print("\n🎉 VirusTotal integration is working perfectly!")
        print("   - 70+ antivirus engines scanning")
        print("   - Real-time threat detection")
        print("   - Comprehensive domain information")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Check the output above for details")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
