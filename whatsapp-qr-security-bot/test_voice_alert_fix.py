#!/usr/bin/env python3
"""
Test script to verify voice alert fix for non-URL text
"""

import sys
sys.path.insert(0, '.')

from app_simple import checker

def test_voice_alert_scenarios():
    """Test different scenarios for voice alerts"""
    
    print("=" * 60)
    print("VOICE ALERT FIX TEST")
    print("=" * 60)
    
    # Test 1: Plain text (not a URL)
    print("\n1. Testing plain text (not a URL):")
    print("   Input: 'hello world'")
    result = checker.check_url_safety('hello world')
    print(f"   ✓ is_safe: {result['is_safe']}")
    print(f"   ✓ is_not_url: {result.get('is_not_url', False)}")
    print(f"   ✓ message: {result['message_hi']}")
    print(f"   ✓ Expected voice: 'यह कोई लिंक नहीं है। यह सिर्फ टेक्स्ट है।'")
    assert result.get('is_not_url') == True, "Should have is_not_url flag"
    assert result['is_safe'] == True, "Plain text should be safe"
    print("   ✅ PASS")
    
    # Test 2: Safe URL
    print("\n2. Testing safe URL:")
    print("   Input: 'https://google.com'")
    result = checker.check_url_safety('https://google.com')
    print(f"   ✓ is_safe: {result['is_safe']}")
    print(f"   ✓ is_not_url: {result.get('is_not_url', False)}")
    print(f"   ✓ message: {result['message_hi']}")
    print(f"   ✓ Expected voice: 'यह लिंक सुरक्षित है। डोमेन नाम है google.com।'")
    assert result.get('is_not_url') != True, "Should NOT have is_not_url flag"
    assert result['is_safe'] == True, "Google should be safe"
    print("   ✅ PASS")
    
    # Test 3: Suspicious URL
    print("\n3. Testing suspicious URL:")
    print("   Input: 'http://192.168.1.1'")
    result = checker.check_url_safety('http://192.168.1.1')
    print(f"   ✓ is_safe: {result['is_safe']}")
    print(f"   ✓ is_not_url: {result.get('is_not_url', False)}")
    print(f"   ✓ message: {result['message_hi']}")
    print(f"   ✓ Expected voice: 'सावधान! यह लिंक खतरनाक है...'")
    assert result.get('is_not_url') != True, "Should NOT have is_not_url flag"
    assert result['is_safe'] == False, "IP address should be suspicious"
    print("   ✅ PASS")
    
    # Test 4: Random text
    print("\n4. Testing random text:")
    print("   Input: 'mat kar lala'")
    result = checker.check_url_safety('mat kar lala')
    print(f"   ✓ is_safe: {result['is_safe']}")
    print(f"   ✓ is_not_url: {result.get('is_not_url', False)}")
    print(f"   ✓ message: {result['message_hi']}")
    print(f"   ✓ Expected voice: 'यह कोई लिंक नहीं है। यह सिर्फ टेक्स्ट है।'")
    assert result.get('is_not_url') == True, "Should have is_not_url flag"
    print("   ✅ PASS")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nSummary:")
    print("- Plain text now has 'is_not_url: True' flag")
    print("- Frontend will check this flag and speak correct message")
    print("- Voice will say 'यह कोई लिंक नहीं है' instead of 'यह लिंक सुरक्षित है'")
    print("\nFix complete! ✨")

if __name__ == '__main__':
    test_voice_alert_scenarios()
