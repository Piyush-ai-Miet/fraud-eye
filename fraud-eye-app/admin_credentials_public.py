"""
Admin Credentials Module - Public Version
For deployment without exposing personal credentials
"""
import os
import json

# Default admin credentials (CHANGE THESE!)
DEFAULT_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
DEFAULT_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

def verify_credentials(username, password):
    """
    Verify admin credentials
    In production, use environment variables or secure storage
    Returns: (verified: bool, message: str)
    """
    # Check environment variables first
    admin_user = os.getenv('ADMIN_USERNAME', DEFAULT_USERNAME)
    admin_pass = os.getenv('ADMIN_PASSWORD', DEFAULT_PASSWORD)
    
    if username == admin_user and password == admin_pass:
        return True, 'Credentials verified'
    else:
        return False, 'Invalid username or password'

def is_face_registered():
    """
    Check if admin face is registered
    Returns False for public deployment (face auth disabled)
    """
    return False

def mark_face_registered():
    """
    Mark face as registered
    No-op for public deployment
    """
    pass

# For compatibility with existing code
if __name__ == '__main__':
    print("Admin Credentials Module - Public Version")
    print("Set ADMIN_USERNAME and ADMIN_PASSWORD environment variables")
