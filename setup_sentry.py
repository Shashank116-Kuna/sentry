#!/usr/bin/env python3
"""
SENTRY Automated Setup Script for Beginners
Run this script to automatically create all necessary files
"""

import os
import sys
from pathlib import Path

# ANSI color codes for pretty output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_step(step_num, message):
    print(f"\n{BLUE}[Step {step_num}]{RESET} {message}")

def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message):
    print(f"{RED}✗{RESET} {message}")

def print_warning(message):
    print(f"{YELLOW}⚠{RESET} {message}")

def check_python_version():
    """Check if Python version is 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python 3.9+ required. You have Python {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_directory_structure():
    """Create all necessary directories"""
    print_step(1, "Creating directory structure...")
    
    directories = [
        "backend/api",
        "backend/nlp",
        "backend/security",
        "backend/utils",
        "frontend/assets/js",
        "frontend/assets/css",
        "data",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Created {directory}/")
    
    return True

def create_init_files():
    """Create __init__.py files for Python packages"""
    print_step(2, "Creating Python package files...")
    
    init_files = [
        "backend/__init__.py",
        "backend/api/__init__.py",
        "backend/nlp/__init__.py",
        "backend/security/__init__.py",
        "backend/utils/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print_success(f"Created {init_file}")
    
    return True

def create_requirements_file():
    """Create requirements.txt"""
    print_step(3, "Creating requirements.txt...")
    
    requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print_success("Created requirements.txt")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(4, "Installing dependencies (this may take a few minutes)...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("All dependencies installed successfully")
            return True
        else:
            print_error("Failed to install dependencies")
            print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Error installing dependencies: {e}")
        return False

def download_file_from_artifacts(filename):
    """
    Placeholder function - in real use, files would be copied from artifacts
    For now, this will provide instructions
    """
    return None

def main():
    """Main setup function"""
    print("=" * 60)
    print(f"{BLUE}SENTRY Setup Script for Beginners{RESET}")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check current directory
    cwd = Path.cwd()
    print(f"\n{YELLOW}Current directory:{RESET} {cwd}")
    
    response = input(f"\n{YELLOW}Is this where you want to create SENTRY? (yes/no):{RESET} ").strip().lower()
    if response not in ['yes', 'y']:
        print(f"\n{YELLOW}Please navigate to your desired directory and run this script again.{RESET}")
        print(f"Example: cd Desktop/my-projects")
        sys.exit(0)
    
    # Create directory structure
    if not create_directory_structure():
        print_error("Failed to create directories")
        sys.exit(1)
    
    # Create __init__.py files
    if not create_init_files():
        print_error("Failed to create package files")
        sys.exit(1)
    
    # Create requirements.txt
    if not create_requirements_file():
        print_error("Failed to create requirements.txt")
        sys.exit(1)
    
    # Ask about installing dependencies
    print(f"\n{YELLOW}Would you like to install dependencies now?{RESET}")
    print("(You can also run: pip install -r requirements.txt later)")
    response = input("Install now? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        if not install_dependencies():
            print_warning("Dependency installation failed, but you can continue manually")
    
    # Final instructions
    print("\n" + "=" * 60)
    print(f"{GREEN}Setup Phase 1 Complete!{RESET}")
    print("=" * 60)
    
    print(f"\n{BLUE}Next Steps:{RESET}")
    print(f"\n1. I will now guide you to create the code files")
    print(f"2. You have two options:")
    print(f"\n   {YELLOW}Option A: Manual Creation{RESET}")
    print(f"   - I'll show you each file to create")
    print(f"   - Copy code from the artifacts I provided earlier")
    print(f"   - Save in the correct location")
    print(f"\n   {YELLOW}Option B: Use the file templates{RESET}")
    print(f"   - I'll create template files with instructions")
    print(f"   - You fill in the code from artifacts")
    
    print(f"\n{BLUE}Your directory structure:{RESET}")
    print_directory_tree(".", 0, max_depth=2)
    
    print(f"\n{GREEN}Ready to continue? Let me know which option you prefer!{RESET}")

def print_directory_tree(directory, indent, max_depth):
    """Print directory tree structure"""
    if indent > max_depth:
        return
    
    try:
        entries = sorted(Path(directory).iterdir(), key=lambda x: (not x.is_dir(), x.name))
        for entry in entries:
            if entry.name.startswith('.') or entry.name == '__pycache__':
                continue
            
            prefix = "  " * indent + "├── "
            if entry.is_dir():
                print(f"{prefix}{entry.name}/")
                print_directory_tree(entry, indent + 1, max_depth)
            else:
                print(f"{prefix}{entry.name}")
    except PermissionError:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Setup cancelled by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
        