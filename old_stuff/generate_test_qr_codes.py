#!/usr/bin/env python3
"""
Generate Test QR Codes for Payment Request Detection
"""

import qrcode
import os

# Create test_qr_codes directory
os.makedirs('test_qr_codes', exist_ok=True)

# Test QR Codes
test_qr_codes = [
    {
        'name': '1_payment_request_5000',
        'url': 'upi://pay?pa=scammer@phonepe&pn=FakeScammer&am=5000&cu=INR',
        'description': '🚨 PAYMENT REQUEST - ₹5000 (HIGH RISK)'
    },
    {
        'name': '2_payment_request_500',
        'url': 'upi://pay?pa=fraudster@paytm&pn=Fraudster&am=500&cu=INR&mode=02',
        'description': '🚨 PAYMENT REQUEST - ₹500 (HIGH RISK)'
    },
    {
        'name': '3_payment_request_no_amount',
        'url': 'upi://pay?pa=scam@phonepe&pn=ScamArtist&cu=INR&mode=02&purpose=00',
        'description': '🚨 PAYMENT REQUEST - No amount specified (HIGH RISK)'
    },
    {
        'name': '4_normal_receive_qr',
        'url': 'upi://pay?pa=myshop@paytm&pn=MyShop',
        'description': '✅ NORMAL RECEIVE QR - Safe for collecting payments (LOW RISK)'
    },
    {
        'name': '5_legitimate_merchant',
        'url': 'upi://pay?pa=merchant123@paytm&pn=LegitimateShop&cu=INR',
        'description': '✅ LEGITIMATE MERCHANT - Safe (LOW RISK)'
    },
    {
        'name': '6_phishing_url',
        'url': 'http://192.168.1.1/verify-kyc?otp=123',
        'description': '🚨 PHISHING URL - IP address, suspicious (HIGH RISK)'
    },
    {
        'name': '7_payment_request_10000',
        'url': 'upi://pay?pa=bigscam@phonepe&pn=BigScammer&am=10000&cu=INR&orgid=123456',
        'description': '🚨 PAYMENT REQUEST - ₹10,000 (HIGH RISK)'
    },
    {
        'name': '8_safe_paytm_url',
        'url': 'https://paytm.com/payment',
        'description': '✅ SAFE URL - Official Paytm (LOW RISK)'
    }
]

print("\n" + "="*60)
print("🎨 Generating Test QR Codes")
print("="*60 + "\n")

for qr_data in test_qr_codes:
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data['url'])
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    filename = f"test_qr_codes/{qr_data['name']}.png"
    img.save(filename)
    
    print(f"✅ Generated: {qr_data['name']}.png")
    print(f"   URL: {qr_data['url'][:60]}...")
    print(f"   Description: {qr_data['description']}")
    print()

print("="*60)
print(f"📁 All QR codes saved in: test_qr_codes/")
print("="*60)
print("\n🧪 Testing Instructions:")
print("1. Start server: python3 app_simple.py")
print("2. Open: http://localhost:5001/scanner")
print("3. Upload QR codes from test_qr_codes/ folder")
print("4. Check if payment requests are detected as HIGH RISK")
print("\n" + "="*60 + "\n")
