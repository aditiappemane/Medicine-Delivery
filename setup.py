#!/usr/bin/env python3
"""
Setup script for Medicine Delivery API
"""

import os
import shutil
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def setup_project():
    """Setup the Medicine Delivery API project"""
    print("=== Medicine Delivery API Setup ===\n")
    
    # Check if Python is available
    if not run_command("python --version", "Checking Python installation"):
        print("Python is not installed or not in PATH")
        return False
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("Failed to install dependencies")
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("✓ Created .env file from env.example")
        else:
            print("✗ env.example not found")
            return False
    
    # Initialize database
    if not run_command("python init_db.py", "Initializing database"):
        print("Failed to initialize database")
        return False
    
    print("\n=== Setup Completed Successfully! ===")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run the application: python run.py")
    print("3. Access the API at: http://localhost:8000")
    print("4. View documentation at: http://localhost:8000/docs")
    print("5. Run tests: python test_api.py")
    
    return True

if __name__ == "__main__":
    success = setup_project()
    sys.exit(0 if success else 1) 