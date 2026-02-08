import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import whois
import re

class RealtimeURLChecker:
    def __init__(self):
        self.timeout = 5
        
    def check_ssl_certificate(self, domain):
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    if cert:
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_remaining = (not_after - datetime.now()).days
                        
                        return {
                            'valid': True,
                            'issuer': dict(x[0] for x in cert['issuer']) if cert.get('issuer') else {},
                            'expires_in_days': days_remaining,
                            'subject': dict(x[0] for x in cert['subject']) if cert.get('subject') else {}
                        }
                    else:
                        return {'valid': True, 'expires_in_days': 365}
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def check_domain_age(self, domain):
        try:
            w = whois.whois(domain)
            if w and w.creation_date:
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
                
                age_days = (datetime.now() - creation_date).days
                
                return {
                    'age_days': age_days,
                    'creation_date': creation_date.strftime('%Y-%m-%d'),
                    'registrar': w.registrar if hasattr(w, 'registrar') else 'Unknown',
                    'is_new': age_days < 180
                }
        except Exception as e:
            pass
        return None
    
    def scrape_page_content(self, url):
        """Enhanced web scraping with better phishing detection"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            content = response.text.lower()
            
            # Enhanced phishing indicators
            phishing_indicators = {
                'login_form': bool(re.search(r'<form.*?(login|signin|password|username)', content)),
                'payment_form': bool(re.search(r'(credit card|cvv|card number|payment|billing)', content)),
                'urgent_language': bool(re.search(r'(urgent|suspended|verify now|click here|limited time|act now)', content)),
                'otp_request': bool(re.search(r'(otp|one time password|verification code|enter code)', content)),
                'fake_brand': bool(re.search(r'(paytm|phonepe|google pay|sbi|hdfc|icici|bank|paypal)', content)),
                'personal_info': bool(re.search(r'(social security|aadhar|pan card|date of birth|mother.*name)', content)),
                'suspicious_links': bool(re.search(r'(bit\.ly|tinyurl|goo\.gl|t\.co)', content)),
                'fake_security': bool(re.search(r'(security alert|account locked|unusual activity)', content)),
                'prize_scam': bool(re.search(r'(congratulations|winner|prize|lottery|claim now)', content)),
                'impersonation': bool(re.search(r'(official|verify your|confirm your|update your)', content))
            }
            
            suspicious_count = sum(phishing_indicators.values())
            
            # Check for LinkedIn/social media impersonation
            is_linkedin_fake = 'linkedin' in url.lower() and 'linkedin.com' not in urlparse(url).netloc
            is_facebook_fake = 'facebook' in url.lower() and 'facebook.com' not in urlparse(url).netloc
            
            if is_linkedin_fake or is_facebook_fake:
                suspicious_count += 3
                phishing_indicators['brand_impersonation'] = True
            
            return {
                'status_code': response.status_code,
                'final_url': response.url,
                'redirected': response.url != url,
                'phishing_indicators': phishing_indicators,
                'suspicious_score': suspicious_count,
                'title': self._extract_title(content),
                'has_forms': '<form' in content,
                'content_length': len(content),
                'is_impersonation': is_linkedin_fake or is_facebook_fake
            }
        except Exception as e:
            return {
                'error': str(e),
                'accessible': False
            }
    
    def _extract_title(self, html):
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        return match.group(1) if match else 'No title'
    
    def check_url_realtime(self, url):
        result = {
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'checks': {}
        }
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        if not domain:
            return {
                'error': 'Invalid URL',
                'is_safe': False
            }
        
        # Check 1: SSL Certificate
        if parsed.scheme == 'https':
            result['checks']['ssl'] = self.check_ssl_certificate(domain)
        else:
            result['checks']['ssl'] = {'valid': False, 'reason': 'No HTTPS'}
        
        # Check 2: Domain Age
        result['checks']['domain_age'] = self.check_domain_age(domain)
        
        # Check 3: Page Content Scraping
        result['checks']['content'] = self.scrape_page_content(url)
        
        # Calculate overall risk
        risk_score = 0
        warnings = []
        
        # SSL check
        if not result['checks']['ssl'].get('valid'):
            risk_score += 3
            warnings.append('⚠️ SSL certificate invalid ya nahi hai')
        
        # Domain age check
        domain_age = result['checks']['domain_age']
        if domain_age and domain_age.get('is_new'):
            risk_score += 2
            warnings.append(f'⚠️ Naya domain ({domain_age.get("age_days")} din purana)')
        
        # Content check
        content = result['checks']['content']
        if content.get('suspicious_score', 0) >= 3:
            risk_score += 4
            warnings.append(f'⚠️ Phishing indicators found: {content.get("suspicious_score")}')
        
        # Brand impersonation check
        if content.get('is_impersonation'):
            risk_score += 5
            warnings.append('🚨 Brand impersonation detected!')
        
        if content.get('redirected'):
            risk_score += 1
            warnings.append('⚠️ URL redirect ho raha hai')
            warnings.append('⚠️ URL redirect ho raha hai')
        
        # Final verdict
        if risk_score >= 5:
            result['verdict'] = {
                'is_safe': False,
                'risk': 'HIGH',
                'message_hi': '🚨 KHATRE! Yeh website bahut dangerous hai. Bilkul mat kholo!',
                'warnings': warnings,
                'risk_score': risk_score
            }
        elif risk_score >= 3:
            result['verdict'] = {
                'is_safe': False,
                'risk': 'MEDIUM',
                'message_hi': '⚠️ Savdhaan! Yeh website suspicious hai. Dhyan se dekho.',
                'warnings': warnings,
                'risk_score': risk_score
            }
        else:
            result['verdict'] = {
                'is_safe': True,
                'risk': 'LOW',
                'message_hi': '✅ Website safe lag rahi hai.',
                'warnings': warnings,
                'risk_score': risk_score
            }
        
        return result

realtime_checker = RealtimeURLChecker()
