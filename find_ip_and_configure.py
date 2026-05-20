#!/usr/bin/env python
"""
Script to find your computer's IP address and configure the system for mobile access
"""

import socket
import subprocess
import platform
import os

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return None

def get_all_ips():
    """Get all IP addresses of this computer"""
    ips = []
    try:
        hostname = socket.gethostname()
        ips.append(socket.gethostbyname(hostname))
        
        # Get additional IPs
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
    except Exception as e:
        print(f"Error getting IPs: {e}")
    
    return ips

def update_env_file(ip_address):
    """Update .env file with the IP address"""
    env_file = '.env'
    
    # Read existing .env file
    env_content = ""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_content = f.read()
    
    # Add or update BASE_URL
    base_url_line = f"BASE_URL=http://{ip_address}:8000"
    
    if "BASE_URL=" in env_content:
        # Update existing BASE_URL
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('BASE_URL='):
                lines[i] = base_url_line
                break
        env_content = '\n'.join(lines)
    else:
        # Add new BASE_URL
        env_content += f"\n# Base URL for mobile access\n{base_url_line}\n"
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Updated .env file with BASE_URL: {base_url_line}")

def main():
    print("🌐 Finding your computer's IP address for mobile access")
    print("=" * 60)
    
    # Get local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"📍 Your computer's IP address: {local_ip}")
    else:
        print("❌ Could not determine IP address automatically")
        return
    
    # Get all IPs
    all_ips = get_all_ips()
    if all_ips:
        print(f"📋 All available IP addresses:")
        for i, ip in enumerate(all_ips, 1):
            print(f"   {i}. {ip}")
    
    print(f"\n🔧 Configuration for mobile access:")
    print(f"   • Use IP: {local_ip}")
    print(f"   • Port: 8000")
    print(f"   • Full URL: http://{local_ip}:8000")
    
    print(f"\n📱 Mobile Access Instructions:")
    print(f"   1. Make sure your phone is on the same WiFi network as this computer")
    print(f"   2. On your phone, open browser and go to: http://{local_ip}:8000")
    print(f"   3. The payment links in emails/SMS will now work on mobile")
    
    # Update .env file
    print(f"\n⚙️ Updating configuration...")
    update_env_file(local_ip)
    
    print(f"\n✅ Configuration complete!")
    print(f"   • Restart your Django server: python manage.py runserver 0.0.0.0:8000")
    print(f"   • Test mobile access: http://{local_ip}:8000")
    print(f"   • Payment links will now work on mobile devices")

if __name__ == "__main__":
    main() 