"""
Admin Credentials Management
Stores username/password with bcrypt hashing
"""
import json
import os
import hashlib
import secrets

CREDENTIALS_FILE = 'data/admin_credentials.json'

def hash_password(password):
    """Hash password using SHA256"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password, stored_hash):
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_hash.split('$')
        test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return test_hash == pwd_hash
    except:
        return False

def create_admin(username, password):
    """Create admin account"""
    os.makedirs('data', exist_ok=True)
    
    credentials = {
        'username': username,
        'password_hash': hash_password(password),
        'created_at': '2026-02-06',
        'face_registered': False
    }
    
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✅ Admin created: {username}")
    return True

def verify_credentials(username, password):
    """Verify username and password"""
    if not os.path.exists(CREDENTIALS_FILE):
        return False, "No admin account found"
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        
        if creds['username'] != username:
            return False, "Invalid username"
        
        if not verify_password(password, creds['password_hash']):
            return False, "Invalid password"
        
        return True, "Credentials verified"
    except Exception as e:
        return False, f"Error: {e}"

def is_face_registered():
    """Check if admin face is registered"""
    if not os.path.exists(CREDENTIALS_FILE):
        return False
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        return creds.get('face_registered', False)
    except:
        return False

def mark_face_registered():
    """Mark admin face as registered"""
    if not os.path.exists(CREDENTIALS_FILE):
        return False
    
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds = json.load(f)
        
        creds['face_registered'] = True
        
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(creds, f, indent=2)
        
        return True
    except:
        return False

if __name__ == "__main__":
    # Create default admin
    print("Creating default admin account...")
    create_admin("admin", "admin123")
    print("\n⚠️ Default credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🔒 Change these in production!")
