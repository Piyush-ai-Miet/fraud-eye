"""
Local testing script - WhatsApp ke bina test karo
"""

from bot import SimpleQRChecker, AudioFraudDetector

def test_qr_checker():
    print("=" * 50)
    print("QR CODE SECURITY CHECKER TEST")
    print("=" * 50)
    
    checker = SimpleQRChecker()
    
    # Test cases
    test_urls = [
        "https://paytm.com/payment",  # Safe
        "http://192.168.1.1/verify",  # Dangerous
        "https://bit.ly/urgent-verify",  # Suspicious
        "https://www.sbi.co.in/login",  # Safe bank
        "http://free-prize.tk/claim",  # Scam
    ]
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        result = checker.check_safety(url)
        print(f"   Risk: {result['risk']}")
        print(f"   Safe: {result['is_safe']}")
        print(f"   Message: {result['message_hi']}")
        if result['warnings']:
            print(f"   Warnings: {', '.join(result['warnings'][:2])}")
        print("-" * 50)

def test_audio_detector():
    print("\n" + "=" * 50)
    print("AUDIO FRAUD DETECTOR TEST")
    print("=" * 50)
    
    detector = AudioFraudDetector()
    
    print("\n✅ Audio detector initialized successfully!")
    print("   Note: Actual audio testing requires audio files")
    print("   Upload audio through web interface or WhatsApp bot")

if __name__ == "__main__":
    print("\n🚀 Starting Local Tests...\n")
    
    test_qr_checker()
    test_audio_detector()
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 50)
    print("\n📱 Next Steps:")
    print("1. Run: python bot.py")
    print("2. Open: http://localhost:5000")
    print("3. Test QR codes and audio files!")
    print("\n")
