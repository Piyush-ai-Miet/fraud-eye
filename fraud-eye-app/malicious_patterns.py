import os
import re
import csv

class MaliciousPatternDetector:
    """
    Malicious Pattern Detector for QR Codes and URLs
    Detects SQL injection, XSS, command injection, and other attacks
    """
    def __init__(self):
        self.patterns = {
            'sqli': [],
            'xss': [],
            'cmdinj': [],
            'lfi': [],
            'xxe': [],
            'ssi': []
        }
        self.phishing_keywords = []
        self.indian_scam_patterns = []
        self.malicious_urls_db = []
        self.kaggle_database = []  # Kaggle dataset with 3,955 URLs
        self.load_patterns()
        self.load_custom_datasets()
        self.load_kaggle_database()
    
    def load_patterns(self):
        """Load attack patterns from dataset"""
        # Try multiple possible paths (prioritize non-archive paths for deployment)
        possible_paths = [
            'qr-dataset/words/',
            'fraud-eye-app/qr-dataset/words/',
            '../qr-dataset/words/',
            './qr-dataset/words/',
            '_archive/qr-dataset/words/',
            'fraud-eye-app/_archive/qr-dataset/words/',
            '../_archive/qr-dataset/words/'
        ]
        
        dataset_path = None
        for path in possible_paths:
            if os.path.exists(path):
                dataset_path = path
                break
        
        if not dataset_path:
            print("[PATTERN] ❌ QR dataset not found")
            return
        
        print(f"[PATTERN] ✅ Found QR dataset at: {dataset_path}")
        
        pattern_files = {
            'sqli': 'sqli.txt',
            'xss': 'xss.txt',
            'cmdinj': 'cmdinj.txt',
            'lfi': 'lfi.txt',
            'xxe': 'xxe.txt',
            'ssi': 'ssi.txt'
        }
        
        for attack_type, filename in pattern_files.items():
            filepath = os.path.join(dataset_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    patterns = [line.strip() for line in f if line.strip()]
                    # Load ALL patterns, not just 50
                    self.patterns[attack_type] = patterns
                    print(f"[PATTERN] ✅ Loaded {len(patterns)} {attack_type} patterns")
            except Exception as e:
                print(f"[PATTERN] ❌ Could not load {attack_type}: {e}")
                pass
    
    def load_custom_datasets(self):
        """Load custom datasets with flexible paths"""
        # Try multiple possible paths
        possible_data_paths = ['data/', 'fraud-eye-app/data/', './data/', '../data/']
        
        # Load phishing keywords
        for base_path in possible_data_paths:
            try:
                with open(os.path.join(base_path, 'phishing_keywords.txt'), 'r') as f:
                    self.phishing_keywords = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
                    break
            except:
                continue
        
        # Load Indian scam patterns
        for base_path in possible_data_paths:
            try:
                with open(os.path.join(base_path, 'indian_scam_patterns.txt'), 'r') as f:
                    self.indian_scam_patterns = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
                    break
            except:
                continue
        
        # Load malicious URLs database
        for base_path in possible_data_paths:
            try:
                with open(os.path.join(base_path, 'malicious_urls.csv'), 'r') as f:
                    reader = csv.DictReader(f)
                    self.malicious_urls_db = list(reader)
                    break
            except:
                continue
    
    def load_kaggle_database(self):
        """Load Kaggle balanced dataset (3,955 URLs)"""
        possible_data_paths = ['data/', 'fraud-eye-app/data/', './data/', '../data/']
        
        for base_path in possible_data_paths:
            try:
                filepath = os.path.join(base_path, 'kaggle_balanced_urls.csv')
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.kaggle_database = list(reader)
                    print(f"[KAGGLE] Loaded {len(self.kaggle_database)} URLs from Kaggle dataset")
                    return
            except Exception as e:
                continue
        
        print(f"[KAGGLE] Could not load Kaggle database from any path")
        self.kaggle_database = []
    
    def check_against_database(self, url):
        """Check URL against both custom database and Kaggle dataset"""
        url_lower = url.lower()
        
        # Check custom malicious URLs database
        for entry in self.malicious_urls_db:
            if entry['url'].lower() in url_lower or url_lower in entry['url'].lower():
                return entry['label'], entry['category']
        
        # Check Kaggle database (3,955 URLs)
        for entry in self.kaggle_database:
            kaggle_url = entry.get('url', '').lower()
            kaggle_type = entry.get('type', '').lower()  # Kaggle uses 'type' not 'label'
            
            # Exact match or substring match
            if kaggle_url and (kaggle_url in url_lower or url_lower in kaggle_url):
                # Kaggle types: phishing, malware, defacement
                if kaggle_type in ['phishing', 'malware', 'defacement']:
                    return 'malicious', kaggle_type
        
        return None, None
    
    def detect_attack(self, url):
        detected = []
        url_lower = url.lower()
        
        # SKIP pattern detection for UPI URLs (they are safe by design)
        if url_lower.startswith('upi://'):
            # UPI URLs are handled separately by UPI fraud detector
            # Don't apply generic attack pattern detection
            return detected
        
        # Check against known malicious URLs
        label, category = self.check_against_database(url)
        if label == 'malicious':
            detected.append(f'Known {category.replace("_", " ").title()}')
        
        # PHP Code Injection
        php_keywords = ['<?php', '<?=', 'system(', 'exec(', 'shell_exec(', 'passthru(', 'eval(', 'base64_decode(']
        if any(kw in url_lower for kw in php_keywords):
            detected.append('PHP Code Injection')
        
        # Check against loaded attack patterns from qr-dataset
        # SQL Injection patterns
        for pattern in self.patterns.get('sqli', []):
            if pattern.lower() in url_lower:
                detected.append('SQL Injection')
                break
        
        # XSS patterns
        for pattern in self.patterns.get('xss', []):
            if pattern.lower() in url_lower:
                detected.append('XSS Attack')
                break
        
        # Command Injection patterns
        for pattern in self.patterns.get('cmdinj', []):
            if pattern.lower() in url_lower:
                detected.append('Command Injection')
                break
        
        # LFI patterns
        for pattern in self.patterns.get('lfi', []):
            if pattern.lower() in url_lower:
                detected.append('Path Traversal')
                break
        
        # XXE patterns
        for pattern in self.patterns.get('xxe', []):
            if pattern.lower() in url_lower:
                detected.append('XXE Attack')
                break
        
        # Fallback keyword-based detection (if pattern matching didn't catch)
        if 'SQL Injection' not in detected:
            sql_keywords = ['select', 'union', 'insert', 'drop', 'delete', '--', 'or 1=1', 'or x=x']
            if any(kw in url_lower for kw in sql_keywords):
                detected.append('SQL Injection')
        
        if 'XSS Attack' not in detected:
            xss_keywords = ['<script', 'javascript:', 'onerror=', 'onload=', 'alert(']
            if any(kw in url_lower for kw in xss_keywords):
                detected.append('XSS Attack')
        
        if 'Command Injection' not in detected:
            cmd_keywords = ['|', ';', '&&', '$(', '`']
            if any(kw in url for kw in cmd_keywords):
                detected.append('Command Injection')
        
        if 'Path Traversal' not in detected:
            if '../' in url or '..\\' in url:
                detected.append('Path Traversal')
        
        # Phishing keywords
        phishing_found = [kw for kw in self.phishing_keywords if kw in url_lower]
        if len(phishing_found) >= 2:
            detected.append(f'Phishing ({len(phishing_found)} suspicious keywords)')
        
        # Indian scam patterns
        indian_scam_found = [pattern for pattern in self.indian_scam_patterns if pattern in url_lower]
        if indian_scam_found:
            detected.append(f'Indian Scam Pattern ({indian_scam_found[0]})')
        
        return detected
    
    def get_risk_score(self, attacks):
        if not attacks:
            return 0
        # Each attack adds 5 points for HIGH risk detection
        return len(attacks) * 5

detector = MaliciousPatternDetector()
