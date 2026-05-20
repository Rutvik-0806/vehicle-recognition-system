#!/usr/bin/env python3
"""
Setup script for Vehicle Recognition System
This script installs all required dependencies and sets up the environment.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system().lower()
    
    if system == "windows":
        print("\n🖥️  Windows detected")
        print("📝 Please install the following manually:")
        print("   1. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   2. Visual Studio Build Tools (for TensorFlow)")
        print("   3. CUDA Toolkit (optional, for GPU support)")
        
    elif system == "linux":
        print("\n🐧 Linux detected")
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y tesseract-ocr tesseract-ocr-eng",
            "sudo apt-get install -y libgl1-mesa-glx libglib2.0-0",
            "sudo apt-get install -y libsm6 libxext6 libxrender-dev",
            "sudo apt-get install -y libgomp1 libgcc-s1"
        ]
        for cmd in commands:
            if not run_command(cmd, f"Installing system dependency: {cmd}"):
                return False
                
    elif system == "darwin":
        print("\n🍎 macOS detected")
        commands = [
            "brew install tesseract",
            "brew install tesseract-lang"
        ]
        for cmd in commands:
            if not run_command(cmd, f"Installing system dependency: {cmd}"):
                return False
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        print("\n📦 Creating virtual environment...")
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate virtual environment
    if platform.system().lower() == "windows":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "source venv/bin/activate"
    
    print(f"🔧 Activating virtual environment: {activate_script}")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📚 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command("venv\\Scripts\\python.exe -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install dependencies in order of complexity
    dependencies = [
        # Core Django and web dependencies
        "Django==4.2.7",
        "django-crispy-forms==2.4",
        "crispy-bootstrap5==2025.6",
        "python-decouple==3.8",
        "requests==2.32.4",
        
        # Image processing
        "Pillow==11.3.0",
        "opencv-python==4.8.1.78",
        "numpy==1.26.4",
        "imutils==0.5.4",
        "scikit-image==0.22.0",
        "matplotlib==3.8.2",
        
        # OCR and deep learning
        "easyocr==1.7.0",
        "pytesseract==0.3.10",
        "tensorflow==2.15.0",
        "keras==2.15.0",
        
        # SMS services
        "twilio==8.10.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"venv\\Scripts\\pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Warning: Failed to install {dep}, continuing...")
    
    return True

def setup_django():
    """Setup Django project"""
    print("\n🚀 Setting up Django project...")
    
    # Run migrations
    if not run_command("venv\\Scripts\\python.exe manage.py makemigrations", "Creating migrations"):
        return False
    
    if not run_command("venv\\Scripts\\python.exe manage.py migrate", "Running migrations"):
        return False
    
    # Create superuser
    print("\n👤 Creating superuser...")
    print("Please enter the following details for the admin user:")
    superuser_cmd = "venv\\Scripts\\python.exe manage.py createsuperuser --noinput"
    env = os.environ.copy()
    env.update({
        'DJANGO_SUPERUSER_USERNAME': 'admin',
        'DJANGO_SUPERUSER_EMAIL': 'admin@example.com',
        'DJANGO_SUPERUSER_PASSWORD': 'admin123'
    })
    
    try:
        subprocess.run(superuser_cmd, shell=True, env=env, check=True)
        print("✅ Superuser created: admin/admin123")
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation failed, you can create it manually later")
    
    # Create sample data
    if not run_command("venv\\Scripts\\python.exe manage.py setup_sample_data", "Creating sample data"):
        print("⚠️  Sample data creation failed, continuing...")
    
    return True

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Creating environment file...")
    
    if not os.path.exists(".env"):
        if os.path.exists("env_example.txt"):
            import shutil
            shutil.copy("env_example.txt", ".env")
            print("✅ Created .env file from template")
            print("📋 Please edit .env file with your actual configuration")
        else:
            print("❌ env_example.txt not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main setup function"""
    print("🚗 Vehicle Recognition System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    if not install_system_dependencies():
        print("⚠️  System dependency installation had issues, continuing...")
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("⚠️  Some dependencies failed to install, but continuing...")
    
    # Setup Django
    if not setup_django():
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Configure SMS and email services")
    print("3. Run: venv\\Scripts\\python.exe manage.py runserver")
    print("4. Access the system at: http://127.0.0.1:8000")
    print("5. Login with: admin/admin123")
    
    print("\n🔧 For SMS configuration:")
    print("- Fast2SMS: Get API key from https://www.fast2sms.com/")
    print("- TextLocal: Get API key from https://www.textlocal.in/")
    print("- Twilio: Get credentials from https://www.twilio.com/")
    print("- MSG91: Get API key from https://msg91.com/")
    
    print("\n📧 For email configuration:")
    print("- Use Gmail with App Password")
    print("- Or configure any SMTP server")

if __name__ == "__main__":
    main() 