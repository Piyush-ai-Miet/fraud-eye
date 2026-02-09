"""
Data Analysis Utility
Analyze scan history and generate statistics
"""
import json
from collections import Counter
from datetime import datetime

class DataAnalyzer:
    def __init__(self, scan_history_file='data/scan_history.json'):
        self.scan_history_file = scan_history_file
        self.scans = []
        self.load_data()
    
    def load_data(self):
        """Load scan history"""
        try:
            with open(self.scan_history_file, 'r') as f:
                self.scans = json.load(f)
        except:
            self.scans = []
    
    def get_total_scans(self):
        """Get total number of scans"""
        return len(self.scans)
    
    def get_scans_by_type(self):
        """Get scan count by type"""
        types = [scan.get('type', 'unknown') for scan in self.scans]
        return dict(Counter(types))
    
    def get_threat_distribution(self):
        """Get distribution of threat levels"""
        risks = [scan.get('result', {}).get('risk', 'UNKNOWN') for scan in self.scans]
        return dict(Counter(risks))
    
    def get_recent_scans(self, limit=10):
        """Get most recent scans"""
        sorted_scans = sorted(self.scans, key=lambda x: x.get('timestamp', ''), reverse=True)
        return sorted_scans[:limit]
    
    def get_malicious_count(self):
        """Count malicious detections"""
        malicious = sum(1 for scan in self.scans 
                       if not scan.get('result', {}).get('is_safe', True))
        return malicious
    
    def get_statistics(self):
        """Get comprehensive statistics"""
        return {
            'total_scans': self.get_total_scans(),
            'scans_by_type': self.get_scans_by_type(),
            'threat_distribution': self.get_threat_distribution(),
            'malicious_count': self.get_malicious_count(),
            'safe_count': self.get_total_scans() - self.get_malicious_count()
        }
    
    def generate_report(self):
        """Generate text report"""
        stats = self.get_statistics()
        
        report = "="*50 + "\n"
        report += "FRAUD EYE - SCAN STATISTICS\n"
        report += "="*50 + "\n\n"
        
        report += f"Total Scans: {stats['total_scans']}\n"
        report += f"Malicious Detected: {stats['malicious_count']}\n"
        report += f"Safe: {stats['safe_count']}\n\n"
        
        report += "Scans by Type:\n"
        for scan_type, count in stats['scans_by_type'].items():
            report += f"  - {scan_type}: {count}\n"
        
        report += "\nThreat Distribution:\n"
        for risk, count in stats['threat_distribution'].items():
            report += f"  - {risk}: {count}\n"
        
        return report

if __name__ == '__main__':
    analyzer = DataAnalyzer()
    print(analyzer.generate_report())
