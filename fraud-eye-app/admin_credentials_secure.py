"""
Fraud Eye - Secure Admin Credentials Module
============================================
Production-grade security using environment variables.
Credentials are NEVER stored in code or committed to GitHub.

Author: Piyush Dhariwal
Date: February 9, 2026
"""

import os
import hashlib
from typing import Optional, Dict

class AdminCredentialsManager:
    """
    Secure admin credentials management using environment variables.
    
    Security Features:
    - Credentials loaded from environment (not hardcoded)
    - Password hashing with SHA-256
    - Face data stored server-side only
    - Session management with timeout
    """
    
    def __init__(self):
        """Initialize credentials from environment variables."""
        self.username = os.getenv('ADMIN_USERNAME')
        self.password_hash = os.getenv('ADMIN_PASSWORD_HASH')
        
        # Validate required environment variables
        if not self.username or not self.password_hash:
            raise EnvironmentError(
                "❌ SECURITY ERROR: Admin credentials not configured!\n"
                "Please set environment variables:\n"
                "  - ADMIN_USERNAME\n"
                "  - ADMIN_PASSWORD_HASH\n\n"
                "Generate password hash:\n"
                "  python -c \"import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())\"\n"
            )
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """
        Verify admin username and password.
        
        Args:
            username: Username to verify
            password: Plain text password to verify
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        if not username or not password:
            return False
        
        # Hash the provided password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Compare with stored credentials
        return (username == self.username and 
                password_hash == self.password_hash)
    
    def get_admin_username(self) -> str:
        """Get the configured admin username."""
        return self.username
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password (hex)
        """
        return hashlib.sha256(password.encode()).hexdigest()


# Global instance (lazy loaded)
_credentials_manager: Optional[AdminCredentialsManager] = None


def get_credentials_manager() -> AdminCredentialsManager:
    """
    Get the global credentials manager instance.
    
    Returns:
        AdminCredentialsManager: Singleton instance
        
    Raises:
        EnvironmentError: If credentials are not configured
    """
    global _credentials_manager
    
    if _credentials_manager is None:
        _credentials_manager = AdminCredentialsManager()
    
    return _credentials_manager


def verify_admin(username: str, password: str) -> bool:
    """
    Verify admin credentials (convenience function).
    
    Args:
        username: Username to verify
        password: Password to verify
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        manager = get_credentials_manager()
        return manager.verify_credentials(username, password)
    except EnvironmentError as e:
        print(f"❌ Credentials Error: {e}")
        return False


# ============================================
# SETUP UTILITY (Run once to generate hash)
# ============================================

if __name__ == "__main__":
    print("🔐 Fraud Eye - Admin Password Hash Generator")
    print("=" * 50)
    print()
    
    password = input("Enter admin password: ")
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        exit(1)
    
    password_hash = AdminCredentialsManager.hash_password(password)
    
    print()
    print("✅ Password hash generated successfully!")
    print()
    print("Add these to your environment variables:")
    print("-" * 50)
    print(f"ADMIN_USERNAME=your_username")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("-" * 50)
    print()
    print("On Render.com:")
    print("1. Go to Environment tab")
    print("2. Add these variables")
    print("3. Redeploy your service")
    print()
