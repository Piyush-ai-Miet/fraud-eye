from flask import Flask, render_template, request, jsonify, redirect, url_for
import re
import validators
from urllib.parse import urlparse
import os
import tempfile

# Scan logger for admin dashboard
try:
    from scan_logger import log_scan, get_scan_history, get_scan_stats
    SCAN_LOGGER_AVAILABLE = True
except Exception as e:
    SCAN_LOGGER_AVAILABLE = False
    print(f"Scan logger not available: {e}")

# Face authentication
try:
    from face_auth import verify_face, create_session, verify_session, logout_session
    FACE_AUTH_AVAILABLE = True
except Exception as e:
    FACE_AUTH_AVAILABLE = False
    print(f"Face auth not available: {e}")

# 2-Step Authentication
try:
    from admin_credentials import verify_credentials, is_face_registered, mark_face_registered
    from face_recognition_simple import register_admin_face_multi, verify_face as verify_face_opencv, get_registration_status
    TWO_STEP_AUTH_AVAILABLE = True
except Exception as e:
    TWO_STEP_AUTH_AVAILABLE = False
    print(f"2-step auth not available: {e}")

# QR code scanning imports
try:
    from simple_qr_scanner import scan_qr_from_upload, QR_SCANNING_AVAILABLE
except ImportError as e:
    QR_SCANNING_AVAILABLE = False
    print(f"QR scanning not available: {e}")

# Malicious pattern detector
try:
    from malicious_patterns import detector as pattern_detector
    PATTERN_DETECTION_AVAILABLE = True
except Exception as e:
    PATTERN_DETECTION_AVAILABLE = False
    print(f"Pattern detection not available: {e}")

# ML URL Classifier
try:
    from ml_url_classifier import ml_classifier
    ML_CLASSIFIER_AVAILABLE = ml_classifier.model_loaded
except Exception as e:
    ML_CLASSIFIER_AVAILABLE = False
    print(f"ML classifier not available: {e}")

# Real-time URL Checker
try:
    from realtime_url_checker import realtime_checker
    REALTIME_CHECKER_AVAILABLE = True
except Exception as e:
    REALTIME_CHECKER_AVAILABLE = False
    print(f"Real-time checker not available: {e}")

# Audio Fraud Classifier (Scikit-learn based)
try:
    from audio_fraud_classifier import audio_classifier
    AUDIO_CLASSIFIER_AVAILABLE = audio_classifier.model_loaded
    if not AUDIO_CLASSIFIER_AVAILABLE:
        print("⚠️ Audio classifier model not loaded - voice detection will use fallback")
except Exception as e:
    AUDIO_CLASSIFIER_AVAILABLE = False
    print(f"⚠️ Audio classifier not available (non-critical): {e}")

app = Flask(__name__)

# Educational explanations for warnings
EXPLANATIONS = {
    'hi': {
        'no_https': '❌ यह वेबसाइट HTTPS नहीं है, मतलब आपका डेटा सुरक्षित नहीं है। हैकर आपकी जानकारी चुरा सकते हैं।',
        'ip_address': '❌ यह IP address का उपयोग कर रहा है। असली वेबसाइट domain name इस्तेमाल करती हैं। यह फर्जी साइट हो सकती है।',
        'free_domain': '❌ यह मुफ्त डोमेन (.tk, .ml, .ga) का उपयोग कर रहा है। स्कैमर्स अक्सर ऐसे डोमेन इस्तेमाल करते हैं क्योंकि ये मुफ्त में मिलते हैं।',
        'phishing_keywords': '❌ इसमें फिशिंग शब्द हैं जैसे "urgent", "verify", "suspended"। यह आपको डराकर जल्दबाजी में पैसे देने की कोशिश है।',
        'sql_injection': '❌ इसमें SQL Injection attack है। यह आपके बैंक डेटाबेस में घुसकर जानकारी चुराने की कोशिश कर सकता है।',
        'xss_attack': '❌ इसमें XSS (Cross-Site Scripting) attack है। यह आपके ब्राउज़र में खतरनाक कोड चला सकता है और पासवर्ड चुरा सकता है।',
        'new_domain': '❌ यह domain बहुत नया है। असली कंपनियों के domain कई साल पुराने होते हैं। नए domain अक्सर स्कैम के लिए बनाए जाते हैं।',
        'ml_malicious': '🤖 हमारे AI model ने 651,000 URLs से सीखा है। यह URL उन खतरनाक patterns से मिलता है जो फिशिंग और मालवेयर साइट्स में होते हैं।'
    },
    'en': {
        'no_https': '❌ This website doesn\'t use HTTPS, meaning your data is not secure. Hackers can steal your information.',
        'ip_address': '❌ This uses an IP address. Real websites use domain names. This could be a fake site.',
        'free_domain': '❌ This uses a free domain (.tk, .ml, .ga). Scammers often use such domains because they\'re free.',
        'phishing_keywords': '❌ Contains phishing words like "urgent", "verify", "suspended". This is trying to scare you into giving money quickly.',
        'sql_injection': '❌ Contains SQL Injection attack. This can try to break into your bank database and steal information.',
        'xss_attack': '❌ Contains XSS (Cross-Site Scripting) attack. This can run dangerous code in your browser and steal passwords.',
        'new_domain': '❌ This domain is very new. Real companies have domains that are years old. New domains are often created for scams.',
        'ml_malicious': '🤖 Our AI model learned from 651,000 URLs. This URL matches dangerous patterns found in phishing and malware sites.'
    }
}

def get_educational_explanation(warnings, lang='hi'):
    """Generate educational explanations for warnings"""
    explanations = []
    exp_dict = EXPLANATIONS.get(lang, EXPLANATIONS['hi'])
    
    for warning in warnings:
        warning_lower = warning.lower()
        if 'https' in warning_lower or '🔓' in warning:
            explanations.append(exp_dict['no_https'])
        elif 'ip address' in warning_lower or '🌐' in warning:
            explanations.append(exp_dict['ip_address'])
        elif '.tk' in warning or '.ml' in warning or 'suspicious domain' in warning_lower:
            explanations.append(exp_dict['free_domain'])
        elif 'scam keywords' in warning_lower or 'phishing' in warning_lower:
            explanations.append(exp_dict['phishing_keywords'])
        elif 'sql' in warning_lower:
            explanations.append(exp_dict['sql_injection'])
        elif 'xss' in warning_lower:
            explanations.append(exp_dict['xss_attack'])
        elif 'days old' in warning_lower or 'new domain' in warning_lower:
            explanations.append(exp_dict['new_domain'])
        elif 'ml:' in warning_lower or 'malicious' in warning_lower:
            explanations.append(exp_dict['ml_malicious'])
    
    return list(set(explanations))  # Remove duplicates

class SimpleQRChecker:
    
    def __init__(self):
        # Scam patterns
        self.scam_keywords = [
            'verify', 'suspended', 'urgent', 'click now', 'confirm',
            'account blocked', 'prize', 'lottery', 'winner', 'claim',
            'free money', 'cash', 'reward', 'limited time', 'otp', 'pin', 'cvv'
        ]
        
        # Suspicious domains
        self.suspicious_domains = [
            '.tk', '.ml', '.ga', '.cf', '.gq',  # Free domains
            'bit.ly', 'tinyurl', 'goo.gl'  # URL shorteners
        ]
        
        # Safe domains
        self.safe_domains = [
            'paytm.com', 'phonepe.com', 'googlepay.com', 'bhim.upi',
            'sbi.co.in', 'hdfcbank.com', 'icicibank.com',
            'gov.in', 'nic.in', 'india.gov.in'
        ]
    
    def check_url_safety(self, url):
        """
        Simple URL checker with PRIORITY system
        1. VirusTotal (70+ engines) - PRIMARY
        2. Dangerous.domains (1M+ domains) - FALLBACK
        3. URLScan.io (Community + Domain info) - FALLBACK
        """
        risk_score = 0
        warnings = []
        realtime_result = None
        
        # Check if URL hai (including UPI URLs)
        is_upi = url.lower().startswith('upi://')
        is_valid_url = validators.url(url) or is_upi
        
        if not is_valid_url:
            return {
                'is_safe': True,
                'risk': 'LOW',
                'message_hi': 'Yeh sirf text hai, koi link nahi hai.',
                'warnings': [],
                'is_not_url': True  # Flag to indicate it's not a URL
            }
        
        url_lower = url.lower()
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Third-party API checks with PRIORITY system
        try:
            from third_party_url_checker import third_party_checker
            
            print(f"\n[URL CHECK] Checking URL: {url}")
            
            # Run comprehensive check with PRIORITY: VirusTotal > Others
            comprehensive_result = third_party_checker.check_url_comprehensive(url)
            
            # Process results from each service
            checks = comprehensive_result.get('checks', {})
            url_info = comprehensive_result.get('url_info', {})
            primary_source = comprehensive_result.get('primary_source', 'Unknown')
            
            # PRIORITY 1: VirusTotal results (if available)
            if 'virustotal' in checks:
                vt = checks['virustotal']
                vt_verdict = vt.get('verdict')
                
                if vt_verdict == 'MALICIOUS':
                    risk_score += 15  # Highest priority
                    warnings.append(f"✅ {vt.get('detection_rate')} engines detected malicious")
                    warnings.append(f"✅ {vt.get('malicious_count')} engines flagged as dangerous")
                elif vt_verdict == 'SUSPICIOUS':
                    risk_score += 10
                    warnings.append(f"✅ {vt.get('suspicious_count')} engines suspicious")
                elif vt_verdict == 'SAFE':
                    warnings.append(f"✅ Clean ({vt.get('detection_rate')})")
                
                # Show primary check (without mentioning VirusTotal)
                warnings.append(f"✅ Primary Check: 70+ engines")
            
            # Check if VirusTotal limit exceeded
            elif comprehensive_result.get('virustotal_limit_exceeded'):
                warnings.append(f"✅ Daily limit exceeded")
                warnings.append(f"✅ Using fallback APIs")
            
            # FALLBACK: Dangerous.domains results
            if 'dangerous_domains' in checks:
                dd = checks['dangerous_domains']
                if dd.get('verdict') == 'MALICIOUS':
                    risk_score += 8
                    warnings.append(f"✅ Dangerous.domains: Malicious domain detected")
                elif dd.get('verdict') == 'SAFE' and 'virustotal' not in checks:
                    warnings.append(f"✅ Dangerous.domains: Clean")
            
            # URLScan.io results (always show for domain info)
            if 'urlscan' in checks:
                urlscan = checks['urlscan']
                if urlscan.get('verdict') == 'MALICIOUS':
                    risk_score += 8
                    warnings.append(f"✅ URLScan.io: Malicious detected")
                    if urlscan.get('score'):
                        warnings.append(f"✅ Threat Score: {urlscan['score']}/100")
                elif urlscan.get('verdict') == 'SAFE' and 'virustotal' not in checks:
                    warnings.append(f"✅ URLScan.io: Safe")
            
            # Add complete URL information in clean format
            if url_info:
                warnings.append("") # Blank line for separation
                warnings.append("📋 URL Information:")
                if url_info.get('domain'):
                    warnings.append(f"✅ Domain: {url_info['domain']}")
                if url_info.get('ip'):
                    warnings.append(f"✅ IP Address: {url_info['ip']}")
                if url_info.get('country'):
                    warnings.append(f"✅ Country: {url_info['country']}")
                if url_info.get('server'):
                    warnings.append(f"✅ Server: {url_info['server']}")
            
            # Add decision reason (WITHOUT bullet point and without mentioning VirusTotal)
            if comprehensive_result.get('decision_reason'):
                decision = comprehensive_result['decision_reason']
                # Remove "VirusTotal (PRIMARY)" from decision text
                decision = decision.replace('VirusTotal (PRIMARY)', 'Primary check')
                decision = decision.replace('VirusTotal', 'Security scan')
                warnings.append("")
                warnings.append(f"Decision: {decision}")
            
            realtime_result = comprehensive_result
            
        except Exception as e:
            print(f"[URL CHECK] Third-party check error: {e}")
            warnings.append("⚠️ Unable to verify URL with third-party services")
        
        # Basic checks (always run)
        
        # Check 1: HTTPS nahi hai?
        if parsed.scheme != 'https':
            risk_score += 2
            warnings.append('🔓 No HTTPS - Data encrypted nahi hai')
        
        # Check 2: IP address use kar raha hai?
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 3
            warnings.append('🌐 IP address used - Suspicious')
        
        # Check 3: Suspicious domain?
        for sus_domain in self.suspicious_domains:
            if sus_domain in domain:
                risk_score += 2
                warnings.append(f'⚠️ Suspicious domain extension: {sus_domain}')
        
        # Final decision
        if risk_score >= 10:
            return {
                'is_safe': False,
                'risk': 'HIGH',
                'message_hi': f'🚨 KHATRE! Domain "{domain}" dangerous hai!',
                'warnings': warnings,
                'realtime_result': realtime_result,
                'domain': domain,
                'educational_explanations': get_educational_explanation(warnings, 'hi')
            }
        elif risk_score >= 5:
            return {
                'is_safe': False,
                'risk': 'MEDIUM',
                'message_hi': f'⚠️ Savdhaan! Domain "{domain}" suspicious hai.',
                'warnings': warnings,
                'realtime_result': realtime_result,
                'domain': domain,
                'educational_explanations': get_educational_explanation(warnings, 'hi')
            }
        else:
            return {
                'is_safe': True,
                'risk': 'LOW',
                'message_hi': f'✅ Domain "{domain}" safe lag raha hai.',
                'warnings': warnings,
                'realtime_result': realtime_result,
                'domain': domain,
                'educational_explanations': []
            }

checker = SimpleQRChecker()

def detect_upi_payment_direction(url):
    """
    Detect if UPI QR code is for sending or receiving money
    Returns: (direction, message, amount, is_payment_request)
    - direction: 'SEND' (payment request), 'RECEIVE' (collect money), or 'UNKNOWN'
    - message: Warning/confirmation message
    - amount: Extracted amount if present
    - is_payment_request: True if it's a payment request (HIGH RISK)
    
    LOGIC:
    1. Normal UPI receive QR (pa=, pn=, no amount) → SAFE
    2. UPI receive QR with embedded amount → SUSPICIOUS (amount pre-filled)
    3. Payment REQUEST (mode=02, intent-based) → DANGEROUS
    """
    if not url:
        return 'UNKNOWN', '', None, False
    
    url_lower = url.lower()
    
    # Check if it's a UPI URL
    if 'upi://' in url_lower or 'pay?pa=' in url_lower:
        # Extract amount if present
        import re
        amount = None
        amount_match = re.search(r'am=([0-9.]+)', url_lower)
        if amount_match:
            amount = amount_match.group(1)
        
        # Check for PAYMENT REQUEST indicators (mode=02, intent-based)
        payment_request_indicators = [
            'mode=02',  # collect request mode - THIS IS PAYMENT REQUEST
            'intent=collect',  # explicit collect intent
            'type=collect',  # collect type
        ]
        
        has_request_indicator = any(indicator in url_lower for indicator in payment_request_indicators)
        
        # CASE 1: Payment REQUEST (mode=02 or intent-based) - DANGEROUS!
        if has_request_indicator:
            if amount:
                message = f'🚨 PAYMENT REQUEST: ₹{amount} मांगा जा रहा है! यह खतरनाक है!'
            else:
                message = '🚨 PAYMENT REQUEST: पैसे मांगे जा रहे हैं! यह खतरनाक है!'
            return 'SEND', message, amount, True
        
        # CASE 2: Normal receive QR with EMBEDDED AMOUNT - SUSPICIOUS
        if amount and 'pa=' in url_lower and 'pn=' in url_lower:
            message = f'⚠️ Amount pre-filled: ₹{amount} - Dhyan se check karein!'
            return 'RECEIVE', message, amount, False  # Not a payment request, but has amount
        
        # CASE 3: Normal receive QR WITHOUT amount - SAFE
        if 'pa=' in url_lower and 'pn=' in url_lower:
            return 'RECEIVE', '✅ Normal UPI receive QR - Safe for collecting payments', None, False
    
    return 'UNKNOWN', '', None, False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanner')
def scanner():
    """Full scanner page with all features"""
    return render_template('demo_full.html')

@app.route('/api/latest-scams', methods=['GET'])
def get_latest_scams():
    """Get latest scam news"""
    try:
        import json
        with open('data/latest_scams.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'scams': []
        }), 500

@app.route('/api/check-url', methods=['POST'])
def check_url():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL nahi mila'}), 400
    
    # Auto-add https:// if missing (for domains like "google.com" or "br-icloud.com.br")
    if not url.startswith(('http://', 'https://', 'upi://')):
        url = 'https://' + url
        print(f"[URL CHECK] Auto-added https:// → {url}")
    
    result = checker.check_url_safety(url)
    result['content'] = url
    
    # Log scan
    if SCAN_LOGGER_AVAILABLE:
        user_ip = request.remote_addr
        log_scan('url', url, result, user_ip)
    
    return jsonify(result)

@app.route('/api/analyze-audio', methods=['POST'])
def analyze_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'Audio file nahi mili'}), 400
    
    file = request.files['audio_file']
    
    if file.filename == '':
        return jsonify({'error': 'File select nahi ki'}), 400
    
    # Check file format FIRST - reject unsupported formats
    allowed_formats = ('.wav', '.mp3', '.ogg', '.m4a', '.flac')
    if not file.filename.lower().endswith(allowed_formats):
        return jsonify({
            'error': '❌ यह audio format support नहीं है',
            'message_hi': 'केवल WAV, MP3, OGG, M4A, या FLAC files upload करें',
            'supported_formats': 'WAV, MP3, OGG, M4A, FLAC',
            'your_format': file.filename.split('.')[-1].upper() if '.' in file.filename else 'UNKNOWN'
        }), 400
    
    print(f"\n[AUDIO] Processing file: {file.filename}")
    
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            file.save(tmp.name)
            file_path = tmp.name
        
        # Initialize variables
        is_fake = False
        confidence = 0.0
        message = ''
        message_detail = ''
        
        # Use Scikit-learn ML classifier (lightweight, fast)
        if AUDIO_CLASSIFIER_AVAILABLE:
            print("[AUDIO] Using ML classifier...")
            ml_result = audio_classifier.predict(file_path)
            
            if ml_result:
                os.unlink(file_path)
                
                is_fake = ml_result['is_fake']
                confidence = ml_result['confidence']
                
                print(f"[AUDIO] Result: {ml_result['label']} (confidence: {confidence:.2f})")
                
                if is_fake:
                    message = f'🚨 KHATRE! Yeh audio AI/FAKE hai!'
                    message_detail = f'ML Model: {confidence*100:.1f}% confident yeh fake hai'
                else:
                    message = f'✅ Audio REAL lag raha hai'
                    message_detail = f'ML Model: {confidence*100:.1f}% confident yeh real hai'
                
                # Log scan
                if SCAN_LOGGER_AVAILABLE:
                    user_ip = request.remote_addr
                    log_result = {
                        'is_safe': not is_fake,
                        'risk': 'HIGH' if is_fake else 'LOW',
                        'warnings': [message_detail]
                    }
                    log_scan('voice', file.filename, log_result, user_ip)
                
                return jsonify({
                    'is_suspicious': is_fake,
                    'confidence': confidence,
                    'reason': message,
                    'warnings': [
                        message_detail,
                        f'Real probability: {ml_result["probability_real"]*100:.1f}%',
                        f'Fake probability: {ml_result["probability_fake"]*100:.1f}%'
                    ],
                    'ml_based': True,
                    'label': ml_result['label'],
                    'voice_alert': 'fake' if is_fake else 'real',
                    'educational_explanation': '🤖 हमारे AI model ने 200 audio files से सीखा है। यह audio में pitch, frequency, और spectral patterns को analyze करता है। Fake audio में unnatural patterns होते हैं।' if is_fake else ''
                })
        
        print("[AUDIO] ML classifier not available, using rule-based...")
        
        # Fallback to rule-based
        file_size = os.path.getsize(file_path)
        
        warnings = []
        risk_score = 0
        
        if file_size < 10000:
            warnings.append('File bahut chhoti hai - suspicious')
            risk_score += 2
        
        if file_size > 5000000:
            warnings.append('File bahut badi hai - suspicious')
            risk_score += 1
        
        if risk_score >= 2:
            is_suspicious = True
            confidence = 0.7
            message = '⚠️ DHYAN RAHE! Yeh audio suspicious lag raha hai.'
        else:
            is_suspicious = False
            confidence = 0.3
            message = '✅ Audio normal lag raha hai.'
        
        os.unlink(file_path)
        
        # Log scan for fallback method too
        if SCAN_LOGGER_AVAILABLE:
            user_ip = request.remote_addr
            log_result = {
                'is_safe': not is_suspicious,
                'risk': 'MEDIUM' if is_suspicious else 'LOW',
                'warnings': warnings if warnings else ['Rule-based analysis']
            }
            log_scan('voice', file.filename, log_result, user_ip)
        
        return jsonify({
            'is_suspicious': is_suspicious,
            'confidence': confidence,
            'reason': message,
            'warnings': warnings,
            'file_size': f'{file_size / 1024:.2f} KB',
            'ml_based': False
        })
        
    except Exception as e:
        print(f"[AUDIO] Error: {e}")
        return jsonify({'error': f'Audio analysis error: {str(e)}'}), 500

@app.route('/api/scan-qr-url', methods=['POST'])
def scan_qr_url():
    """QR code URL analysis - User enters URL manually from QR"""
    data = request.get_json()
    qr_url = data.get('url', '')
    
    if not qr_url:
        return jsonify({'error': 'URL nahi mila'}), 400
    
    # Detect UPI payment direction with enhanced details
    payment_direction, direction_message, amount, is_payment_request = detect_upi_payment_direction(qr_url)
    
    # ML-based analysis for QR codes
    risk_score = 0
    warnings = []
    ml_result = None
    
    # CASE 1: Payment REQUEST (mode=02) - HIGH RISK
    if is_payment_request:
        risk_score += 5  # Automatically HIGH RISK
        if amount:
            warnings.append(f"🚨 PAYMENT REQUEST: ₹{amount} मांगा जा रहा है!")
            warnings.append(f"⚠️ यह खतरनाक है! Agar pay karenge to ₹{amount} aapke account se jayega!")
        else:
            warnings.append("🚨 PAYMENT REQUEST detected - यह खतरनाक है!")
            warnings.append("⚠️ Yeh QR code aapse paise maang raha hai!")
    
    # CASE 2: Normal receive QR with EMBEDDED AMOUNT - MEDIUM RISK
    elif payment_direction == 'RECEIVE' and amount:
        risk_score += 2  # Medium risk - amount pre-filled
        warnings.append(f"⚠️ Amount pre-filled: ₹{amount}")
        warnings.append("💡 Dhyan se check karein - Amount pehle se set hai!")
        warnings.append("✅ Agar aap jaante ho ki yeh kitna hona chahiye, to safe hai")
    
    # CASE 3: Normal receive QR WITHOUT amount - SAFE
    elif payment_direction == 'RECEIVE':
        warnings.append("✅ Normal UPI receive QR - Safe for collecting payments")
        warnings.append("💚 Koi amount pre-filled nahi hai - Aap khud amount enter kar sakte ho")
    
    parsed = urlparse(qr_url)
    domain = parsed.netloc.lower() if parsed.netloc else qr_url
    
    # Check against Kaggle database FIRST (3,955 known URLs)
    if PATTERN_DETECTION_AVAILABLE:
        db_label, db_category = pattern_detector.check_against_database(qr_url)
        if db_label == 'malicious':
            risk_score += 10  # Very high risk for known malicious URLs
            warnings.append(f'🚨 Known {db_category.replace("_", " ").title()} URL in database!')
    
    # Pattern detection (ALWAYS check, even for non-URLs - catches code injection)
    if PATTERN_DETECTION_AVAILABLE:
        attacks = pattern_detector.detect_attack(qr_url)
        if attacks:
            risk_score += pattern_detector.get_risk_score(attacks)
            for attack in attacks:
                warnings.append(f'⚠️ {attack}')
    
    # ML Model prediction (only for valid URLs)
    if ML_CLASSIFIER_AVAILABLE and validators.url(qr_url):
        ml_result = ml_classifier.predict(qr_url)
        if ml_result and ml_result['is_malicious']:
            confidence_pct = ml_result['confidence'] * 100
            warnings.append(f"🤖 ML: {ml_result['label']} ({confidence_pct:.1f}%)")
            risk_score += 5
    
    # Basic checks
    if validators.url(qr_url):
        if parsed.scheme != 'https' and not qr_url.startswith('upi://'):
            risk_score += 1
            warnings.append('🔓 No HTTPS')
        
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 3
            warnings.append('🌐 IP address')
    
    # Final verdict
    if risk_score >= 5:
        result = {
            'is_safe': False,
            'risk': 'HIGH',
            'message_hi': f'🚨 KHATRE! {"Payment request detected!" if is_payment_request else "QR code mein dangerous link hai!"}',
            'warnings': warnings,
            'ml_result': ml_result,
            'educational_explanations': get_educational_explanation(warnings, 'hi'),
            'voice_alert': 'malicious',
            'payment_direction': payment_direction,
            'payment_amount': amount,
            'is_payment_request': is_payment_request
        }
    elif risk_score >= 3:
        result = {
            'is_safe': False,
            'risk': 'MEDIUM',
            'message_hi': f'⚠️ Savdhaan! QR code suspicious hai.',
            'warnings': warnings,
            'ml_result': ml_result,
            'educational_explanations': get_educational_explanation(warnings, 'hi'),
            'voice_alert': 'suspicious',
            'payment_direction': payment_direction,
            'payment_amount': amount,
            'is_payment_request': is_payment_request
        }
    else:
        result = {
            'is_safe': True,
            'risk': 'LOW',
            'message_hi': f'✅ QR code safe lag raha hai.',
            'warnings': warnings,
            'ml_result': ml_result,
            'educational_explanations': [],
            'voice_alert': 'safe',
            'payment_direction': payment_direction,
            'payment_amount': amount,
            'is_payment_request': is_payment_request
        }
    
    result['content'] = qr_url
    result['qr_type'] = 'QRCODE'
    result['domain'] = domain
    
    # Log scan
    if SCAN_LOGGER_AVAILABLE:
        user_ip = request.remote_addr
        log_scan('qr', qr_url, result, user_ip)
    
    return jsonify(result)

@app.route('/api/scan-qr', methods=['POST'])
def scan_qr():
    """QR code image scanning"""
    if not QR_SCANNING_AVAILABLE:
        return jsonify({
            'error': 'QR image scanning not available',
            'message': 'Please scan QR code with your phone camera and enter the URL manually',
            'alternative_endpoint': '/api/scan-qr-url',
            'instructions': 'Use your phone to scan QR code, copy the URL, and paste it in the URL checker'
        }), 400
    
    if 'qr_image' not in request.files:
        return jsonify({'error': 'QR image nahi mili'}), 400
    
    file = request.files['qr_image']
    
    if file.filename == '':
        return jsonify({'error': 'File select nahi ki'}), 400
    
    print(f"\n[QR SCAN] Processing file: {file.filename}")
    
    try:
        from simple_qr_scanner import scan_qr_from_upload
        
        qr_url = scan_qr_from_upload(file)
        
        print(f"[QR SCAN] Result: {qr_url if qr_url else 'NOT DETECTED'}")
        
        if not qr_url:
            return jsonify({
                'error': 'QR code nahi mila',
                'message_hi': '❌ Image mein QR code detect nahi hua',
                'suggestions': [
                    '📸 Clear photo upload karo',
                    '💡 QR code ko center mein rakho',
                    '🔆 Achhi lighting mein photo lo',
                    '📱 Phone camera se scan karke URL manually enter karo'
                ]
            }), 400
        
        # Detect UPI payment direction
        payment_direction, direction_message, amount, is_payment_request = detect_upi_payment_direction(qr_url)
        
        # ML-based analysis for QR codes
        risk_score = 0
        warnings = []
        ml_result = None
        
        # CASE 1: Payment REQUEST (mode=02) - HIGH RISK
        if is_payment_request:
            risk_score += 5  # Automatically HIGH RISK
            if amount:
                warnings.append(f"🚨 PAYMENT REQUEST: ₹{amount} मांगा जा रहा है!")
                warnings.append(f"⚠️ यह खतरनाक है! Agar pay karenge to ₹{amount} aapke account se jayega!")
            else:
                warnings.append("🚨 PAYMENT REQUEST detected - यह खतरनाक है!")
        
        # CASE 2: Normal receive QR with EMBEDDED AMOUNT - MEDIUM RISK
        elif payment_direction == 'RECEIVE' and amount:
            risk_score += 2  # Medium risk - amount pre-filled
            warnings.append(f"⚠️ Amount pre-filled: ₹{amount}")
            warnings.append("💡 Dhyan se check karein - Amount pehle se set hai!")
            warnings.append("✅ Agar aap jaante ho ki yeh kitna hona chahiye, to safe hai")
        
        # CASE 3: Normal receive QR WITHOUT amount - SAFE
        elif payment_direction == 'RECEIVE':
            warnings.append("✅ Normal UPI receive QR - Safe for collecting payments")
            warnings.append("💚 Koi amount pre-filled nahi hai - Aap khud amount enter kar sakte ho")
        
        parsed = urlparse(qr_url)
        domain = parsed.netloc.lower() if parsed.netloc else qr_url
        
        # Check against Kaggle database FIRST (3,955 known URLs)
        if PATTERN_DETECTION_AVAILABLE:
            db_label, db_category = pattern_detector.check_against_database(qr_url)
            if db_label == 'malicious':
                risk_score += 10  # Very high risk for known malicious URLs
                warnings.append(f'🚨 Known {db_category.replace("_", " ").title()} URL in database!')
        
        # Pattern detection (for all strings, not just URLs)
        if PATTERN_DETECTION_AVAILABLE:
            attacks = pattern_detector.detect_attack(qr_url)
            if attacks:
                risk_score += pattern_detector.get_risk_score(attacks)
                for attack in attacks:
                    warnings.append(f'⚠️ {attack}')
        
        # ML Model prediction (only for valid URLs)
        if ML_CLASSIFIER_AVAILABLE and validators.url(qr_url):
            ml_result = ml_classifier.predict(qr_url)
            if ml_result and ml_result['is_malicious']:
                confidence_pct = ml_result['confidence'] * 100
                warnings.append(f"🤖 ML: {ml_result['label']} ({confidence_pct:.1f}%)")
                risk_score += 5
        
        # Basic checks
        if validators.url(qr_url):
            if parsed.scheme != 'https':
                risk_score += 1
                warnings.append('🔓 No HTTPS')
            
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                risk_score += 3
                warnings.append('🌐 IP address')
        
        # Final verdict
        if risk_score >= 5:
            result = {
                'is_safe': False,
                'risk': 'HIGH',
                'message_hi': f'🚨 KHATRE! QR code mein dangerous link hai!',
                'warnings': warnings,
                'ml_result': ml_result,
                'educational_explanations': get_educational_explanation(warnings, 'hi'),
                'voice_alert': 'malicious',
                'payment_direction': payment_direction
            }
        elif risk_score >= 3:
            result = {
                'is_safe': False,
                'risk': 'MEDIUM',
                'message_hi': f'⚠️ Savdhaan! QR code suspicious hai.',
                'warnings': warnings,
                'ml_result': ml_result,
                'educational_explanations': get_educational_explanation(warnings, 'hi'),
                'voice_alert': 'suspicious',
                'payment_direction': payment_direction
            }
        else:
            result = {
                'is_safe': True,
                'risk': 'LOW',
                'message_hi': f'✅ QR code safe lag raha hai.',
                'warnings': warnings,
                'ml_result': ml_result,
                'educational_explanations': [],
                'voice_alert': 'safe',
                'payment_direction': payment_direction
            }
        
        result['content'] = qr_url
        result['qr_type'] = 'QRCODE'
        result['domain'] = domain
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'QR scan error: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Fraud Eye is running!'})

@app.route('/api/system-status')
def system_status():
    """Diagnostic endpoint to check what's loaded on Render"""
    import os
    
    status = {
        'server': 'running',
        'working_directory': os.getcwd(),
        'modules': {
            'scan_logger': SCAN_LOGGER_AVAILABLE,
            'face_auth': FACE_AUTH_AVAILABLE,
            'two_step_auth': TWO_STEP_AUTH_AVAILABLE,
            'qr_scanning': QR_SCANNING_AVAILABLE,
            'pattern_detection': PATTERN_DETECTION_AVAILABLE,
            'ml_classifier': ML_CLASSIFIER_AVAILABLE,
            'realtime_checker': REALTIME_CHECKER_AVAILABLE,
            'audio_classifier': AUDIO_CLASSIFIER_AVAILABLE
        },
        'models': {},
        'data_files': {}
    }
    
    # Check model files
    models_dir = 'models'
    if os.path.exists(models_dir):
        status['models']['directory_exists'] = True
        status['models']['files'] = os.listdir(models_dir)
    else:
        status['models']['directory_exists'] = False
        status['models']['error'] = 'Models directory not found'
    
    # Check data files
    data_dir = 'data'
    if os.path.exists(data_dir):
        status['data_files']['directory_exists'] = True
        status['data_files']['files'] = os.listdir(data_dir)
    else:
        status['data_files']['directory_exists'] = False
    
    # Check ML classifier details
    if ML_CLASSIFIER_AVAILABLE:
        try:
            from ml_url_classifier import ml_classifier
            status['ml_classifier_details'] = {
                'model_loaded': ml_classifier.model_loaded,
                'has_model': ml_classifier.model is not None,
                'has_features': ml_classifier.feature_names is not None
            }
        except Exception as e:
            status['ml_classifier_details'] = {'error': str(e)}
    
    # Check audio classifier details
    if AUDIO_CLASSIFIER_AVAILABLE:
        try:
            from audio_fraud_classifier import audio_classifier
            status['audio_classifier_details'] = {
                'model_loaded': audio_classifier.model_loaded,
                'has_model': audio_classifier.model is not None
            }
        except Exception as e:
            status['audio_classifier_details'] = {'error': str(e)}
    
    return jsonify(status)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard - Smart routing: First time = Register, Logged in = Dashboard, Not logged in = Login"""
    
    # CASE 1: First time setup - No face registered yet
    if TWO_STEP_AUTH_AVAILABLE and not is_face_registered():
        print("[ADMIN] First time - showing registration page")
        return render_template('admin_register.html')
    
    # CASE 2: Check if user is logged in
    token = request.cookies.get('admin_token') or request.args.get('token')
    
    if not token or not FACE_AUTH_AVAILABLE or not verify_session(token):
        # Not logged in - redirect to login
        print("[ADMIN] Not logged in - redirecting to login")
        return redirect('/admin/login')
    
    # CASE 3: Valid session - show dashboard
    print("[ADMIN] Valid session - showing dashboard")
    return render_template('admin.html')

@app.route('/admin/login')
def admin_login_2step():
    """2-Step authentication login page"""
    print("[LOGIN] Loading 2-step login page")
    
    # If not registered yet, redirect to /admin (which will show registration)
    if TWO_STEP_AUTH_AVAILABLE and not is_face_registered():
        print("[LOGIN] Admin not registered - redirecting to /admin")
        return redirect('/admin')
    
    # Show login page
    print("[LOGIN] Showing 2-step authentication page")
    return render_template('admin_login_simple.html')

@app.route('/admin/register')
def admin_register_page():
    """BLOCKED - Direct access not allowed"""
    return """
    <html>
    <head>
        <title>Access Denied - Fraud Eye</title>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <h1 style="font-size: 3em;">🚫 Access Denied</h1>
        <p style="font-size: 1.5em; margin: 30px 0;">Direct registration is not allowed!</p>
        <p style="font-size: 1.2em; opacity: 0.9;">Please use the main admin page:</p>
        <a href="/admin" style="display: inline-block; margin-top: 30px; padding: 15px 40px; background: white; color: #667eea; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 1.2em;">
            Go to Admin Panel
        </a>
    </body>
    </html>
    """, 403

@app.route('/api/admin/register', methods=['POST'])
def register_admin():
    """Register new admin with username, password, and multi-angle face"""
    if not TWO_STEP_AUTH_AVAILABLE:
        return jsonify({'success': False, 'message': '2-step auth not available'}), 500
    
    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')
    angle = request.form.get('angle', 'center')  # center, left, right, up, down
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    if 'face_image' not in request.files:
        return jsonify({'success': False, 'message': 'Face image required'}), 400
    
    file = request.files['face_image']
    image_data = file.read()
    
    try:
        # Create admin credentials (only once)
        if angle == 'center':
            from admin_credentials import create_admin
            create_admin(username, password)
        
        # Register face for this angle
        success, message = register_admin_face_multi(image_data, angle)
        
        if not success:
            return jsonify({'success': False, 'message': f'Face registration failed: {message}'}), 400
        
        # Check registration status
        status = get_registration_status()
        all_registered = all(status.values())
        
        # Mark as registered when all angles are done
        if all_registered:
            mark_face_registered()
        
        print(f"[ADMIN] Face angle '{angle}' registered for: {username}")
        
        return jsonify({
            'success': True,
            'message': message,
            'angle': angle,
            'status': status,
            'all_registered': all_registered
        })
        
    except Exception as e:
        print(f"[ADMIN] Registration error: {e}")
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'}), 500

@app.route('/api/admin/registration-status', methods=['GET'])
def get_admin_registration_status():
    """Get status of multi-angle face registration"""
    if not TWO_STEP_AUTH_AVAILABLE:
        return jsonify({'error': 'Auth not available'}), 500
    
    status = get_registration_status()
    return jsonify({
        'status': status,
        'all_registered': all(status.values()) if status else False
    })

@app.route('/api/admin/verify-credentials', methods=['POST'])
def verify_admin_credentials():
    """Step 1: Verify username and password"""
    if not TWO_STEP_AUTH_AVAILABLE:
        return jsonify({'error': '2-step auth not available'}), 500
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'verified': False, 'message': 'Username and password required'}), 400
    
    verified, message = verify_credentials(username, password)
    
    if verified:
        # Create temporary token for Step 2
        import secrets
        temp_token = secrets.token_urlsafe(16)
        
        # Store in session (in-memory for now)
        if not hasattr(app, 'temp_sessions'):
            app.temp_sessions = {}
        
        app.temp_sessions[temp_token] = {
            'username': username,
            'timestamp': __import__('time').time(),
            'verified': True
        }
        
        print(f"[AUTH] Step 1 passed: {username} - temp token: {temp_token[:10]}...")
        
        return jsonify({
            'verified': True,
            'message': message,
            'face_registered': is_face_registered(),
            'temp_token': temp_token  # Send to client for Step 2
        })
    else:
        print(f"[AUTH] Step 1 failed: {username}")
        return jsonify({'verified': False, 'message': message}), 401

@app.route('/api/admin/verify-face-2step', methods=['POST'])
def verify_face_2step():
    """Step 2: Verify face after credentials - REQUIRES TEMP TOKEN FROM STEP 1"""
    if not TWO_STEP_AUTH_AVAILABLE:
        return jsonify({'verified': False, 'message': '2-step auth not available'}), 500
    
    # Check for temp token from Step 1
    temp_token = request.form.get('temp_token') or request.headers.get('X-Temp-Token')
    
    if not temp_token:
        print("[FACE] Step 2 failed: No temp token - credentials not verified")
        return jsonify({
            'verified': False,
            'message': 'Please verify username and password first (Step 1)'
        }), 403
    
    # Verify temp token
    if not hasattr(app, 'temp_sessions') or temp_token not in app.temp_sessions:
        print("[FACE] Step 2 failed: Invalid temp token")
        return jsonify({
            'verified': False,
            'message': 'Invalid or expired session. Please login again.'
        }), 403
    
    # Check token expiry (5 minutes)
    import time
    session_data = app.temp_sessions[temp_token]
    if time.time() - session_data['timestamp'] > 300:  # 5 minutes
        del app.temp_sessions[temp_token]
        print("[FACE] Step 2 failed: Temp token expired")
        return jsonify({
            'verified': False,
            'message': 'Session expired. Please login again.'
        }), 403
    
    if 'face_image' not in request.files:
        return jsonify({'verified': False, 'message': 'No face image provided'}), 400
    
    file = request.files['face_image']
    image_data = file.read()
    
    username = session_data['username']
    print(f"[FACE] Step 2: Verifying face for user: {username}")
    
    # Check if admin face is registered
    if not is_face_registered():
        print("[FACE] ❌ Admin face not registered. Please register first.")
        return jsonify({
            'verified': False,
            'message': 'Admin face not registered. Please register first.',
            'similarity': 0,
            'first_time': True
        }), 403
    
    # Verify face against registered admin faces
    print("[FACE] Verifying face...")
    try:
        verified, message, similarity = verify_face_opencv(image_data)
        similarity = float(similarity)  # Ensure Python float for JSON
    except Exception as e:
        print(f"[FACE] Error during verification: {e}")
        return jsonify({
            'verified': False,
            'message': f'Face verification error: {str(e)}'
        }), 500
    
    if verified:
        token = create_session()
        
        # Clean up temp session
        del app.temp_sessions[temp_token]
        
        response = jsonify({
            'verified': True,
            'token': token,
            'message': message,
            'similarity': similarity,
            'first_time': False
        })
        response.set_cookie('admin_token', token, max_age=86400, httponly=True)
        
        print(f"[FACE] Verification successful for {username}: {similarity:.1f}%")
        return response
    else:
        print(f"[FACE] Verification failed for {username}: {message}")
        return jsonify({
            'verified': False,
            'message': message,
            'similarity': similarity
        }), 401

@app.route('/api/admin/verify-face', methods=['POST'])
def verify_face_api():
    """DEPRECATED - Use /api/admin/verify-face-2step instead"""
    return jsonify({
        'error': 'This endpoint is deprecated. Please use 2-step authentication.',
        'message': 'Use /admin/login for proper authentication',
        'redirect': '/admin/login'
    }), 403

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Logout admin"""
    token = request.cookies.get('admin_token')
    
    if FACE_AUTH_AVAILABLE and token:
        logout_session(token)
    
    response = jsonify({'success': True})
    response.set_cookie('admin_token', '', max_age=0)
    
    return response

@app.route('/api/admin/log-unauthorized', methods=['POST'])
def log_unauthorized_attempt():
    """Log unauthorized access attempt with photo, device info, and complete details"""
    try:
        from datetime import datetime
        import os
        import json as json_module
        
        # Get uploaded photo
        if 'unauthorized_face' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400
        
        photo = request.files['unauthorized_face']
        timestamp = request.form.get('timestamp', datetime.now().isoformat())
        device_info_str = request.form.get('device_info', '{}')
        
        try:
            device_info = json_module.loads(device_info_str)
        except:
            device_info = {}
        
        # Create unauthorized logs directory
        log_dir = 'data/unauthorized_attempts'
        os.makedirs(log_dir, exist_ok=True)
        
        # Save photo with timestamp
        filename = f"unauthorized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        photo_path = os.path.join(log_dir, filename)
        photo.save(photo_path)
        
        # Log to JSON file with complete details including device info
        log_file = os.path.join(log_dir, 'attempts_log.json')
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json_module.load(f)
        else:
            logs = []
        
        # Add complete log entry with device info
        log_entry = {
            'timestamp': timestamp,
            'photo': filename,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown'),
            'device_info': device_info,
            'total_attempts': 5,
            'status': 'BLOCKED',
            'severity': 'HIGH',
            'action_taken': 'Photo captured, device info logged, access denied, session terminated'
        }
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json_module.dump(logs, f, indent=2)
        
        print(f"[SECURITY] Unauthorized attempt logged: {filename}")
        print(f"[SECURITY] IP: {request.remote_addr}, Device: {device_info.get('platform', 'Unknown')}")
        
        return jsonify({
            'success': True,
            'message': 'Unauthorized attempt logged with complete details',
            'photo': filename,
            'details': log_entry
        })
        
    except Exception as e:
        print(f"[ERROR] Failed to log unauthorized attempt: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """Get scan statistics for admin dashboard - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if SCAN_LOGGER_AVAILABLE:
        stats = get_scan_stats()
        return jsonify(stats)
    return jsonify({'error': 'Scan logger not available'}), 500

@app.route('/api/admin/unauthorized-attempts', methods=['GET'])
def get_unauthorized_attempts():
    """Get unauthorized access attempts - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import json
        import os
        
        log_file = 'data/unauthorized_attempts/attempts_log.json'
        
        if not os.path.exists(log_file):
            return jsonify({'attempts': []})
        
        with open(log_file, 'r') as f:
            attempts = json.load(f)
        
        # Return most recent first
        attempts.reverse()
        
        return jsonify({'attempts': attempts})
        
    except Exception as e:
        print(f"[ERROR] Failed to get unauthorized attempts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/data/unauthorized_attempts/<filename>')
def serve_unauthorized_photo(filename):
    """Serve unauthorized attempt photos - requires auth"""
    token = request.cookies.get('admin_token') or request.args.get('token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return "Unauthorized", 401
    
    from flask import send_from_directory
    return send_from_directory('data/unauthorized_attempts', filename)

@app.route('/api/admin/history', methods=['GET'])
def admin_history():
    """Get scan history for admin dashboard - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if SCAN_LOGGER_AVAILABLE:
        limit = request.args.get('limit', 100, type=int)
        history = get_scan_history(limit)
        return jsonify(history)
    return jsonify({'error': 'Scan logger not available'}), 500

@app.route('/api/admin/clear-logs', methods=['POST'])
def clear_all_logs():
    """Clear all scan history logs - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Clear scan history JSON file
        scan_history_file = 'data/scan_history.json'
        if os.path.exists(scan_history_file):
            with open(scan_history_file, 'w') as f:
                import json
                json.dump([], f)
            return jsonify({'success': True, 'message': 'All logs cleared'})
        else:
            return jsonify({'success': True, 'message': 'No logs to clear'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/delete-logs', methods=['POST'])
def delete_selected_logs():
    """Delete selected scan logs by indices - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        indices = data.get('indices', [])
        
        if not indices:
            return jsonify({'error': 'No indices provided'}), 400
        
        scan_history_file = 'data/scan_history.json'
        if not os.path.exists(scan_history_file):
            return jsonify({'error': 'No scan history found'}), 404
        
        import json
        with open(scan_history_file, 'r') as f:
            history = json.load(f)
        
        # Sort indices in reverse to delete from end to start
        indices_sorted = sorted(set(indices), reverse=True)
        deleted_count = 0
        
        for idx in indices_sorted:
            if 0 <= idx < len(history):
                del history[idx]
                deleted_count += 1
        
        # Save updated history
        with open(scan_history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return jsonify({'success': True, 'deleted': deleted_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/delete-attempts', methods=['POST'])
def delete_unauthorized_attempts():
    """Delete selected unauthorized attempts - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'error': 'No filenames provided'}), 400
        
        deleted_count = 0
        attempts_dir = 'data/unauthorized_attempts'
        attempts_log_file = os.path.join(attempts_dir, 'attempts_log.json')
        
        # Delete image files
        for filename in filenames:
            file_path = os.path.join(attempts_dir, filename)
            if os.path.exists(file_path) and filename.endswith('.jpg'):
                os.remove(file_path)
                deleted_count += 1
        
        # Update attempts log JSON
        if os.path.exists(attempts_log_file):
            import json
            with open(attempts_log_file, 'r') as f:
                attempts = json.load(f)
            
            # Remove deleted attempts from log
            attempts = [a for a in attempts if a.get('photo') not in filenames]
            
            with open(attempts_log_file, 'w') as f:
                json.dump(attempts, f, indent=2)
        
        return jsonify({'success': True, 'deleted': deleted_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/clear-face-data', methods=['POST'])
def clear_face_data():
    """Clear all face registration data - requires auth"""
    token = request.cookies.get('admin_token')
    
    if not FACE_AUTH_AVAILABLE or not verify_session(token):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        import shutil
        
        # Delete face images
        face_dir = 'data/admin_faces'
        if os.path.exists(face_dir):
            shutil.rmtree(face_dir)
            os.makedirs(face_dir, exist_ok=True)
        
        # Delete face data JSON
        face_data_file = 'data/admin_face_data.json'
        if os.path.exists(face_data_file):
            os.remove(face_data_file)
        
        # Delete credentials
        cred_file = 'data/admin_credentials.json'
        if os.path.exists(cred_file):
            os.remove(cred_file)
        
        print("[ADMIN] Face data cleared for re-registration")
        return jsonify({'success': True, 'message': 'Face data cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️ Fraud Eye - Cyber Security for Villages")
    print("="*60)
    print("\n✅ Server starting...")
    print("🌐 Open in browser: http://localhost:5001")
    print("\n📝 Features available:")
    print("   - QR code scanner")
    print("   - Voice fraud detector")
    print("   - URL safety checker")
    print("   - Hindi language support")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
