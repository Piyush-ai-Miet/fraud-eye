"""
Test QR code scanner
"""
import sys

print("Testing QR scanner...")
print("-" * 50)

# Test 1: Check if pyzbar is available
try:
    from pyzbar.pyzbar import decode
    print("✅ pyzbar imported successfully")
    PYZBAR_OK = True
except ImportError as e:
    print(f"❌ pyzbar import failed: {e}")
    PYZBAR_OK = False

# Test 2: Check if OpenCV is available
try:
    import cv2
    print("✅ OpenCV imported successfully")
    print(f"   OpenCV version: {cv2.__version__}")
    OPENCV_OK = True
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")
    OPENCV_OK = False

# Test 3: Check if simple_qr_scanner works
try:
    from simple_qr_scanner import scan_qr_from_upload, QR_SCANNING_AVAILABLE, PYZBAR_AVAILABLE, OPENCV_AVAILABLE
    print(f"✅ simple_qr_scanner imported")
    print(f"   PYZBAR_AVAILABLE: {PYZBAR_AVAILABLE}")
    print(f"   OPENCV_AVAILABLE: {OPENCV_AVAILABLE}")
    print(f"   QR_SCANNING_AVAILABLE: {QR_SCANNING_AVAILABLE}")
except ImportError as e:
    print(f"❌ simple_qr_scanner import failed: {e}")

# Test 4: Check if Pillow works
try:
    from PIL import Image
    print("✅ Pillow imported successfully")
except ImportError as e:
    print(f"❌ Pillow import failed: {e}")

print("-" * 50)

if PYZBAR_OK or OPENCV_OK:
    print("\n✅ QR scanning is ready!")
    if OPENCV_OK:
        print("   Using OpenCV QRCodeDetector")
    if PYZBAR_OK:
        print("   Using pyzbar (preferred)")
    print("\nYou can now upload QR code images to the web interface.")
else:
    print("\n⏳ Waiting for zbar installation to complete...")
    print("Run: brew install zbar")
    print("Then restart the Flask server.")

print("\nTo test the server:")
print("1. python3 app_simple.py")
print("2. Open http://localhost:5001")
print("3. Upload a QR code image")
