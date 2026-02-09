import re
from urllib.parse import urlparse, parse_qs

class UPIFraudDetector:
    def __init__(self):
        # Suspicious VPA patterns
        self.suspicious_vpa_patterns = [
            r'\d{5,}@',  # Too many numbers
            r'(user|payment|customer|refund|kyc|verify)@',  # Generic names
            r'@(paytm|phonepe|gpay|googlepay)$',  # Direct to app (suspicious)
        ]
        
        # Legitimate UPI handles
        self.legitimate_handles = [
            'paytm', 'phonepe', 'ybl', 'okaxis', 'okhdfcbank', 
            'okicici', 'oksbi', 'ibl', 'axl', 'pnb'
        ]
        
        # Fraud keywords in transaction notes
        self.fraud_keywords = [
            'refund', 'kyc', 'update', 'verify', 'urgent', 'prize',
            'winner', 'claim', 'otp', 'pin', 'password', 'cvv',
            'suspended', 'blocked', 'confirm', 'activate'
        ]
    
    def is_upi_qr(self, qr_data):
        """Check if QR code is UPI format"""
        return qr_data.startswith('upi://pay')
    
    def parse_upi_qr(self, qr_data):
        """Parse UPI QR code parameters"""
        try:
            # Extract query parameters
            if '?' in qr_data:
                query_string = qr_data.split('?')[1]
                params = {}
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value
                return params
            return {}
        except:
            return {}
    
    def check_vpa_suspicious(self, vpa):
        """Check if VPA looks suspicious"""
        if not vpa:
            return True, "VPA missing"
        
        # Check for suspicious patterns
        for pattern in self.suspicious_vpa_patterns:
            if re.search(pattern, vpa.lower()):
                return True, f"Suspicious VPA pattern: {pattern}"
        
        # Check if handle is legitimate
        handle = vpa.split('@')[1] if '@' in vpa else ''
        if handle and not any(leg in handle for leg in self.legitimate_handles):
            return True, f"Unknown UPI handle: {handle}"
        
        return False, "VPA looks legitimate"
    
    def check_amount_suspicious(self, amount):
        """Check if amount is suspicious"""
        if not amount:
            return False, "No amount specified"
        
        try:
            amt = float(amount)
            
            # Very high amount
            if amt > 10000:
                return True, f"Very high amount: ₹{amt}"
            
            # Round numbers are suspicious in payment requests
            if amt % 1000 == 0 and amt >= 1000:
                return True, f"Round amount: ₹{amt} (suspicious)"
            
            return False, f"Amount: ₹{amt}"
        except:
            return True, "Invalid amount format"
    
    def check_transaction_note(self, note):
        """Check if transaction note contains fraud keywords"""
        if not note:
            return False, "No transaction note"
        
        note_lower = note.lower()
        found_keywords = [kw for kw in self.fraud_keywords if kw in note_lower]
        
        if found_keywords:
            return True, f"Fraud keywords: {', '.join(found_keywords)}"
        
        return False, "Transaction note looks normal"
    
    def check_merchant_code(self, mc):
        """Check if merchant code is present"""
        if not mc:
            return True, "No merchant code (suspicious for business)"
        return False, f"Merchant code present: {mc}"
    
    def detect_upi_fraud(self, qr_data):
        """Main UPI fraud detection function"""
        result = {
            'is_upi': False,
            'is_suspicious': False,
            'risk_score': 0,
            'warnings': [],
            'details': {}
        }
        
        # Check if UPI QR
        if not self.is_upi_qr(qr_data):
            return result
        
        result['is_upi'] = True
        
        # Parse UPI parameters
        params = self.parse_upi_qr(qr_data)
        result['details'] = params
        
        # Check VPA
        vpa = params.get('pa', '')
        is_sus, msg = self.check_vpa_suspicious(vpa)
        if is_sus:
            result['risk_score'] += 3
            result['warnings'].append(f"⚠️ {msg}")
        
        # Check amount
        amount = params.get('am', '')
        is_sus, msg = self.check_amount_suspicious(amount)
        if is_sus:
            result['risk_score'] += 2
            result['warnings'].append(f"💰 {msg}")
        
        # Check transaction note
        tn = params.get('tn', '')
        is_sus, msg = self.check_transaction_note(tn)
        if is_sus:
            result['risk_score'] += 3
            result['warnings'].append(f"📝 {msg}")
        
        # Check merchant code
        mc = params.get('mc', '')
        is_sus, msg = self.check_merchant_code(mc)
        if is_sus:
            result['risk_score'] += 1
            result['warnings'].append(f"🏪 {msg}")
        
        # Check payee name
        pn = params.get('pn', '')
        if not pn or len(pn) < 3:
            result['risk_score'] += 1
            result['warnings'].append("👤 Payee name missing or too short")
        
        # Final verdict
        if result['risk_score'] >= 5:
            result['is_suspicious'] = True
            result['verdict'] = {
                'risk': 'HIGH',
                'message_hi': f'🚨 KHATRE! Yeh UPI QR code FRAUD hai! Paisa mat bhejo!',
                'message_en': 'DANGER! This UPI QR code is FRAUDULENT! Do not send money!'
            }
        elif result['risk_score'] >= 3:
            result['is_suspicious'] = True
            result['verdict'] = {
                'risk': 'MEDIUM',
                'message_hi': f'⚠️ Savdhaan! Yeh UPI QR code suspicious hai. Dhyan se check karo.',
                'message_en': 'WARNING! This UPI QR code is suspicious. Check carefully.'
            }
        else:
            result['verdict'] = {
                'risk': 'LOW',
                'message_hi': f'✅ UPI QR code safe lag raha hai.',
                'message_en': 'UPI QR code appears safe.'
            }
        
        return result

upi_detector = UPIFraudDetector()
