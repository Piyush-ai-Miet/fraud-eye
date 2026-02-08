"""
Scan History Logger for Admin Dashboard
Logs all QR, URL, and Voice scans
"""
import json
import os
from datetime import datetime

HISTORY_FILE = 'data/scan_history.json'

def log_scan(scan_type, content, result, user_ip='unknown'):
    """Log a scan to history"""
    try:
        # Load existing history
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {'scans': []}
        
        # Create scan entry
        scan_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': scan_type,  # 'qr', 'url', 'voice'
            'content': content[:100] if content else 'N/A',  # Truncate long content
            'is_safe': result.get('is_safe', True),
            'risk': result.get('risk', 'UNKNOWN'),
            'user_ip': user_ip,
            'warnings_count': len(result.get('warnings', []))
        }
        
        # Add to history (keep last 1000 scans)
        history['scans'].insert(0, scan_entry)
        history['scans'] = history['scans'][:1000]
        
        # Save history
        os.makedirs('data', exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error logging scan: {e}")
        return False

def get_scan_history(limit=100):
    """Get scan history for admin dashboard"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
            return history['scans'][:limit]
        return []
    except Exception as e:
        print(f"Error reading history: {e}")
        return []

def get_scan_stats():
    """Get statistics for admin dashboard"""
    try:
        if not os.path.exists(HISTORY_FILE):
            return {
                'total_scans': 0,
                'safe_scans': 0,
                'malicious_scans': 0,
                'suspicious_scans': 0,
                'qr_scans': 0,
                'url_scans': 0,
                'voice_scans': 0
            }
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        scans = history['scans']
        
        stats = {
            'total_scans': len(scans),
            'safe_scans': sum(1 for s in scans if s.get('is_safe')),
            'malicious_scans': sum(1 for s in scans if not s.get('is_safe') and s.get('risk') == 'HIGH'),
            'suspicious_scans': sum(1 for s in scans if not s.get('is_safe') and s.get('risk') == 'MEDIUM'),
            'qr_scans': sum(1 for s in scans if s.get('type') == 'qr'),
            'url_scans': sum(1 for s in scans if s.get('type') == 'url'),
            'voice_scans': sum(1 for s in scans if s.get('type') == 'voice')
        }
        
        return stats
    except Exception as e:
        print(f"Error calculating stats: {e}")
        return {}

if __name__ == "__main__":
    # Test logging
    test_result = {
        'is_safe': False,
        'risk': 'HIGH',
        'warnings': ['Test warning 1', 'Test warning 2']
    }
    
    log_scan('qr', 'http://fake-site.tk/scam', test_result, '192.168.1.1')
    print("✅ Test scan logged")
    
    stats = get_scan_stats()
    print(f"\n📊 Stats: {stats}")
