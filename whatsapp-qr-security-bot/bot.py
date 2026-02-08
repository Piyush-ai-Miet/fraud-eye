from flask import Flask, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import io
import requests
import validators
import re
from gtts import gTTS
import os
from urllib.parse import urlparse
import torch
import torchaudio
import tempfile

app = Flask(__name__)

# Audio fraud detection model (lightweight check)
class AudioFraudDetector:
    """Simple audio fraud detection"""
    
    def __init__(self):
        self.suspicious_patterns = [
            'bank account', 'otp', 'password', 'pin', 'cvv',
            'urgent', 'immediately', 'suspended', 'blocked',
            'prize', 'lottery', 'winner', 'congratulations'
        ]
    
    def check_audio(self, audio_path):
        """Audio file check karo"""
        try:
            # Basic audio analysis
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # Simple checks
            duration = waveform.shape[1] / sample_rate
            
            # Very short or very long suspicious ho sakta hai
            if duration < 2 or duration > 120:
                return {
                    'is_suspicious': True,
                    'confidence': 0.6,
                    'reason': 'Audio duration suspicious hai'
                }
            
            # Audio quality check
            mean_amplitude = torch.mean(torch.abs(waveform)).item()
            
            if mean_amplitude < 0.01:
                return {
                    'is_suspicious': True,
                    'confidence': 0.7,
                    'reason': 'Audio quality bahut kharab hai - recorded lag raha hai'
                }
            
            return {
                'is_suspicious': False,
                'confidence': 0.5,
                'reason': 'Audio normal lag raha hai'
            }
            
        except Exception as e:
            return {
                'is_suspicious': False,
                'confidence': 0.3,
                'reason': f'Audio check nahi ho paya: {str(e)}'
            }

audio_detector = AudioFraudDetector()

class SimpleQRChecker:
    """Lightweight QR security checker for villagers"""
    
    def __init__(self):
        # Scam patterns - simple aur effective
        self.scam_keywords = [
            'verify', 'suspended', 'urgent', 'click now', 'confirm',
            'account blocked', 'prize', 'lottery', 'winner', 'claim',
            'free money', 'cash', 'reward', 'limited time'
        ]
        
        # Suspicious domains
        self.suspicious_domains = [
            '.tk', '.ml', '.ga', '.cf', '.gq',  # Free domains
            'bit.ly', 'tinyurl', 'goo.gl'  # URL shorteners
        ]
        
        # Safe domains (banks, govt)
        self.safe_domains = [
            'paytm.com', 'phonepe.com', 'googlepay.com', 'bhim.upi',
            'sbi.co.in', 'hdfcbank.com', 'icicibank.com',
            'gov.in', 'nic.in', 'india.gov.in'
        ]
    
    def scan_qr(self, image_url):
        """QR code scan karo"""
        try:
            # Image download karo
            response = requests.get(image_url, timeout=10)
            image = Image.open(io.BytesIO(response.content))
            image_np = np.array(image)
            
            # QR decode karo
            decoded = decode(image_np)
            
            if not decoded:
                return None, "QR code nahi mila image mein"
            
            qr_data = decoded[0].data.decode('utf-8')
            return qr_data, None
            
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def check_safety(self, content):
        """Simple safety check - no heavy ML"""
        risk_score = 0
        warnings = []
        
        # Check if URL hai
        if not validators.url(content):
            return {
                'is_safe': True,
                'risk': 'LOW',
                'message_hi': 'Yeh sirf text hai, koi link nahi hai.',
                'warnings': []
            }
        
        content_lower = content.lower()
        parsed = urlparse(content)
        domain = parsed.netloc.lower()
        
        # Check 1: Safe domain hai?
        for safe in self.safe_domains:
            if safe in domain:
                return {
                    'is_safe': True,
                    'risk': 'LOW',
                    'message_hi': f'Yeh {safe} ka official link hai. Safe hai.',
                    'warnings': []
                }
        
        # Check 2: HTTPS nahi hai?
        if parsed.scheme != 'https':
            risk_score += 30
            warnings.append('HTTPS nahi hai - secure nahi')
        
        # Check 3: IP address use kar raha hai?
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            risk_score += 50
            warnings.append('IP address use kar raha hai - bahut suspicious')
        
        # Check 4: Suspicious domain?
        for sus_domain in self.suspicious_domains:
            if sus_domain in domain:
                risk_score += 40
                warnings.append(f'Suspicious domain: {sus_domain}')
        
        # Check 5: Scam keywords?
        found_keywords = [kw for kw in self.scam_keywords if kw in content_lower]
        if found_keywords:
            risk_score += 20 * len(found_keywords)
            warnings.append(f'Scam keywords mile: {", ".join(found_keywords[:3])}')
        
        # Check 6: Bahut lamba domain?
        if len(domain) > 40:
            risk_score += 20
            warnings.append('Bahut lamba domain name - suspicious')
        
        # Final decision
        if risk_score >= 50:
            return {
                'is_safe': False,
                'risk': 'HIGH',
                'message_hi': '⚠️ DHYAN RAHE! Yeh link bahut dangerous lag raha hai. Is par click mat karo!',
                'warnings': warnings
            }
        elif risk_score >= 25:
            return {
                'is_safe': False,
                'risk': 'MEDIUM',
                'message_hi': '⚠️ Savdhaan! Yeh link thoda suspicious hai. Dhyan se check karo.',
                'warnings': warnings
            }
        else:
            return {
                'is_safe': True,
                'risk': 'LOW',
                'message_hi': '✅ Yeh link safe lag raha hai, lekin phir bhi dhyan rakho.',
                'warnings': warnings
            }

checker = SimpleQRChecker()

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """WhatsApp messages handle karo"""
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    num_media = int(request.values.get('NumMedia', 0))
    media_content_type = request.values.get('MediaContentType0', '')
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # Agar media bheja hai
    if num_media > 0:
        media_url = request.values.get('MediaUrl0', '')
        
        # Check karo - image hai ya audio?
        if 'image' in media_content_type:
            # QR CODE CHECK
            qr_content, error = checker.scan_qr(media_url)
            
            if error:
                msg.body(f"❌ {error}\n\nKripya ek clear QR code image bhejiye.")
                return str(resp)
            
            # Safety check karo
            result = checker.check_safety(qr_content)
            
            # Response banao
            response_text = f"📱 QR CODE REPORT\n\n"
            response_text += f"{result['message_hi']}\n\n"
            response_text += f"🔍 Link: {qr_content[:50]}...\n"
            response_text += f"📊 Risk: {result['risk']}\n\n"
            
            if result['warnings']:
                response_text += "⚠️ Warnings:\n"
                for warning in result['warnings'][:3]:
                    response_text += f"• {warning}\n"
            
            if not result['is_safe']:
                response_text += "\n🛡️ Suraksha Tips:\n"
                response_text += "• Unknown link par click mat karo\n"
                response_text += "• Personal details share mat karo\n"
                response_text += "• Bank se confirm karo\n"
            
            msg.body(response_text)
            
            # Hindi audio response
            try:
                audio_file = create_hindi_audio(result['message_hi'])
                if audio_file and os.path.exists(audio_file):
                    msg.media(audio_file)
            except:
                pass
        
        elif 'audio' in media_content_type or 'ogg' in media_content_type:
            # VOICE MESSAGE CHECK
            try:
                # Audio download karo
                audio_response = requests.get(media_url, timeout=10)
                
                # Temporary file mein save karo
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_audio:
                    temp_audio.write(audio_response.content)
                    temp_audio_path = temp_audio.name
                
                # Audio fraud check
                audio_result = audio_detector.check_audio(temp_audio_path)
                
                # Response banao
                response_text = f"🎤 VOICE MESSAGE REPORT\n\n"
                
                if audio_result['is_suspicious']:
                    response_text += f"⚠️ DHYAN RAHE!\n\n"
                    response_text += f"Yeh voice message suspicious lag raha hai.\n\n"
                    response_text += f"Reason: {audio_result['reason']}\n"
                    response_text += f"Confidence: {int(audio_result['confidence']*100)}%\n\n"
                    response_text += "🛡️ Suraksha Tips:\n"
                    response_text += "• Kisi ko bhi OTP/PIN mat batao\n"
                    response_text += "• Bank kabhi call karke password nahi mangta\n"
                    response_text += "• Urgent calls se savdhaan raho\n"
                else:
                    response_text += f"✅ Voice message normal lag raha hai.\n\n"
                    response_text += f"{audio_result['reason']}\n\n"
                    response_text += "Lekin phir bhi dhyan rakho!"
                
                msg.body(response_text)
                
                # Cleanup
                os.unlink(temp_audio_path)
                
            except Exception as e:
                msg.body(f"❌ Audio check nahi ho paya.\n\nError: {str(e)}")
        
        else:
            msg.body("❌ Sirf image (QR code) ya audio message bhejiye.")
    
    else:
        # Welcome message
        msg.body("🙏 Namaste!\n\n"
                "Main aapki cyber security mein madad karunga.\n\n"
                "📸 QR CODE CHECK:\n"
                "QR code ki photo bhejiye\n\n"
                "🎤 VOICE CHECK:\n"
                "Voice message bhejiye\n\n"
                "Main bataunga safe hai ya scam!")
    
    return str(resp)

def create_hindi_audio(text):
    """Hindi audio message banao (optional)"""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        audio_file = 'temp_audio.mp3'
        tts.save(audio_file)
        return audio_file
    except:
        return None

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/api/check-qr', methods=['POST'])
def api_check_qr():
    """Web interface ke liye API"""
    if 'qr_image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['qr_image']
    image_data = file.read()
    
    try:
        # QR scan
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)
        decoded = decode(image_np)
        
        if not decoded:
            return jsonify({'error': 'QR code nahi mila'}), 400
        
        qr_content = decoded[0].data.decode('utf-8')
        result = checker.check_safety(qr_content)
        result['content'] = qr_content
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-audio', methods=['POST'])
def api_check_audio():
    """Audio check API"""
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio provided'}), 400
    
    file = request.files['audio_file']
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            file.save(temp_audio.name)
            temp_audio_path = temp_audio.name
        
        result = audio_detector.check_audio(temp_audio_path)
        os.unlink(temp_audio_path)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
