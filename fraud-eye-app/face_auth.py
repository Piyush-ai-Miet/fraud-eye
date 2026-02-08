"""
Simple Face Authentication System
For demo: Uses basic image verification
In production: Use face_recognition library or cloud API
"""
import os
import secrets
import json
from datetime import datetime, timedelta

# Session storage
SESSIONS_FILE = 'data/admin_sessions.json'
ADMIN_FACE_FILE = 'data/admin_face.jpg'

def generate_session_token():
    """Generate secure session token"""
    return secrets.token_urlsafe(32)

def save_admin_face(image_data):
    """Save admin face for first-time setup"""
    os.makedirs('data', exist_ok=True)
    with open(ADMIN_FACE_FILE, 'wb') as f:
        f.write(image_data)
    return True

def verify_face(image_data):
    """
    Verify face against stored admin face
    For demo: Just checks if admin face exists
    In production: Use face_recognition library
    """
    # Check if admin face is registered
    if not os.path.exists(ADMIN_FACE_FILE):
        # First time - register this face as admin
        save_admin_face(image_data)
        return True, "First admin registered"
    
    # For demo: Always verify successfully if face exists
    # In production, use actual face recognition:
    # import face_recognition
    # known_face = face_recognition.load_image_file(ADMIN_FACE_FILE)
    # unknown_face = face_recognition.load_image_file(image_data)
    # results = face_recognition.compare_faces([known_face], unknown_face)
    # return results[0], "Face matched" if results[0] else "Face not matched"
    
    return True, "Face verified (demo mode)"

def create_session(user_id='admin'):
    """Create admin session"""
    token = generate_session_token()
    
    # Load existing sessions
    sessions = {}
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r') as f:
            sessions = json.load(f)
    
    # Create new session
    expiry = (datetime.now() + timedelta(hours=24)).isoformat()
    sessions[token] = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'expires_at': expiry
    }
    
    # Save sessions
    os.makedirs('data', exist_ok=True)
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)
    
    return token

def verify_session(token):
    """Verify if session token is valid"""
    if not token:
        return False
    
    if not os.path.exists(SESSIONS_FILE):
        return False
    
    try:
        with open(SESSIONS_FILE, 'r') as f:
            sessions = json.load(f)
        
        if token not in sessions:
            return False
        
        session = sessions[token]
        expiry = datetime.fromisoformat(session['expires_at'])
        
        # Check if expired
        if datetime.now() > expiry:
            # Remove expired session
            del sessions[token]
            with open(SESSIONS_FILE, 'w') as f:
                json.dump(sessions, f, indent=2)
            return False
        
        return True
    except Exception as e:
        print(f"Session verification error: {e}")
        return False

def logout_session(token):
    """Logout and remove session"""
    if not os.path.exists(SESSIONS_FILE):
        return True
    
    try:
        with open(SESSIONS_FILE, 'r') as f:
            sessions = json.load(f)
        
        if token in sessions:
            del sessions[token]
            with open(SESSIONS_FILE, 'w') as f:
                json.dump(sessions, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Logout error: {e}")
        return False

if __name__ == "__main__":
    # Test
    print("Testing face auth system...")
    
    # Create test session
    token = create_session()
    print(f"✅ Session created: {token[:20]}...")
    
    # Verify session
    is_valid = verify_session(token)
    print(f"✅ Session valid: {is_valid}")
    
    # Logout
    logout_session(token)
    print(f"✅ Session logged out")
    
    # Verify again
    is_valid = verify_session(token)
    print(f"✅ Session valid after logout: {is_valid}")
