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
        # Phishs.com API keys (optional - get from https://phishs.com)
        self.phishs_public_key = os.getenv('PHISHS_PUBLIC_KEY', '')
        self.phishs_secret_key = os.getenv('PHISHS_SECRET_KEY', '')
        self.phishs_team_id = os.getenv('PHISHS_TEAM_ID', '')
        
        # VirusTotal API key (get from https://www.virustotal.com)
        self.virustotal_api_key = os.getenv('VIRUSTOTAL_API_KEY', '847b72227574d01600c6e59bf0bd7d6e66a822b4b119bcdaa8a0acaf8d4839aa')
    
    def check_virustotal(self, url):
        """
        VirusTotal - Industry-leading malware/phishing detection
        Scans URL with 70+ antivirus engines
        FREE: 4 requests per minute, 500 per day
        """
        if not self.virustotal_api_key:
            return {'error': 'VirusTotal API key not configured'}
        
        try:
            import base64
            
            # VirusTotal requires URL to be base64 encoded (without padding)
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            
            api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            
            headers = {
                'x-apikey': self.virustotal_api_key
            }
            
            response = requests.get(api_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract analysis stats
                attributes = data.get('data', {}).get('attributes', {})
                stats = attributes.get('last_analysis_stats', {})
                
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                harmless = stats.get('harmless', 0)
                undetected = stats.get('undetected', 0)
                
                total_scans = malicious + suspicious + harmless + undetected
                
                # Get categories
                categories = attributes.get('categories', {})
                
                # Determine verdict
                is_malicious = malicious > 0 or suspicious > 2
                
                if malicious > 0:
                    verdict = 'MALICIOUS'
                    message = f'{malicious}/{total_scans} engines detected as malicious'
                elif suspicious > 2:
                    verdict = 'SUSPICIOUS'
                    message = f'{suspicious}/{total_scans} engines flagged as suspicious'
                else:
                    verdict = 'SAFE'
                    message = f'Clean - {harmless}/{total_scans} engines confirmed safe'
                
                return {
                    'service': 'VirusTotal',
                    'is_malicious': is_malicious,
                    'verdict': verdict,
                    'malicious_count': malicious,
                    'suspicious_count': suspicious,
                    'harmless_count': harmless,
                    'total_scans': total_scans,
                    'detection_rate': f'{malicious}/{total_scans}',
                    'categories': list(categories.values()) if categories else [],
                    'message': message
                }
            
            elif response.status_code == 404:
                # URL not in database, submit for scanning
                return self._submit_url_to_virustotal(url)
            
            else:
                return {'error': f'VirusTotal API error: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'VirusTotal check failed: {str(e)}'}
    
    def _submit_url_to_virustotal(self, url):
        """Submit URL to VirusTotal for scanning if not in database"""
        try:
            api_url = "https://www.virustotal.com/api/v3/urls"
            
            headers = {
                'x-apikey': self.virustotal_api_key
            }
            
            data = {'url': url}
            
            response = requests.post(api_url, headers=headers, data=data, timeout=15)
            
            if response.status_code == 200:
                return {
                    'service': 'VirusTotal',
                    'verdict': 'UNKNOWN',
                    'message': 'URL submitted for scanning - check again in a few minutes',
                    'status': 'scanning'
                }
            else:
                return {'error': f'VirusTotal submission error: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'VirusTotal submission failed: {str(e)}'}
    
    def check_phishs_com(self, url):
        """
        Phishs.com - Professional phishing detection service
        FREE tier available with API key
        Sign up: https://phishs.com
        """
        if not self.phishs_public_key or not self.phishs_secret_key or not self.phishs_team_id:
            return {'error': 'Phishs.com API keys not configured'}
        
        try:
            api_url = "https://api.phishs.com/v1/scan/url"
            
            headers = {
                'Content-Type': 'application/json',
                'Public-Key': self.phishs_public_key,
                'Secret-Key': self.phishs_secret_key
            }
            
            payload = {
                'teamId': self.phishs_team_id,
                'url': url,
                'rescan': False  # Use cache for faster response
            }
            
            response = requests.post(api_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if request was successful
                status = data.get('status', {})
                if status.get('code') == 0:
                    url_status = data.get('urlStatus', {})
                    
                    # status: 0 = No classification (safe)
                    # status: 1 = Potentially Malicious
                    # status: -1 = Not a valid URL
                    scan_status = url_status.get('status', -1)
                    last_scan = url_status.get('lastScanTimeStr', 'Unknown')
                    
                    is_malicious = scan_status == 1
                    
                    if scan_status == 1:
                        verdict = 'MALICIOUS'
                        message = 'Potentially Malicious (Phishing detected)'
                    elif scan_status == 0:
                        verdict = 'SAFE'
                        message = 'No classification (appears safe)'
                    else:
                        verdict = 'UNKNOWN'
                        message = 'Not a valid URL'
                    
                    return {
                        'service': 'Phishs.com',
                        'is_malicious': is_malicious,
                        'status_code': scan_status,
                        'verdict': verdict,
                        'message': message,
                        'last_scan': last_scan
                    }
                else:
                    return {'error': f'Phishs.com error: {status.get("message", "Unknown error")}'}
            else:
                return {'error': f'Phishs.com API error: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'Phishs.com check failed: {str(e)}'}
    
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
            api_url = f"https://dangerous.domains/api/v1/{domain}"
            
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # API returns: {"success": true, "isMalicious": false}
                success = data.get('success', False)
                is_dangerous = data.get('isMalicious', False)
                
                if not success:
                    return {'error': 'Dangerous.domains API error'}
                
                return {
                    'service': 'Dangerous.domains',
                    'is_malicious': is_dangerous,
                    'verdict': 'MALICIOUS' if is_dangerous else 'SAFE',
                    'message': 'Malicious domain detected!' if is_dangerous else 'Clean domain'
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
        Comprehensive check with PRIORITY system:
        
        PRIORITY 1: VirusTotal (70+ engines - MOST TRUSTED!)
        - If available: Use VirusTotal verdict as PRIMARY decision
        - If limit exceeded: Fallback to other APIs
        
        FALLBACK: Dangerous.domains + URLScan.io
        - Use when VirusTotal unavailable
        - Combine results for decision
        
        ALWAYS: Collect complete URL information
        """
        results = {
            'url': url,
            'checks': {},
            'summary': {
                'total_checks': 0,
                'malicious_count': 0,
                'safe_count': 0,
                'unknown_count': 0
            },
            'url_info': {},  # Complete URL information
            'virustotal_available': False,
            'primary_source': None  # Which API made the final decision
        }
        
        # PRIORITY 1: VirusTotal (70+ engines - BEST!)
        virustotal_working = False
        if self.virustotal_api_key:
            print("[URL CHECK] 🦠 Checking VirusTotal (70+ engines) - PRIMARY SOURCE...")
            vt_result = self.check_virustotal(url)
            
            if not vt_result.get('error'):
                results['checks']['virustotal'] = vt_result
                results['summary']['total_checks'] += 1
                results['virustotal_available'] = True
                results['primary_source'] = 'VirusTotal'
                virustotal_working = True
                print(f"[URL CHECK] ✅ VirusTotal: {vt_result.get('verdict')} ({vt_result.get('detection_rate')})")
            else:
                error_msg = vt_result.get('error', '')
                if '429' in error_msg or 'quota' in error_msg.lower() or 'limit' in error_msg.lower():
                    print("[URL CHECK] ⚠️ VirusTotal: Daily limit exceeded - using fallback APIs")
                    results['virustotal_limit_exceeded'] = True
                else:
                    print(f"[URL CHECK] ⚠️ VirusTotal error: {error_msg}")
        
        # FALLBACK APIs: Dangerous.domains + URLScan.io
        # Always run these for complete information
        print("[URL CHECK] 🌐 Checking Dangerous.domains (1M+ domains)...")
        dangerous_result = self.check_dangerous_domains(url)
        if not dangerous_result.get('error'):
            results['checks']['dangerous_domains'] = dangerous_result
            results['summary']['total_checks'] += 1
            if not virustotal_working:
                results['primary_source'] = 'Dangerous.domains + URLScan.io'
            print(f"[URL CHECK] ✅ Dangerous.domains: {dangerous_result.get('verdict')}")
        
        print("[URL CHECK] 🔍 Checking URLScan.io (Domain info + Community scans)...")
        urlscan_result = self.check_urlscan_io(url)
        if not urlscan_result.get('error'):
            results['checks']['urlscan'] = urlscan_result
            results['summary']['total_checks'] += 1
            
            # Extract URL information from URLScan.io
            if urlscan_result.get('domain'):
                results['url_info']['domain'] = urlscan_result.get('domain')
            if urlscan_result.get('ip'):
                results['url_info']['ip'] = urlscan_result.get('ip')
            if urlscan_result.get('country'):
                results['url_info']['country'] = urlscan_result.get('country')
            if urlscan_result.get('server'):
                results['url_info']['server'] = urlscan_result.get('server')
            
            print(f"[URL CHECK] ✅ URLScan.io: {urlscan_result.get('verdict')}")
        
        # Calculate verdict counts
        for service, result in results['checks'].items():
            verdict = result.get('verdict', 'UNKNOWN')
            if verdict in ['MALICIOUS', 'PHISHING', 'SUSPICIOUS']:
                results['summary']['malicious_count'] += 1
            elif verdict == 'SAFE':
                results['summary']['safe_count'] += 1
            else:
                results['summary']['unknown_count'] += 1
        
        # DECISION LOGIC with PRIORITY
        if virustotal_working:
            # VirusTotal is PRIORITY - use its verdict
            vt_verdict = results['checks']['virustotal'].get('verdict')
            vt_malicious = results['checks']['virustotal'].get('malicious_count', 0)
            vt_suspicious = results['checks']['virustotal'].get('suspicious_count', 0)
            vt_total = results['checks']['virustotal'].get('total_scans', 0)
            
            if vt_verdict == 'MALICIOUS':
                results['overall_verdict'] = 'MALICIOUS'
                results['risk_level'] = 'HIGH'
                results['message'] = f'VirusTotal: {vt_malicious}/{vt_total} engines detected malicious'
                results['decision_reason'] = f'Primary check detected threat with {vt_malicious} engines'
            elif vt_verdict == 'SUSPICIOUS':
                results['overall_verdict'] = 'SUSPICIOUS'
                results['risk_level'] = 'MEDIUM'
                results['message'] = f'VirusTotal: {vt_suspicious}/{vt_total} engines flagged suspicious'
                results['decision_reason'] = f'Primary check flagged as suspicious'
            else:
                results['overall_verdict'] = 'SAFE'
                results['risk_level'] = 'LOW'
                results['message'] = f'VirusTotal: Clean - {vt_total} engines scanned'
                results['decision_reason'] = f'Primary check confirmed safe with {vt_total} engines'
        else:
            # Fallback to other APIs
            if results['summary']['malicious_count'] > 0:
                results['overall_verdict'] = 'MALICIOUS'
                results['risk_level'] = 'HIGH'
                results['message'] = f'{results["summary"]["malicious_count"]} service(s) detected as malicious'
                results['decision_reason'] = 'Fallback APIs detected threat (primary check unavailable)'
            elif results['summary']['safe_count'] >= 1:
                results['overall_verdict'] = 'SAFE'
                results['risk_level'] = 'LOW'
                results['message'] = f'{results["summary"]["safe_count"]} service(s) confirmed safe'
                results['decision_reason'] = 'Fallback APIs confirmed safe (primary check unavailable)'
            else:
                results['overall_verdict'] = 'UNKNOWN'
                results['risk_level'] = 'MEDIUM'
                results['message'] = 'Unable to determine - insufficient data'
                results['decision_reason'] = 'Insufficient data from all APIs'
        
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
