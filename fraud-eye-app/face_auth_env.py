"""
Face Authentication using Environment Variables
Stores face encodings in env vars instead of files (GitHub safe)
"""
import os
import json
import base64
import numpy as np
import cv2

def encode_face_to_env(image_data):
    """
    Extract face encoding from image and convert to base64 string
    Returns: base64 encoded face data
    """
    try:
        # Convert image data to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize to standard size (100x100)
        resized = cv2.resize(gray, (100, 100))
        
        # Flatten and convert to base64
        flat = resized.flatten()
        encoded = base64.b64encode(flat.tobytes()).decode('utf-8')
        
        return encoded
        
    except Exception as e:
        print(f"[FACE] Encoding error: {e}")
        return None

def decode_face_from_env(encoded_str):
    """
    Decode base64 face data back to numpy array
    """
    try:
        decoded = base64.b64decode(encoded_str)
        face_array = np.frombuffer(decoded, dtype=np.uint8)
        face_img = face_array.reshape(100, 100)
        return face_img
    except Exception as e:
        print(f"[FACE] Decoding error: {e}")
        return None

def register_face_to_env(image_data, angle='center'):
    """
    Register face by storing encoding in environment variable
    AND save to .env file for persistence
    Angle: center, left, right, up
    """
    try:
        # Encode face
        encoded = encode_face_to_env(image_data)
        if not encoded:
            return False, "Failed to encode face"
        
        # Store in environment variable (for current session)
        env_key = f'ADMIN_FACE_{angle.upper()}'
        os.environ[env_key] = encoded
        
        # Save to .env file for persistence
        env_file = '.env'
        env_lines = []
        key_exists = False
        
        # Read existing .env file
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add the key
        updated_lines = []
        for line in env_lines:
            if line.startswith(f'{env_key}='):
                updated_lines.append(f'{env_key}={encoded}\n')
                key_exists = True
            else:
                updated_lines.append(line)
        
        # Add new key if not exists
        if not key_exists:
            updated_lines.append(f'{env_key}={encoded}\n')
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"[FACE] ✅ Registered face angle: {angle}")
        print(f"[FACE] ✅ Saved to .env file: {env_key}")
        print(f"[FACE] 📋 For Render, add: {env_key}={encoded[:50]}...")
        
        return True, f"Face angle '{angle}' registered and saved to .env"
        
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def verify_face_from_env(image_data):
    """
    Verify face against stored encodings in environment variables
    Returns: (verified, message, similarity)
    """
    try:
        # Encode current face
        current_encoded = encode_face_to_env(image_data)
        if not current_encoded:
            return False, "Failed to encode face", 0.0
        
        current_face = decode_face_from_env(current_encoded)
        
        # Check against all registered angles
        angles = ['CENTER', 'LEFT', 'RIGHT', 'UP']
        best_match = 0
        
        for angle in angles:
            env_key = f'ADMIN_FACE_{angle}'
            stored_encoded = os.getenv(env_key)
            
            if not stored_encoded:
                continue
            
            stored_face = decode_face_from_env(stored_encoded)
            if stored_face is None:
                continue
            
            # Calculate similarity (MSE - lower is better)
            mse = np.mean((current_face - stored_face) ** 2)
            similarity = 1 / (1 + mse)  # Convert to 0-1 scale
            
            if similarity > best_match:
                best_match = similarity
        
        # Threshold: 0.7 = 70% match required
        if best_match > 0.7:
            return True, f"Face verified (confidence: {best_match*100:.1f}%)", best_match * 100
        else:
            return False, f"Face not recognized (confidence: {best_match*100:.1f}%)", best_match * 100
            
    except Exception as e:
        return False, f"Verification failed: {str(e)}", 0.0

def is_face_registered_env():
    """
    Check if at least center face is registered
    """
    return os.getenv('ADMIN_FACE_CENTER') is not None

def get_registration_status_env():
    """
    Get registration status for all angles
    """
    return {
        'center': os.getenv('ADMIN_FACE_CENTER') is not None,
        'left': os.getenv('ADMIN_FACE_LEFT') is not None,
        'right': os.getenv('ADMIN_FACE_RIGHT') is not None,
        'up': os.getenv('ADMIN_FACE_UP') is not None
    }

def mark_face_registered_env():
    """
    Mark face as registered (set flag in env)
    """
    os.environ['ADMIN_FACE_REGISTERED'] = 'true'
    print("[FACE] Face registration complete!")

# For compatibility
register_admin_face_multi = register_face_to_env
verify_face = verify_face_from_env
is_face_registered = is_face_registered_env
get_registration_status = get_registration_status_env
mark_face_registered = mark_face_registered_env


def get_render_env_vars():
    """
    Get all face environment variables for Render deployment
    Returns: dict of env vars
    """
    env_vars = {}
    angles = ['CENTER', 'LEFT', 'RIGHT', 'UP']
    
    for angle in angles:
        env_key = f'ADMIN_FACE_{angle}'
        value = os.getenv(env_key)
        if value:
            env_vars[env_key] = value
    
    return env_vars

def print_render_instructions():
    """
    Print instructions for adding face data to Render
    """
    env_vars = get_render_env_vars()
    
    if not env_vars:
        print("\n⚠️ No face data registered yet")
        return
    
    print("\n" + "="*70)
    print("📋 RENDER ENVIRONMENT VARIABLES")
    print("="*70)
    print("\nCopy these to Render Dashboard → Environment:")
    print()
    
    for key, value in env_vars.items():
        print(f"Variable Name: {key}")
        print(f"Value: {value}")
        print()
    
    print("="*70)
    print("✅ After adding these, your face auth will work on Render!")
    print("="*70 + "\n")
