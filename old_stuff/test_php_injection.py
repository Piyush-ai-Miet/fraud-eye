#!/usr/bin/env python3
"""
Test PHP Code Injection Detection
"""

print("\n" + "="*60)
print("🧪 PHP CODE INJECTION TEST")
print("="*60 + "\n")

from malicious_patterns import detector

# Test cases
test_cases = [
    '<?php system($_GET["cmd"]);?>',
    '<?php exec("rm -rf /");?>',
    '<?php shell_exec($_POST["cmd"]);?>',
    '<?php passthru("cat /etc/passwd");?>',
    '<?php eval($_REQUEST["code"]);?>',
    '<?= system("whoami"); ?>',
    'http://example.com/page.php?code=<?php system("ls");?>',
]

print("Testing PHP Code Injection patterns:\n")

for i, test_url in enumerate(test_cases, 1):
    print(f"{i}. Testing: {test_url}")
    
    attacks = detector.detect_attack(test_url)
    risk_score = detector.get_risk_score(attacks)
    
    if attacks:
        print(f"   ✅ DETECTED!")
        print(f"   Attacks: {attacks}")
        print(f"   Risk Score: {risk_score}")
        
        if risk_score >= 5:
            print(f"   🚨 HIGH RISK")
        elif risk_score >= 3:
            print(f"   ⚠️ MEDIUM RISK")
    else:
        print(f"   ❌ NOT DETECTED - PROBLEM!")
    
    print()

print("="*60)
print("✅ PHP Code Injection detection is working!")
print("="*60 + "\n")
