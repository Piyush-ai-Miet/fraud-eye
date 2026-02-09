"""
URL Validation Utility
Validates and extracts information from URLs
"""
import re
from urllib.parse import urlparse

def validate_url(url):
    """Validate if string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None

def is_https(url):
    """Check if URL uses HTTPS"""
    return url.startswith('https://')

def has_ip_address(url):
    """Check if URL contains IP address"""
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    return bool(re.search(ip_pattern, url))

def get_url_features(url):
    """Extract all URL features"""
    return {
        'length': len(url),
        'domain': extract_domain(url),
        'is_https': is_https(url),
        'has_ip': has_ip_address(url),
        'dot_count': url.count('.'),
        'slash_count': url.count('/'),
        'hyphen_count': url.count('-')
    }

if __name__ == '__main__':
    # Test
    test_url = "https://example.com/path?query=value"
    print(f"URL: {test_url}")
    print(f"Valid: {validate_url(test_url)}")
    print(f"Features: {get_url_features(test_url)}")
