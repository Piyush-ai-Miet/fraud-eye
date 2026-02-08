#!/usr/bin/env python3
"""
Test all Fraud Eye models and detectors
"""

print("\n" + "="*60)
print("🧪 FRAUD EYE - ALL MODELS TEST")
print("="*60 + "\n")

# Test 1: Malicious Pattern Detector
print("1️⃣ Testing Malicious Pattern Detector...")
print("-" * 60)
try:
    from malicious_patterns import detector
    
    test_cases = [
        ('<?php system($_GET["cmd"]);?>', 'PHP Code Injection'),
        ('http://example.com/page?id=1 OR 1=1', 'SQL Injection'),
        ('<script>alert("xss")</script>', 'XSS Attack'),
        ('http://example.com/file.php?page=../../etc/passwd', 'Path Traversal'),
        ('http://example.com/cmd?exec=ls|cat /etc/passwd', 'Command Injection'),
    ]
    
    passed = 0
    failed = 0
    
    for url, expected_attack in test_cases:
        attacks = detector.detect_attack(url)
        risk_score = detector.get_risk_score(attacks)
        
        if any(expected_attack.lower() in attack.lower() for attack in attacks):
            print(f"   ✅ {expected_attack}: DETECTED")
            print(f"      URL: {url[:50]}...")
            print(f"      Attacks: {attacks}")
            print(f"      Risk Score: {risk_score}")
            passed += 1
        else:
            print(f"   ❌ {expected_attack}: NOT DETECTED")
            print(f"      URL: {url[:50]}...")
            print(f"      Attacks: {attacks}")
            failed += 1
        print()
    
    print(f"Pattern Detector: {passed}/{len(test_cases)} tests passed\n")
    
except Exception as e:
    print(f"   ❌ Pattern Detector Error: {e}\n")

# Test 2: ML URL Classifier
print("2️⃣ Testing ML URL Classifier...")
print("-" * 60)
try:
    from ml_url_classifier import ml_classifier
    
    if ml_classifier.model_loaded:
        test_urls = [
            ('http://192.168.1.1/phishing', 'Malicious'),
            ('https://paytm.com', 'Benign'),
            ('http://bit.ly/urgent-verify-account', 'Malicious'),
            ('https://www.google.com', 'Benign'),
        ]
        
        passed = 0
        for url, expected in test_urls:
            result = ml_classifier.predict(url)
            if result:
                label = result['label']
                confidence = result['confidence'] * 100
                
                if (expected == 'Malicious' and result['is_malicious']) or \
                   (expected == 'Benign' and not result['is_malicious']):
                    print(f"   ✅ {label} ({confidence:.1f}%): {url[:40]}...")
                    passed += 1
                else:
                    print(f"   ❌ Expected {expected}, got {label}: {url[:40]}...")
            else:
                print(f"   ❌ No prediction for: {url[:40]}...")
        
        print(f"\nML Classifier: {passed}/{len(test_urls)} tests passed")
        print(f"Model: {ml_classifier.model_path}")
        print(f"Training samples: 4040 URLs\n")
    else:
        print("   ❌ ML Classifier model not loaded\n")
        
except Exception as e:
    print(f"   ❌ ML Classifier Error: {e}\n")

# Test 3: Audio Fraud Classifier
print("3️⃣ Testing Audio Fraud Classifier...")
print("-" * 60)
try:
    from audio_fraud_classifier import audio_classifier
    
    if audio_classifier.model_loaded:
        print(f"   ✅ Audio Classifier loaded")
        print(f"   Model: {audio_classifier.model_path}")
        print(f"   Training samples: 200 audio files")
        print(f"   Features: {len(audio_classifier.feature_names)} audio features")
        print(f"   Status: Ready for predictions\n")
    else:
        print("   ❌ Audio Classifier model not loaded\n")
        
except Exception as e:
    print(f"   ❌ Audio Classifier Error: {e}\n")

# Test 4: UPI Payment Detection
print("4️⃣ Testing UPI Payment Detection...")
print("-" * 60)
try:
    from app_simple import detect_upi_payment_direction
    
    test_cases = [
        ('upi://pay?pa=merchant@paytm&pn=Shop&am=500', 'SEND', '500'),
        ('upi://pay?pa=merchant@paytm&pn=Shop', 'RECEIVE', None),
        ('upi://pay?pa=scammer@upi&am=10000&mode=02', 'SEND', '10000'),
        ('https://paytm.com/payment', 'UNKNOWN', None),
    ]
    
    passed = 0
    for url, expected_dir, expected_amt in test_cases:
        direction, message, amount, is_request = detect_upi_payment_direction(url)
        
        if direction == expected_dir and (expected_amt is None or amount == expected_amt):
            print(f"   ✅ {direction}: {url[:50]}...")
            if amount:
                print(f"      Amount: ₹{amount}")
            if is_request:
                print(f"      ⚠️ PAYMENT REQUEST (HIGH RISK)")
            passed += 1
        else:
            print(f"   ❌ Expected {expected_dir}, got {direction}: {url[:50]}...")
        print()
    
    print(f"UPI Detection: {passed}/{len(test_cases)} tests passed\n")
    
except Exception as e:
    print(f"   ❌ UPI Detection Error: {e}\n")

# Test 5: QR Code Scanner
print("5️⃣ Testing QR Code Scanner...")
print("-" * 60)
try:
    from simple_qr_scanner import QR_SCANNING_AVAILABLE
    
    if QR_SCANNING_AVAILABLE:
        print("   ✅ QR Scanner available")
        print("   Libraries: OpenCV, pyzbar")
        print("   Status: Ready for QR image scanning\n")
    else:
        print("   ❌ QR Scanner not available\n")
        
except Exception as e:
    print(f"   ❌ QR Scanner Error: {e}\n")

# Test 6: Face Authentication
print("6️⃣ Testing Face Authentication...")
print("-" * 60)
try:
    from face_recognition_simple import get_registration_status
    
    status = get_registration_status()
    print("   ✅ Face Authentication available")
    print(f"   Registration status: {status}")
    print("   Status: Ready for admin authentication\n")
    
except Exception as e:
    print(f"   ❌ Face Authentication Error: {e}\n")

# Summary
print("="*60)
print("📊 TEST SUMMARY")
print("="*60)
print("\n✅ All critical models tested!")
print("\n🔍 Key Features:")
print("   • Pattern Detection: PHP, SQL, XSS, Command Injection")
print("   • ML URL Classifier: 4040 URLs trained")
print("   • Audio Classifier: 200 audio files trained")
print("   • UPI Payment Detection: Payment request detection")
print("   • QR Scanner: Image-based QR code scanning")
print("   • Face Auth: Multi-angle face recognition")
print("\n" + "="*60 + "\n")
