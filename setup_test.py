"""
Quick Setup and Testing Script
Run this to verify the installation and test components
"""

import sys
import subprocess
from pathlib import Path

def check_packages():
    """Check if all required packages are installed"""
    print("📦 Checking required packages...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'ultralytics': 'ultralytics',
        'pyttsx3': 'pyttsx3',
        'streamlit': 'streamlit',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} (missing)")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All packages found!\n")
    return True


def test_database():
    """Test database initialization"""
    print("🗄️  Testing database...")
    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager("test_memory.db")
        print("  ✓ Database initialized")
        
        # Test operations
        db.log_object_detection("test_object", 0.95, "center")
        print("  ✓ Object logging works")
        
        db.log_activity("sitting", 0.90)
        print("  ✓ Activity logging works")
        
        # Cleanup
        import os
        if os.path.exists("test_memory.db"):
            os.remove("test_memory.db")
        
        print("✓ Database tests passed!\n")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}\n")
        return False


def test_modules():
    """Test module imports"""
    print("🧠 Testing modules...")
    try:
        from modules.object_detector import MockObjectDetector
        print("  ✓ Object detector imports")
        
        from modules.activity_recognizer import MockActivityRecognizer
        print("  ✓ Activity recognizer imports")
        
        from modules.reminder_engine import MockReminderEngine
        print("  ✓ Reminder engine imports")
        
        print("✓ Module imports successful!\n")
        return True
    except Exception as e:
        print(f"✗ Module error: {e}\n")
        return False


def show_quick_start():
    """Show quick start commands"""
    print("🚀 Quick Start Guide:")
    print("\n1. Run with mock data (no camera needed):")
    print("   python app.py --mock")
    print("\n2. Run with webcam:")
    print("   python app.py")
    print("\n3. Launch web dashboard:")
    print("   streamlit run ui/dashboard.py")
    print("\n4. Run headless (no display):")
    print("   python app.py --headless --duration 30")


def main():
    print("=" * 50)
    print("Memory Aid System - Setup Verification")
    print("=" * 50 + "\n")
    
    all_ok = True
    
    # Change to script directory
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    
    all_ok &= check_packages()
    all_ok &= test_database()
    all_ok &= test_modules()
    
    if all_ok:
        print("✅ All tests passed! System is ready to use.\n")
        show_quick_start()
    else:
        print("❌ Some tests failed. Please install missing packages.")
        print("Run: pip install -r requirements.txt")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
