#!/usr/bin/env python
"""
Quick test to verify mobile access is working
"""

import requests
import socket

def test_mobile_access():
    """Test if the server is accessible from mobile"""
    
    print("📱 Testing Mobile Access")
    print("=" * 40)
    
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "192.168.71.69"  # Your IP from earlier
    
    print(f"📍 Your computer's IP: {local_ip}")
    print(f"🌐 Mobile access URL: http://{local_ip}:8000")
    
    # Test local access
    try:
        response = requests.get("http://127.0.0.1:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Local access (127.0.0.1:8000) - Working")
        else:
            print(f"❌ Local access failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Local access failed - {e}")
    
    # Test IP access
    try:
        response = requests.get(f"http://{local_ip}:8000", timeout=5)
        if response.status_code == 200:
            print("✅ IP access working - Mobile should be able to connect")
        else:
            print(f"❌ IP access failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ IP access failed - {e}")
    
    print(f"\n📋 Mobile Testing Instructions:")
    print(f"1. Make sure your phone is on the same WiFi network")
    print(f"2. Open browser on your phone")
    print(f"3. Go to: http://{local_ip}:8000")
    print(f"4. You should see the Vehicle Recognition System")
    print(f"5. Try clicking 'Pay Now' links from emails")

if __name__ == "__main__":
    test_mobile_access() 