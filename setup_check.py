#!/usr/bin/env python3
"""
CinemaStream Setup Helper
Quick validation and setup script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python 3.8+ is installed."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. You have {}.{}".format(version.major, version.minor))
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import flask
        print("✓ Flask installed")
        return True
    except ImportError:
        print("❌ Flask not installed")
        print("   Run: pip install -r movie_streaming/requirements.txt")
        return False

def check_folder_structure():
    """Check if all required folders exist."""
    base_dir = Path(__file__).parent
    folders = [
        base_dir / "movie_streaming",
        base_dir / "movie_streaming" / "templates",
        base_dir / "movie_streaming" / "static",
        base_dir / "movie_streaming" / "static" / "css",
        base_dir / "movie_streaming" / "static" / "js",
        base_dir / "movie_streaming" / "static" / "images" / "thumbnails",
    ]
    
    all_exist = True
    for folder in folders:
        if folder.exists():
            print(f"✓ {folder.relative_to(base_dir)}")
        else:
            print(f"❌ {folder.relative_to(base_dir)} (missing)")
            all_exist = False
    
    return all_exist

def check_files():
    """Check if all required files exist."""
    base_dir = Path(__file__).parent
    files = {
        "movie_streaming/app.py": "Flask application",
        "movie_streaming/config.py": "Configuration",
        "movie_streaming/requirements.txt": "Dependencies",
        "movie_streaming/README.md": "Documentation",
        "movie_streaming/templates/base.html": "Base template",
        "movie_streaming/templates/login.html": "Login template",
        "movie_streaming/templates/catalog.html": "Catalog template",
        "movie_streaming/templates/player.html": "Player template",
        "movie_streaming/templates/purchases.html": "Purchases template",
        "movie_streaming/templates/error.html": "Error template",
        "movie_streaming/static/css/style.css": "Styling",
        "movie_streaming/static/js/main.js": "Frontend logic",
    }
    
    all_exist = True
    for file_path, description in files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist

def install_dependencies():
    """Install required packages."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "movie_streaming/requirements.txt"],
            cwd=Path(__file__).parent
        )
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def show_usage():
    """Show usage instructions."""
    print("\n" + "="*60)
    print(" CinemaStream - Setup Complete!")
    print("="*60 + "\n")
    print("🚀 To start the application:\n")
    print("   Option 1 - Direct Flask:")
    print("   $ cd movie_streaming")
    print("   $ python app.py\n")
    print("   Option 2 - From CLI Hub:")
    print("   $ python hub.py")
    print("   → Select option 4: CinemaStream\n")
    print("📱 Then open your browser to:")
    print("   → http://localhost:5000\n")
    print("🔑 Login with demo account:")
    print("   Account: demo001")
    print("   Password: password123\n")
    print("📚 Documentation:")
    print("   → QUICKSTART_MOVIESTREAMING.md")
    print("   → INTEGRATION_GUIDE.md")
    print("   → README_CINEMASTREAM.md\n")
    print("="*60 + "\n")

def main():
    """Main setup check."""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "CinemaStream Setup Validator" + " "*20 + "║")
    print("╚" + "="*58 + "╝\n")
    
    print("🔍 Checking requirements...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Folder Structure", check_folder_structure),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 40)
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Error: {e}")
            all_passed = False
    
    if not all_passed:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("   Try installing dependencies:")
        print("   $ pip install -r movie_streaming/requirements.txt")
        return False
    
    print("\n✅ All checks passed!")
    show_usage()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
