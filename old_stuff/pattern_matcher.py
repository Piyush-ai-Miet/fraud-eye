"""
Pattern Matching Utility
Detect malicious patterns in URLs and text
"""
import re

class PatternMatcher:
    def __init__(self):
        self.sql_patterns = [
            r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
            r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
            r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))"
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*="
        ]
        
        self.phishing_keywords = [
            'urgent', 'verify', 'suspended', 'account blocked',
            'prize', 'lottery', 'winner', 'claim', 'free money'
        ]
    
    def detect_sql_injection(self, text):
        """Detect SQL injection patterns"""
        for pattern in self.sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def detect_xss(self, text):
        """Detect XSS patterns"""
        for pattern in self.xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def detect_phishing(self, text):
        """Detect phishing keywords"""
        text_lower = text.lower()
        found_keywords = []
        for keyword in self.phishing_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        return len(found_keywords) > 0, found_keywords
    
    def analyze(self, text):
        """Comprehensive analysis"""
        results = {
            'sql_injection': self.detect_sql_injection(text),
            'xss': self.detect_xss(text),
            'phishing': self.detect_phishing(text)[0],
            'phishing_keywords': self.detect_phishing(text)[1]
        }
        
        is_malicious = any([results['sql_injection'], results['xss'], results['phishing']])
        
        return {
            'is_malicious': is_malicious,
            'details': results
        }

if __name__ == '__main__':
    matcher = PatternMatcher()
    
    # Test cases
    test_cases = [
        "https://example.com/login",
        "https://bank.com/verify?urgent=true",
        "<script>alert('xss')</script>",
        "SELECT * FROM users WHERE id=1 OR 1=1--"
    ]
    
    for test in test_cases:
        result = matcher.analyze(test)
        print(f"\nText: {test}")
        print(f"Malicious: {result['is_malicious']}")
        print(f"Details: {result['details']}")
