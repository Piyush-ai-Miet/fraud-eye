"""
Face Recognition using Face++ API
Free tier: 1000 calls/month
Sign up: https://www.faceplusplus.com/
"""
import requests
import base64
import json
import os

# Face++ API credentials (get from https://console.faceplusplus.com/)
FACE_API_KEY = os.getenv('FACE_API_KEY', 'YOUR_API_KEY_HERE')
FACE_API_SECRET = os.getenv('FACE_API_SECRET', 'YOUR_API_SECRET_HERE')
FACE_API_URL = 'https://api-us.faceplusplus.com/facepp/v3'

ADMIN_FACE_TOKEN_FILE = 'data/admin_face_token.json'

def detect_face(image_data):
    """
    Detect face in image using Face++ API
    Returns: face_token if face detected, None otherwise
    """
    try:
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Call Face++ detect API
        response = requests.post(
            f'{FACE_API_URL}/detect',
            data={
                'api_key': FACE_API_KEY,
                'api_secret': FACE_API_SECRET,
                'image_base64': image_base64,
                'return_attributes': 'gender,age'
            },
            timeout=10
        )
        
        result = response.json()
        
        if 'faces' in result and len(result['faces']) > 0:
            face_token = result['faces'][0]['face_token']
            return True, face_token, "Face detected"
        else:
            return False, None, "No face detected"
            
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def register_admin_face(image_data):
    """
    Register admin face for first time
    Stores face_token for future comparisons
    """
    success, face_token, message = detect_face(image_data)
    
    if not success:
        return False, message
    
    # Store admin face token
    os.makedirs('data', exist_ok=True)
    with open(ADMIN_FACE_TOKEN_FILE, 'w') as f:
        json.dump({
            'face_token': face_token,
            'registered_at': '2026-02-06'
        }, f, indent=2)
    
    return True, "Admin face registered successfully"

def verify_face(image_data):
    """
    Verify face against registered admin face
    Uses Face++ compare API
    """
    # Check if admin face is registered
    if not os.path.exists(ADMIN_FACE_TOKEN_FILE):
        return False, "Admin face not registered. Please register first."
    
    # Load admin face token
    with open(ADMIN_FACE_TOKEN_FILE, 'r') as f:
        admin_data = json.load(f)
    admin_face_token = admin_data['face_token']
    
    # Detect face in current image
    success, current_face_token, message = detect_face(image_data)
    
    if not success:
        return False, message
    
    try:
        # Compare faces using Face++ API
        response = requests.post(
            f'{FACE_API_URL}/compare',
            data={
                'api_key': FACE_API_KEY,
                'api_secret': FACE_API_SECRET,
                'face_token1': admin_face_token,
                'face_token2': current_face_token
            },
            timeout=10
        )
        
        result = response.json()
        
        if 'confidence' in result:
            confidence = result['confidence']
            threshold = result.get('thresholds', {}).get('1e-5', 70)
            
            # Face matched if confidence > threshold
            if confidence > threshold:
                return True, f"Face matched! Confidence: {confidence:.1f}%"
            else:
                return False, f"Face not matched. Confidence: {confidence:.1f}%"
        else:
            return False, "Face comparison failed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_api_configured():
    """Check if Face++ API is configured"""
    if FACE_API_KEY == 'YOUR_API_KEY_HERE' or FACE_API_SECRET == 'YOUR_API_SECRET_HERE':
        return False
    return True

if __name__ == "__main__":
    print("Face++ API Configuration")
    print("=" * 50)
    
    if check_api_configured():
        print("✅ API configured")
    else:
        print("❌ API not configured")
        print("\n📝 Steps to configure:")
        print("1. Sign up at: https://www.faceplusplus.com/")
        print("2. Get API Key and Secret from console")
        print("3. Set environment variables:")
        print("   export FACE_API_KEY='your_key'")
        print("   export FACE_API_SECRET='your_secret'")
        print("\nOr update face_recognition_api.py directly")
