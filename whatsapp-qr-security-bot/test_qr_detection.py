"""
Test QR detection with different preprocessing methods
"""
import cv2
import numpy as np
from PIL import Image
import sys

def test_opencv_qr_detection(image_path):
    """Test OpenCV QR detection with multiple methods"""
    print(f"\nTesting: {image_path}")
    print("-" * 60)
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            print("❌ Cannot read image")
            return None
        
        print(f"✅ Image loaded: {img.shape}")
        detector = cv2.QRCodeDetector()
        
        # Method 1: Original
        print("\n1. Original image...")
        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            print(f"   ✅ Detected: {data[:50]}...")
            return data
        print("   ❌ Not detected")
        
        # Method 2: Grayscale
        print("\n2. Grayscale...")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = detector.detectAndDecode(gray)
        if data:
            print(f"   ✅ Detected: {data[:50]}...")
            return data
        print("   ❌ Not detected")
        
        # Method 3: Binary threshold
        print("\n3. Binary threshold...")
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        data, bbox, _ = detector.detectAndDecode(thresh)
        if data:
            print(f"   ✅ Detected: {data[:50]}...")
            return data
        print("   ❌ Not detected")
        
        # Method 4: Adaptive threshold
        print("\n4. Adaptive threshold...")
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        data, bbox, _ = detector.detectAndDecode(adaptive)
        if data:
            print(f"   ✅ Detected: {data[:50]}...")
            return data
        print("   ❌ Not detected")
        
        # Method 5: Enhanced contrast
        print("\n5. Enhanced contrast...")
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        data, bbox, _ = detector.detectAndDecode(enhanced)
        if data:
            print(f"   ✅ Detected: {data[:50]}...")
            return data
        print("   ❌ Not detected")
        
        print("\n❌ QR code not detected with any method")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        result = test_opencv_qr_detection(image_path)
        if result:
            print("\n" + "=" * 60)
            print("✅ SUCCESS!")
            print(f"QR Content: {result}")
            print("=" * 60)
    else:
        print("Usage: python3 test_qr_detection.py <image_path>")
        print("\nExample:")
        print("  python3 test_qr_detection.py qr_code.png")
