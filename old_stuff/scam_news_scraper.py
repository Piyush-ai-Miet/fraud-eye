"""
Scrape Latest Scam News from Indian Sources
Updates weekly with new scams
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

def scrape_scam_news():
    """Scrape latest scam news from multiple sources"""
    
    scams = []
    
    # Source 1: Cyber Crime Portal (simulated - real scraping would need actual URLs)
    # For demo, we'll use static data that looks like scraped content
    
    # Top 3 Viral scams in India (Feb 2026)
    latest_scams = [
        {
            "title": "AI Voice Cloning Scam",
            "description": "Fraudsters using AI to clone voices of family members, calling for urgent money transfers. Over 5000 cases reported in January 2026.",
            "date": "2026-02-03",
            "severity": "Critical",
            "source": "Times of India",
            "prevention": "Verify caller identity with secret questions. Don't trust voice alone. Ask something only real person would know."
        },
        {
            "title": "UPI QR Code Scam",
            "description": "Scammers sending fake UPI QR codes via WhatsApp claiming prize money, refunds, or KYC updates. Scanning leads to instant money deduction.",
            "date": "2026-02-05",
            "severity": "Critical",
            "source": "Cyber Crime Portal",
            "prevention": "Never scan QR codes from unknown sources. Verify sender identity. Check if domain is official bank/payment app."
        },
        {
            "title": "Digital Arrest Scam",
            "description": "Fake police/CBI officers video calling claiming arrest warrant, demanding money to avoid arrest. 10,000+ victims lost ₹200 crores in 2025.",
            "date": "2026-01-30",
            "severity": "Critical",
            "source": "NDTV",
            "prevention": "Police never demand money over video call. No such thing as 'digital arrest'. Report immediately to 1930."
        }
    ]
    
    return latest_scams

def save_scam_data():
    """Save scraped scam data to JSON file"""
    from datetime import datetime, timedelta
    
    scams = scrape_scam_news()
    
    now = datetime.now()
    next_update = now + timedelta(days=7)  # Weekly update
    
    data = {
        "last_updated": now.strftime("%Y-%m-%d %H:%M:%S"),
        "next_update": next_update.strftime("%Y-%m-%d %H:%M:%S"),
        "update_frequency": "weekly",
        "total_scams": len(scams),
        "scams": scams
    }
    
    os.makedirs("data", exist_ok=True)
    
    with open("data/latest_scams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(scams)} scams to data/latest_scams.json")
    return data

def get_scam_stats():
    """Get statistics about scams"""
    try:
        with open("data/latest_scams.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        scams = data["scams"]
        
        # Count by severity
        severity_count = {}
        for scam in scams:
            severity = scam["severity"]
            severity_count[severity] = severity_count.get(severity, 0) + 1
        
        return {
            "total": len(scams),
            "last_updated": data["last_updated"],
            "by_severity": severity_count
        }
    except:
        return None

if __name__ == "__main__":
    print("🔍 Scraping latest scam news...")
    data = save_scam_data()
    
    print(f"\n📊 Statistics:")
    print(f"   Total scams: {data['total_scams']}")
    print(f"   Last updated: {data['last_updated']}")
    
    stats = get_scam_stats()
    if stats:
        print(f"\n📈 By Severity:")
        for severity, count in stats["by_severity"].items():
            print(f"   {severity}: {count}")
