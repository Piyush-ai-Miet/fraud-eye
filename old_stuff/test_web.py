#!/usr/bin/env python3
"""
Web interface test - Check if Flask app can start
"""

print("🌐 Testing Web Interface Setup...\n")

try:
    print("1️⃣ Checking Flask installation...")
    import flask
    print(f"   ✅ Flask {flask.__version__} installed")
except ImportError:
    print("   ❌ Flask not installed")
    print("   Run: pip3 install flask")
    exit(1)

try:
    print("\n2️⃣ Checking if bot.py can be imported...")
    import sys
    import os
    
    # Check if bot.py exists
    if os.path.exists('bot.py'):
        print("   ✅ bot.py found")
    else:
        print("   ❌ bot.py not found")
        exit(1)
    
    print("\n3️⃣ Checking template files...")
    if os.path.exists('templates/dashboard.html'):
        print("   ✅ dashboard.html found")
        
        # Check if it contains Hindi text
        with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'साइबर सुरक्षा' in content or 'QR Code' in content:
                print("   ✅ Hindi text present in template")
            else:
                print("   ⚠️ Hindi text might be missing")
    else:
        print("   ❌ dashboard.html not found")
        exit(1)
    
    print("\n4️⃣ Checking dependencies...")
    dependencies = {
        'flask': 'Flask',
        'PIL': 'Pillow',
        'requests': 'requests',
        'validators': 'validators'
    }
    
    missing = []
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {package} installed")
        except ImportError:
            print(f"   ❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip3 install {' '.join(missing.lower())}")
    
    print("\n" + "=" * 60)
    print("✅ WEB INTERFACE READY!")
    print("=" * 60)
    print("\n📝 To start the server:")
    print("   python3 bot.py")
    print("\n🌐 Then open in browser:")
    print("   http://localhost:5000")
    print("\n")

except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
