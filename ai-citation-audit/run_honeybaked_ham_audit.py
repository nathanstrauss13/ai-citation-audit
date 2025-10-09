#!/usr/bin/env python3
"""
Wrapper script to run HoneyBaked Ham Citation Audit
with environment setup and error handling.
"""

import os
import sys
import subprocess
import venv
import platform
from dotenv import load_dotenv

def check_python_version():
    """Ensure Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ is required.")
        sys.exit(1)

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist"""
    venv_path = '.venv'
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("Virtual environment created.")
    return venv_path

def install_dependencies(venv_path):
    """Install project dependencies in the virtual environment"""
    pip_path = os.path.join(venv_path, 'bin' if platform.system() != 'Windows' else 'Scripts', 'pip')
    
    try:
        # Upgrade pip first
        subprocess.check_call([pip_path, 'install', '--upgrade', 'pip'])
        
        # Install requirements
        subprocess.check_call([pip_path, 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_api_keys():
    """Check if required API keys are set"""
    required_keys = [
        'PERPLEXITY_API_KEY', 
        'OPENAI_API_KEY', 
        'ANTHROPIC_API_KEY', 
        'GEMINI_API_KEY'
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.environ.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("Warning: The following API keys are not set:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\nPlease set these keys in a .env file or export them as environment variables.")
        confirm = input("Do you want to continue without these keys? (y/N): ")
        if confirm.lower() != 'y':
            sys.exit(1)

def run_audit():
    """Run the HoneyBaked Ham Citation Audit"""
    python_path = os.path.join('.venv', 'bin' if platform.system() != 'Windows' else 'Scripts', 'python')
    
    try:
        subprocess.check_call([
            python_path, 
            'honeybaked_ham_citation_audit.py'
        ])
    except subprocess.CalledProcessError as e:
        print(f"Error running audit: {e}")
        sys.exit(1)

def main():
    """Main execution function"""
    print("🍖 HoneyBaked Ham Citation Audit Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    check_api_keys()
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    
    # Install dependencies
    install_dependencies(venv_path)
    
    # Run the audit
    run_audit()
    
    print("\n✅ HoneyBaked Ham Citation Audit Completed Successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAudit interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
