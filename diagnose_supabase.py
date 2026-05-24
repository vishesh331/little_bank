#!/usr/bin/env python3
"""Diagnose supabase installation issues."""

import subprocess
import sys
import os

print("=" * 70)
print("SUPABASE INSTALLATION DIAGNOSTIC")
print("=" * 70)

# Check Python version
print(f"\n1. Python Version: {sys.version}")
print(f"   Executable: {sys.executable}")

# Try to check pip version
print("\n2. Checking pip version...")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, text=True, timeout=10)
    print(f"   {result.stdout.strip()}")
except Exception as e:
    print(f"   Error: {e}")

# Try dry-run of supabase installation to see what fails
print("\n3. Attempting dry-run of supabase installation...")
print("   (This will show what packages are needed without installing)")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "install", 
                           "--dry-run", "supabase"],
                          capture_output=True, text=True, timeout=30)
    print("   STDOUT:")
    print("   " + "\n   ".join(result.stdout.split("\n")[:20]))  # First 20 lines
    if result.stderr:
        print("\n   STDERR:")
        print("   " + "\n   ".join(result.stderr.split("\n")[:20]))
    print(f"\n   Return code: {result.returncode}")
except subprocess.TimeoutExpired:
    print("   Timeout: Installation dry-run took too long")
except Exception as e:
    print(f"   Error running dry-run: {e}")

# Try to install with verbose output
print("\n4. Attempting actual supabase installation (verbose)...")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "install", 
                           "-v", "supabase"],
                          capture_output=True, text=True, timeout=120)
    
    # Show last 30 lines of output (where errors usually appear)
    lines = result.stdout.split("\n")
    if len(lines) > 30:
        print("   Last 30 lines of output:")
        for line in lines[-30:]:
            if line.strip():
                print(f"   {line}")
    else:
        print(result.stdout)
    
    if result.stderr:
        print("\n   STDERR (if any):")
        print(result.stderr)
    
    print(f"\n   Return code: {result.returncode}")
    
except subprocess.TimeoutExpired:
    print("   Timeout: Installation took too long (>2 minutes)")
except Exception as e:
    print(f"   Error during installation: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
