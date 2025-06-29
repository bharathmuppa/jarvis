#!/usr/bin/env python3
"""
Installation script for Advanced JARVIS dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_package(package):
    """Check if a package is already installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def main():
    """Install all required packages for Advanced JARVIS"""
    print("🤖" + "="*50 + "🤖")
    print("     ADVANCED JARVIS DEPENDENCY INSTALLER")
    print("🤖" + "="*50 + "🤖")
    
    # Core dependencies
    core_packages = [
        "openai>=0.27.8",
        "anthropic",
        "elevenlabs",
        "SpeechRecognition",
        "PyAudio",
        "pyttsx3",
        "requests",
        "aiohttp",
        "asyncio"
    ]
    
    # Optional voice packages
    voice_packages = [
        "edge-tts",
        "gtts",
        "pygame"
    ]
    
    # Optional system packages
    system_packages = [
        "psutil",
        "neo4j",
        "ollama-python"
    ]
    
    print("\n📦 Installing core packages...")
    for package in core_packages:
        package_name = package.split(">=")[0].split("==")[0]
        if not check_package(package_name.replace("-", "_")):
            install_package(package)
        else:
            print(f"✅ {package_name} already installed")
    
    print("\n🔊 Installing voice packages...")
    for package in voice_packages:
        if not check_package(package.replace("-", "_")):
            install_package(package)
        else:
            print(f"✅ {package} already installed")
    
    print("\n🔧 Installing system packages...")
    for package in system_packages:
        if not check_package(package.replace("-", "_")):
            install_package(package)
        else:
            print(f"✅ {package} already installed")
    
    print("\n🔑 Setting up API keys...")
    
    # Check for required API keys
    api_keys = {
        "OPENAI_API_KEY": "OpenAI API key for ChatGPT",
        "ANTHROPIC_API_KEY": "Anthropic API key for Claude",
        "ELEVEN_API_KEY": "ElevenLabs API key for premium TTS"
    }
    
    missing_keys = []
    for key, description in api_keys.items():
        if not os.getenv(key):
            missing_keys.append((key, description))
            print(f"❌ Missing: {key} ({description})")
        else:
            print(f"✅ Found: {key}")
    
    if missing_keys:
        print(f"\n⚠️  Please set the following environment variables:")
        for key, description in missing_keys:
            print(f"   export {key}='your_api_key_here'  # {description}")
        
        print(f"\n💡 You can add these to your ~/.bashrc or ~/.zshrc file")
        print(f"💡 Or create a .env file in the project directory")
    
    print("\n🚀 Installation complete!")
    print("\nNext steps:")
    print("1. Set your API keys (see above)")
    print("2. Run: python3 app_advanced_jarvis.py --system-status")
    print("3. Run: python3 app_advanced_jarvis.py")
    print("\n🤖 Welcome to Advanced JARVIS!")

if __name__ == "__main__":
    main()