from realtime_url_checker import realtime_checker

print("="*60)
print("REAL-TIME URL CHECKER TEST")
print("="*60)

test_urls = [
    "https://google.com",
    "https://paytm.com",
    "http://fake-sbi.tk/urgent-login",
    "http://192.168.1.1/verify-otp"
]

for i, url in enumerate(test_urls, 1):
    print(f"\n{i}. Testing: {url}")
    print("-" * 60)
    
    result = realtime_checker.check_url_realtime(url)
    
    # Verdict
    verdict = result.get('verdict', {})
    print(f"   Risk: {verdict.get('risk', 'N/A')}")
    print(f"   Safe: {'✅ YES' if verdict.get('is_safe') else '❌ NO'}")
    print(f"   Message: {verdict.get('message_hi', 'N/A')}")
    print(f"   Risk Score: {verdict.get('risk_score', 0)}")
    
    # SSL Check
    ssl = result.get('checks', {}).get('ssl', {})
    if ssl.get('valid'):
        print(f"   SSL: ✅ Valid (expires in {ssl.get('expires_in_days')} days)")
    else:
        print(f"   SSL: ❌ Invalid - {ssl.get('error', ssl.get('reason', 'Unknown'))}")
    
    # Domain Age
    domain_age = result.get('checks', {}).get('domain_age', {})
    if domain_age.get('age_days'):
        print(f"   Domain Age: {domain_age['age_days']} days")
        print(f"   Created: {domain_age.get('creation_date', 'Unknown')}")
        print(f"   Registrar: {domain_age.get('registrar', 'Unknown')}")
    
    # Content Check
    content = result.get('checks', {}).get('content', {})
    if content.get('accessible', True):
        print(f"   Page Title: {content.get('title', 'N/A')}")
        print(f"   Suspicious Score: {content.get('suspicious_score', 0)}/5")
        if content.get('redirected'):
            print(f"   Redirected to: {content.get('final_url')}")
    
    # Warnings
    if verdict.get('warnings'):
        print(f"   Warnings:")
        for warning in verdict['warnings']:
            print(f"      - {warning}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60 + "\n")
