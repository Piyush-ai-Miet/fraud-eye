#!/usr/bin/env python3
"""
Third-Party URL Checker - Clean Version with FREE APIs
1. Dangerous.domains (NO API KEY - 1M+ domains, unlimited)
2. URLScan.io (NO API KEY - community scans)
"""

import requests
from urllib.parse import urlparse
import os

class ThirdPartyURLChecker:
    def __init__(self):
        pass
    
    def check_dangerous_domains(self, url):
        """
        Dangerous.domains - Completely FREE malicious domain checker
        NO API KEY NEEDED, NO RATE LIMITS
        Built on Cloudflare Workers, very fast
        Database: 1M+ malicious domains
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # API endpoint - completely free, no authentication
            api_url = f"https://api.dangerous.domains/check/{domain}"
            
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                is_dangerous = data.get('dangerous', False)
                category = data.get('category', 'unknown')
                confidence = data.get('confidence', 0)
                
                return {
                    'service': 'Dangerous.domains',
                    'is_malicious': is_dangerous,
                    'category': category,
                    'confidence': confidence,
                    'verdict': 'MALICIOUS' if is_dangerous else 'SAFE',
                    'message': f'{category.title()} (Confidence: {confidence}%)' if is_dangerous else 'Clean domain'
                }
            else:
                return {'error': f'Dangerous.domains error: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'Dangerous.domains check failed: {str(e)}'}
    
    def check_urlscan_io(self, url):
        """
        URLScan.io - Free URL scanning service
        Uses public search API (no authentication needed)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Search for existing scans of this domain
            search_url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
            
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    # Get the most recent scan
                    latest_scan = results[0]
                    
                    # Extract information
                    page = latest_scan.get('page', {})
                    
                    scan_domain = page.get('domain', '')
                    ip = page.get('ip', '')
                    country = page.get('country', '')
                    server = page.get('server', '')
                    
                    # Verdicts
                    verdicts = latest_scan.get('verdicts', {})
                    overall = verdicts.get('overall', {})
                    
                    malicious = overall.get('malicious', False)
                    score = overall.get('score', 0)
                    categories = overall.get('categories', [])
                    
                    # Stats
                    stats = latest_scan.get('stats', {})
                    malicious_requests = stats.get('malicious', 0)
                    
                    return {
                        'service': 'URLScan.io',
                        'is_malicious': malicious or malicious_requests > 0,
                        'score': score,
                        'categories': categories,
                        'verdict': 'MALICIOUS' if (malicious or malicious_requests > 0) else 'SAFE',
                        'domain': scan_domain,
                        'ip': ip,
                        'country': country,
                        'server': server,
                        'message': f'Score: {score}/100' + (f', {", ".join(categories)}' if categories else '')
                    }
                else:
                    # No previous scans found
                    return {
                        'service': 'URLScan.io',
                        'status': 'not_scanned',
                        'verdict': 'UNKNOWN',
                        'message': 'No previous scans found for this domain'
                    }
            else:
                return {'error': f'URLScan.io error: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'URLScan.io check failed: {str(e)}'}
    
    def check_url_comprehensive(self, url):
        """
        Comprehensive check using 2 FREE APIs (NO API KEYS NEEDED):
        1. Dangerous.domains (1M+ domains, unlimited, NO API KEY)
        2. URLScan.io (community scans, NO API KEY)
        """
        results = {
            'url': url,
            'checks': {},
            'summary': {
                'total_checks': 0,
                'malicious_count': 0,
                'safe_count': 0,
                'unknown_count': 0
            }
        }
        
        # Check 1: Dangerous.domains (ALWAYS AVAILABLE, NO API KEY)
        print("[URL CHECK] Checking Dangerous.domains (NO API KEY)...")
        dangerous_result = self.check_dangerous_domains(url)
        if not dangerous_result.get('error'):
            results['checks']['dangerous_domains'] = dangerous_result
            results['summary']['total_checks'] += 1
        
        # Check 2: URLScan.io (always available, no API key)
        print("[URL CHECK] Checking URLScan.io...")
        urlscan_result = self.check_urlscan_io(url)
        if not urlscan_result.get('error'):
            results['checks']['urlscan'] = urlscan_result
            results['summary']['total_checks'] += 1
        
        # Calculate overall verdict
        for service, result in results['checks'].items():
            verdict = result.get('verdict', 'UNKNOWN')
            if verdict in ['MALICIOUS', 'PHISHING', 'SUSPICIOUS']:
                results['summary']['malicious_count'] += 1
            elif verdict == 'SAFE':
                results['summary']['safe_count'] += 1
            else:
                results['summary']['unknown_count'] += 1
        
        # Determine overall verdict
        if results['summary']['malicious_count'] > 0:
            results['overall_verdict'] = 'MALICIOUS'
            results['risk_level'] = 'HIGH'
            results['message'] = f'{results["summary"]["malicious_count"]} service(s) detected as malicious'
        elif results['summary']['safe_count'] >= 1:
            results['overall_verdict'] = 'SAFE'
            results['risk_level'] = 'LOW'
            results['message'] = f'{results["summary"]["safe_count"]} service(s) confirmed safe'
        else:
            results['overall_verdict'] = 'UNKNOWN'
            results['risk_level'] = 'MEDIUM'
            results['message'] = 'Unable to determine - insufficient data'
        
        return results

# Initialize checker
third_party_checker = ThirdPartyURLChecker()

if __name__ == '__main__':
    # Test
    print("\n🧪 Testing Third-Party URL Checker (NO API KEYS NEEDED)")
    print("="*60)
    print("Using 2 FREE APIs:")
    print("1. Dangerous.domains (1M+ domains, NO API KEY)")
    print("2. URLScan.io (community scans, NO API KEY)")
    print("="*60)
    print("\n✅ Both APIs work WITHOUT any setup!")
    print("   - No API keys required")
    print("   - No rate limits")
    print("   - Completely free")
    print("="*60)
    
    test_urls = [
        "https://google.com",
        "https://paytm.com",
        "http://malicious-site.tk"
    ]
    
    for test_url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {test_url}")
        print('='*60)
        
        result = third_party_checker.check_url_comprehensive(test_url)
        
        print(f"\nOverall Verdict: {result['overall_verdict']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Message: {result['message']}")
        print(f"\nSummary:")
        print(f"  Total Checks: {result['summary']['total_checks']}")
        print(f"  Malicious: {result['summary']['malicious_count']}")
        print(f"  Safe: {result['summary']['safe_count']}")
        print(f"  Unknown: {result['summary']['unknown_count']}")
        
        print(f"\nDetailed Results:")
        for service, check_result in result['checks'].items():
            print(f"\n  {service.upper()}:")
            if 'error' in check_result:
                print(f"    Error: {check_result['error']}")
            else:
                print(f"    Verdict: {check_result.get('verdict', 'N/A')}")
                print(f"    Message: {check_result.get('message', 'N/A')}")
                if 'domain' in check_result:
                    print(f"    Domain: {check_result['domain']}")
                if 'ip' in check_result:
                    print(f"    IP: {check_result['ip']}")
                if 'country' in check_result:
                    print(f"    Country: {check_result['country']}")
