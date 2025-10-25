#!/usr/bin/env python3
"""
ShipDB Demo Runner - Clean Interface for All Demos
Run different database demos from a single interface
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("🚀" + "="*60 + "🚀")
    print("🚀" + " "*20 + "SHIPDB DEMO RUNNER" + " "*20 + "🚀")
    print("🚀" + " "*15 + "Clean Project Interface" + " "*15 + "🚀")
    print("🚀" + "="*60 + "🚀")
    print()

def get_project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent

def run_demo(demo_name):
    """Run a specific demo"""
    project_root = get_project_root()
    demo_path = project_root / "scripts" / "demos" / f"{demo_name}.py"
    
    if not demo_path.exists():
        print(f"❌ Demo '{demo_name}' not found!")
        return False
    
    print(f"🚀 Running {demo_name} demo...")
    print("-" * 50)
    
    # Change to backend directory and activate venv
    backend_dir = project_root / "backend"
    os.chdir(backend_dir)
    
    # Run the demo
    try:
        result = subprocess.run([
            sys.executable, str(demo_path)
        ], cwd=str(backend_dir), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed with error: {e}")
        return False

def run_test(test_name):
    """Run a specific test"""
    project_root = get_project_root()
    test_path = project_root / "scripts" / "tests" / f"{test_name}.py"
    
    if not test_path.exists():
        print(f"❌ Test '{test_name}' not found!")
        return False
    
    print(f"🧪 Running {test_name} test...")
    print("-" * 50)
    
    # Change to backend directory and activate venv
    backend_dir = project_root / "backend"
    os.chdir(backend_dir)
    
    # Run the test
    try:
        result = subprocess.run([
            sys.executable, str(test_path)
        ], cwd=str(backend_dir), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test failed with error: {e}")
        return False

def show_menu():
    """Show the main menu"""
    print("📋 Available Demos:")
    print("   1. AWS Infrastructure Demo")
    print("   2. E-commerce Database Generator")
    print("   3. Social Media Database Generator")
    print("   4. E-commerce Sample Data")
    print()
    print("🧪 Available Tests:")
    print("   5. AWS Infrastructure Test")
    print("   6. API Test")
    print("   7. Project Connection Test")
    print()
    print("📚 Documentation:")
    print("   8. View Documentation")
    print()
    print("   0. Exit")
    print()

def show_docs():
    """Show available documentation"""
    project_root = get_project_root()
    docs_dir = project_root / "docs"
    
    print("📚 Available Documentation:")
    print("-" * 30)
    
    for doc_file in docs_dir.glob("*.md"):
        print(f"   • {doc_file.stem}")
    
    print()
    print("💡 To view a document:")
    print(f"   cat {docs_dir}/<filename>.md")

def main():
    print_banner()
    
    while True:
        show_menu()
        choice = input("Enter your choice (0-8): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            run_demo("demo_aws_infrastructure")
        elif choice == "2":
            run_demo("generate_ecommerce_database")
        elif choice == "3":
            run_demo("generate_social_media_database")
        elif choice == "4":
            run_demo("add_ecommerce_sample_data")
        elif choice == "5":
            run_test("test_aws_infrastructure")
        elif choice == "6":
            run_test("test_api")
        elif choice == "7":
            run_test("show_project_connection")
        elif choice == "8":
            show_docs()
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

