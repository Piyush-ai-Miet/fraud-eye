#!/usr/bin/env python3
"""
Test face registration to debug issues
"""
import sys
import os

print("="*60)
print("🧪 Face Registration Test")
print("="*60)

# Test 1: Check if OpenCV is available
print("\n[TEST 1] Checking OpenCV...")
try:
    import cv2
    print(f"✅ OpenCV version: {cv2.__version__}")
except Exception as e:
    print(f"❌ OpenCV error: {e}")
    sys.exit(1)

# Test 2: Check face cascade
print("\n[TEST 2] Checking face cascade...")
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("✅ Face cascade loaded")
except Exception as e:
    print(f"❌ Face cascade error: {e}")
    sys.exit(1)

# Test 3: Check face_recognition_simple module
print("\n[TEST 3] Checking face_recognition_simple module...")
try:
    from face_recognition_simple import detect_face_opencv, register_admin_face_multi, get_registration_status
    print("✅ face_recognition_simple module loaded")
except Exception as e:
    print(f"❌ Module error: {e}")
    sys.exit(1)

# Test 4: Check registration status
print("\n[TEST 4] Checking registration status...")
try:
    status = get_registration_status()
    print(f"Registration status: {status}")
    if any(status.values()):
        print("⚠️ Some angles already registered!")
    else:
        print("✅ No angles registered yet (ready for fresh registration)")
except Exception as e:
    print(f"❌ Status check error: {e}")

# Test 5: Check admin_credentials module
print("\n[TEST 5] Checking admin_credentials module...")
try:
    from admin_credentials import is_face_registered
    is_registered = is_face_registered()
    print(f"Face registered flag: {is_registered}")
    if is_registered:
        print("⚠️ Admin already marked as registered!")
    else:
        print("✅ Admin not registered yet")
except Exception as e:
    print(f"❌ Credentials check error: {e}")

# Test 6: Check data directories
print("\n[TEST 6] Checking data directories...")
face_dir = 'data/admin_faces'
if os.path.exists(face_dir):
    files = os.listdir(face_dir)
    print(f"✅ Face directory exists")
    print(f"   Files: {files if files else 'Empty'}")
else:
    print(f"⚠️ Face directory doesn't exist (will be created)")

# Test 7: Test face detection with a dummy image
print("\n[TEST 7] Testing face detection...")
try:
    import numpy as np
    # Create a dummy image (black square)
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, img_encoded = cv2.imencode('.jpg', dummy_img)
    img_bytes = img_encoded.tobytes()
    
    success, face_img, message = detect_face_opencv(img_bytes)
    print(f"Detection result: {message}")
    if not success:
        print("⚠️ No face detected in dummy image (expected)")
    else:
        print("✅ Face detection working")
except Exception as e:
    print(f"❌ Detection test error: {e}")

print("\n" + "="*60)
print("📋 SUMMARY")
print("="*60)
print("\nIf all tests passed, face registration should work.")
print("If you're still having issues, please share:")
print("1. Browser console errors (F12 → Console tab)")
print("2. Network tab errors (F12 → Network tab)")
print("3. Any error messages shown on the page")
print("\nCommon issues:")
print("- Camera permission denied → Allow camera in browser")
print("- No face detected → Ensure good lighting and face visible")
print("- Network error → Check if server is running on port 5001")
print("="*60)
