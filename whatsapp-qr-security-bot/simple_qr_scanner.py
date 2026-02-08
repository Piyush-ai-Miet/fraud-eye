"""
QR Code Scanner using pyzbar, OpenCV, and Pillow
"""
from PIL import Image
import tempfile
import os
import numpy as np

# Try pyzbar first (needs zbar library)
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

# Try OpenCV QR detector as fallback
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

def decode_qr_with_pyzbar(image_path):
    """Decode using pyzbar"""
    try:
        img = Image.open(image_path)
        decoded_objects = pyzbar_decode(img)
        
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        return None
    except Exception as e:
        print(f"pyzbar error: {e}")
        return None

def decode_qr_with_opencv(image_path):
    """Decode using OpenCV QRCodeDetector with preprocessing"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"[OpenCV] Cannot read image: {image_path}")
            return None
        
        print(f"[OpenCV] Image loaded: {img.shape}")
        detector = cv2.QRCodeDetector()
        
        # Try 1: Original image
        data, bbox, _ = detector.detectAndDecode(img)
        if data:
            print(f"[OpenCV] ✅ Detected (original): {data[:50]}")
            return data
        
        # Try 2: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = detector.detectAndDecode(gray)
        if data:
            print(f"[OpenCV] ✅ Detected (grayscale): {data[:50]}")
            return data
        
        # Try 3: Apply thresholding
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        data, bbox, _ = detector.detectAndDecode(thresh)
        if data:
            print(f"[OpenCV] ✅ Detected (threshold): {data[:50]}")
            return data
        
        # Try 4: Adaptive thresholding
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        data, bbox, _ = detector.detectAndDecode(adaptive)
        if data:
            print(f"[OpenCV] ✅ Detected (adaptive): {data[:50]}")
            return data
        
        # Try 5: Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        data, bbox, _ = detector.detectAndDecode(enhanced)
        if data:
            print(f"[OpenCV] ✅ Detected (enhanced): {data[:50]}")
            return data
        
        print("[OpenCV] ❌ QR not detected with any method")
        return None
    except Exception as e:
        print(f"[OpenCV] Error: {e}")
        return None

def decode_qr_image(image_path):
    """
    Decode QR code from image file
    Tries multiple methods
    """
    # Try pyzbar first (most reliable)
    if PYZBAR_AVAILABLE:
        result = decode_qr_with_pyzbar(image_path)
        if result:
            return result
    
    # Fallback to OpenCV
    if OPENCV_AVAILABLE:
        result = decode_qr_with_opencv(image_path)
        if result:
            return result
    
    return None

def scan_qr_from_upload(image_file):
    """
    Scan QR code from uploaded file
    """
    if not PYZBAR_AVAILABLE and not OPENCV_AVAILABLE:
        return None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            image_file.save(tmp.name)
            file_path = tmp.name
        
        result = decode_qr_image(file_path)
        os.unlink(file_path)
        
        return result
        
    except Exception as e:
        print(f"Scan error: {e}")
        return None

# Export availability status
PYZBAR_AVAILABLE = PYZBAR_AVAILABLE
OPENCV_AVAILABLE = OPENCV_AVAILABLE
QR_SCANNING_AVAILABLE = PYZBAR_AVAILABLE or OPENCV_AVAILABLE
