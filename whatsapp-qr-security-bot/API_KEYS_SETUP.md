# 🔑 Third-Party API Keys Setup Guide (Simplified)

## Overview
Fraud Eye ab **SIRF 2 legitimate third-party services** use karta hai URL checking ke liye:

### 1. URLScan.io ✅ (FREE, No API Key)
- **Status**: WORKING
- **Rate Limit**: Unlimited
- **Features**: Domain info, IP, Country, Malicious score

### 2. Google Safe Browsing 🔑 (FREE 10,000/day)
- **Status**: READY (needs API key)
- **Rate Limit**: 10,000 requests/day
- **Features**: Google's official malware/phishing detector

**Note**: URLScan.io already working without any setup! Google Safe Browsing optional but highly recommended.

---

## 1. URLScan.io ✅ (Already Working!)

### Free Tier
- Unlimited public scans
- No API key required
- No rate limits

**Already integrated!** No setup needed.

### Features
- Domain scanning
- IP address detection
- Country identification
- Server information
- Malicious score (0-100)

---

## 2. Google Safe Browsing 🔑 (Highly Recommended)

### Free Tier
- 10,000 requests per day
- Google ka official malware/phishing database
- Most trusted source

### Setup Steps
1. Visit: https://console.cloud.google.com/
2. Create new project or select existing
3. Enable "Safe Browsing API"
4. Go to: APIs & Services → Credentials
5. Create API Key
6. Copy your API key

### Add to Environment
```bash
# Linux/Mac
export GOOGLE_SAFEBROWSING_API_KEY="your_api_key_here"

# Windows
set GOOGLE_SAFEBROWSING_API_KEY=your_api_key_here

# Or add to .env file
echo "GOOGLE_SAFEBROWSING_API_KEY=your_api_key_here" >> .env
```

---

## Testing

### Test Third-Party Checker
```bash
# No API key needed for basic testing (URLScan.io works)
python3 third_party_url_checker.py

# With Google Safe Browsing API key
export GOOGLE_SAFEBROWSING_API_KEY="your_key"
python3 third_party_url_checker.py
```

### Test with URL Checker
```bash
# Start server
python3 app_simple.py

# Test in another terminal
curl -X POST http://localhost:5001/api/check-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

---

## API Response Examples

### URLScan.io Response
```json
{
  "service": "URLScan.io",
  "verdict": "SAFE",
  "domain": "google.com",
  "ip": "142.250.185.46",
  "country": "US",
  "server": "gws",
  "message": "Score: 0/100"
}
```

### Google Safe Browsing Response (Safe)
```json
{
  "service": "Google Safe Browsing",
  "is_malicious": false,
  "verdict": "SAFE",
  "message": "No threats detected by Google"
}
```

### Google Safe Browsing Response (Malicious)
```json
{
  "service": "Google Safe Browsing",
  "is_malicious": true,
  "threat_types": ["SOCIAL_ENGINEERING", "MALWARE"],
  "verdict": "MALICIOUS",
  "message": "Detected as: SOCIAL_ENGINEERING, MALWARE"
}
```

---

## Without API Keys

Agar Google Safe Browsing API key nahi hai, to bhi system kaam karega:
- ✅ URLScan.io (free, no key needed) - WORKING
- ✅ Basic checks (HTTPS, IP, domain)

**1 out of 2 services already working!**

---

## Rate Limits

### URLScan.io (Free) ✅
- Unlimited public scans
- No rate limits
- No API key needed
- **Status**: WORKING

### Google Safe Browsing (Free) 🔑
- 10,000 requests/day
- No per-minute limit
- Agar limit exceed ho to: "Quota exceeded" error
- **Status**: READY (needs API key)

---

## Security Best Practices

1. **Never commit API keys to Git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   ```python
   import os
   api_key = os.getenv('GOOGLE_SAFEBROWSING_API_KEY')
   ```

3. **Rotate keys regularly**
   - Change keys every 3-6 months
   - Revoke old keys

4. **Monitor usage**
   - Check API dashboards
   - Set up alerts for quota limits

---

## Troubleshooting

### "API key not configured"
```bash
# Check if environment variable is set
echo $GOOGLE_SAFEBROWSING_API_KEY

# If empty, set it
export GOOGLE_SAFEBROWSING_API_KEY="your_key"
```

### "Quota exceeded"
- Wait until next day (10,000/day limit)
- Or use only URLScan.io (still works!)

### "Invalid API key"
- Check if key is correct
- Check if API is enabled in console
- Regenerate key if needed

---

## Cost Comparison

| Service | Free Tier | API Key Needed | Status |
|---------|-----------|----------------|--------|
| URLScan.io | Unlimited | ❌ No | ✅ Working |
| Google Safe Browsing | 10,000/day | ✅ Yes | 🔑 Ready |

**Recommendation**: 
- **Current Setup**: URLScan.io (working, no key needed)
- **Best Setup**: URLScan.io + Google Safe Browsing (add API key for 10,000/day free)

---

**Status**: ✅ PRODUCTION READY
**Date**: February 7, 2026
**Working Now**: URLScan.io (no API key needed!)
**Recommended Addition**: Google Safe Browsing API key (10,000/day free, most reliable)
