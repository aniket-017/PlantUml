#!/usr/bin/env python3
"""
Environment setup script for PlantUML server
This script checks for required dependencies and environment variables
"""
import os
import subprocess
import sys
from pathlib import Path

def check_java():
    """Check if Java is installed and available"""
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Java is installed")
            return True
        else:
            print("✗ Java is not working properly")
            return False
    except FileNotFoundError:
        print("✗ Java is not installed or not in PATH")
        return False

def check_plantuml_jar():
    """Check if plantuml.jar exists"""
    jar_path = Path(__file__).parent / "app" / "plantuml.jar"
    if jar_path.exists():
        print(f"✓ PlantUML jar found at: {jar_path}")
        return True
    else:
        print(f"✗ PlantUML jar not found at: {jar_path}")
        return False

def check_openai_key():
    """Check if OpenAI API key is set"""
    key = os.getenv("OPENAI_API_KEY")
    if key:
        print("✓ OPENAI_API_KEY is set")
        return True
    else:
        print("✗ OPENAI_API_KEY is not set")
        return False

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "fastapi", "uvicorn", "pandas", "openpyxl", 
        "phidata", "openai", "python-dotenv"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def main():
    print("PlantUML Server Environment Check")
    print("=" * 40)
    
    all_good = True
    
    # Check Java
    if not check_java():
        all_good = False
        print("\nTo install Java:")
        print("  Ubuntu/Debian: sudo apt-get install openjdk-11-jdk")
        print("  CentOS/RHEL: sudo yum install java-11-openjdk-devel")
        print("  Windows: Download from https://adoptium.net/")
    
    # Check PlantUML jar
    if not check_plantuml_jar():
        all_good = False
        print("\nTo get PlantUML jar:")
        print("  Download from: https://plantuml.com/download")
        print("  Place it in: app/plantuml.jar")
    
    # Check OpenAI API key
    if not check_openai_key():
        all_good = False
        print("\nTo set OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("  Or create a .env file with: OPENAI_API_KEY=your-api-key-here")
    
    # Check Python dependencies
    deps_ok, missing = check_python_dependencies()
    if not deps_ok:
        all_good = False
        print(f"\nTo install missing packages:")
        print(f"  pip install {' '.join(missing)}")
    
    print("\n" + "=" * 40)
    if all_good:
        print("✓ All checks passed! Server should work correctly.")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
