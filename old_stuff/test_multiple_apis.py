#!/usr/bin/env python3
"""
Test Multiple Third-Party APIs Integration
Tests URL checker with all available APIs
"""

import requests
import json

def test_url_checker(url):
    """Test URL checker API"""
    print(f"\n{'='*60}")
    print(f"Testing URL: {url}")
    print('='*60)
    
    api_url = "http://localhost:5001/api/check-url"
    
    try:
        response = requests.post(
            api_url,
            json={"url": url},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Status: {response.status_code}")
            print(f"🔒 Safe: {result.get('is_safe')}")
            print(f"⚠️ Risk: {result.get('risk')}")
            print(f"💬 Message: {result.get('message_hi')}")
            print(f"🌐 Domain: {result.get('domain')}")
            
            print(f"\n📋 Warnings ({len(result.get('warnings', []))}):")
            for warning in result.get('warnings', []):
                print(f"   {warning}")
            
            # Show third-party results
            realtime = result.get('realtime_result', {})
            if realtime:
                print(f"\n🔍 Third-Party Checks:")
                checks = realtime.get('checks', {})
                summary = realtime.get('summary', {})
                
                print(f"   Total Checks: {summary.get('total_checks', 0)}")
                print(f"   Malicious: {summary.get('malicious_count', 0)}")
                print(f"   Safe: {summary.get('safe_count', 0)}")
                print(f"   Unknown: {summary.get('unknown_count', 0)}")
                
                print(f"\n   Services:")
                for service, data in checks.items():
                    verdict = data.get('verdict', 'N/A')
                    message = data.get('message', 'N/A')
                    print(f"   - {service}: {verdict} ({message})")
            
            return result
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None

if __name__ == '__main__':
    print("\n🧪 Testing Multiple APIs Integration")
    print("="*60)
    print("Make sure server is running: python3 app_simple.py")
    print("="*60)
    
    # Test URLs
    test_urls = [
        "https://google.com",
        "https://paytm.com",
        "http://suspicious-site.tk",
        "https://192.168.1.1",
    ]
    
    results = []
    for url in test_urls:
        result = test_url_checker(url)
        results.append({
            'url': url,
            'result': result
        })
        print()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    for item in results:
        url = item['url']
        result = item['result']
        if result:
            risk = result.get('risk', 'UNKNOWN')
            safe = result.get('is_safe', False)
            status = '✅ SAFE' if safe else '🚨 DANGEROUS'
            print(f"{status} [{risk:6s}] {url}")
        else:
            print(f"❌ ERROR           {url}")
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
