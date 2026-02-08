"""
UPI QR Code Fraud Analysis
"""

print("="*60)
print("UPI QR CODE FRAUD - ANALYSIS")
print("="*60)

# Common UPI fraud patterns
upi_fraud_patterns = {
    "Fake Payment Links": [
        "Scammer sends fake UPI payment link",
        "Looks like payment request but actually money deduction",
        "Example: upi://pay?pa=scammer@paytm&pn=FakeShop&am=1000"
    ],
    
    "QR Code Swap": [
        "Scammer replaces merchant QR with their own",
        "Customer scans thinking it's shop QR",
        "Money goes to scammer instead of merchant"
    ],
    
    "Fake UPI Apps": [
        "Fake apps that look like Paytm/PhonePe/GooglePay",
        "Steal UPI PIN and credentials",
        "Download links in QR codes"
    ],
    
    "Refund Scams": [
        "Scammer claims to give refund",
        "Sends payment request instead",
        "Victim thinks they're receiving money"
    ],
    
    "KYC Update Scams": [
        "Fake KYC update links",
        "Asks for bank details, UPI PIN",
        "Links to phishing websites"
    ]
}

print("\nUPI FRAUD TYPES:")
print("-"*60)
for fraud_type, details in upi_fraud_patterns.items():
    print(f"\n{fraud_type}:")
    for detail in details:
        print(f"  - {detail}")

# UPI QR code structure
print("\n" + "="*60)
print("LEGITIMATE UPI QR CODE STRUCTURE")
print("="*60)
print("""
Format: upi://pay?pa=<VPA>&pn=<Name>&am=<Amount>&cu=<Currency>

Parameters:
- pa: Payee VPA (e.g., merchant@paytm)
- pn: Payee Name
- am: Amount (optional)
- cu: Currency (INR)
- tn: Transaction Note
- mc: Merchant Code
- tid: Transaction ID

Example (Legitimate):
upi://pay?pa=merchant@paytm&pn=ShopName&mc=1234&tid=TXN123

Example (Fraud):
upi://pay?pa=scammer@paytm&pn=FakeRefund&am=5000&tn=RefundAmount
""")

# Detection features for UPI fraud
print("\n" + "="*60)
print("UPI FRAUD DETECTION FEATURES")
print("="*60)

detection_features = {
    "Suspicious VPA Patterns": [
        "Random numbers in VPA (scammer123@paytm)",
        "Generic names (user@paytm, payment@phonepe)",
        "Misspelled merchant names (paytm@paytm instead of merchant@paytm)"
    ],
    
    "Suspicious Amount Patterns": [
        "Very high amounts (>10,000)",
        "Round numbers (5000, 10000)",
        "Amount in payment request (should be collect request)"
    ],
    
    "Suspicious Transaction Notes": [
        "Refund, KYC, Update, Verify",
        "Urgent, Prize, Winner, Claim",
        "OTP, PIN, Password"
    ],
    
    "Missing Parameters": [
        "No merchant code (mc)",
        "No transaction ID (tid)",
        "Generic payee name"
    ],
    
    "URL-based QR Codes": [
        "QR contains URL instead of upi://",
        "Links to fake payment pages",
        "Download links for fake apps"
    ]
}

for category, features in detection_features.items():
    print(f"\n{category}:")
    for feature in features:
        print(f"  ✓ {feature}")

# Dataset requirements
print("\n" + "="*60)
print("DATASET REQUIREMENTS FOR UPI FRAUD")
print("="*60)
print("""
Current Dataset:
- 651K URLs (phishing, malware, defacement)
- General web-based fraud
- NOT specific to UPI QR codes

Required Dataset:
- UPI QR code strings (upi://pay?...)
- Legitimate merchant QR codes
- Fraudulent QR codes
- Indian payment app URLs
- Fake payment pages

Sources:
1. Cybercrime reports (Indian)
2. UPI fraud case studies
3. Synthetic fraud QR generation
4. Real merchant QR codes (anonymized)
5. Reported scam QR codes
""")

# Recommendation
print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)
print("""
CURRENT APPROACH:
✅ ML model trained on general phishing URLs
✅ Can detect suspicious domains
✅ Can detect phishing keywords
❌ NOT trained on UPI-specific patterns
❌ May miss UPI QR code fraud

IMPROVED APPROACH:
1. Add UPI-specific pattern detection
2. Parse UPI QR code parameters
3. Validate VPA format
4. Check merchant code presence
5. Detect suspicious transaction notes
6. Flag high amounts in payment requests
7. Combine with existing ML model

HYBRID SOLUTION:
- Use ML for URL-based QR codes
- Use rule-based for UPI QR codes
- Combine both for maximum accuracy
""")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("""
1. Create UPI QR code parser
2. Add UPI-specific fraud rules
3. Generate synthetic UPI fraud dataset
4. Train separate model for UPI QR codes
5. Integrate with existing system
""")

print("\n" + "="*60)
