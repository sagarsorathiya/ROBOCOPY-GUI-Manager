#!/usr/bin/env python3
"""
Setup script for ROBOCOPY GUI
"""

import os
import sys
import subprocess
import platform

def check_requirements():
    """Check system requirements"""
    print("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if Windows
    if platform.system() != "Windows":
        print("⚠️  This application is designed for Windows systems")
        print("   ROBOCOPY functionality may not work on other platforms")
    else:
        print("✅ Windows operating system detected")
    
    # Check if tkinter is available
    try:
        import tkinter
        print("✅ tkinter GUI library available")
    except ImportError:
        print("❌ tkinter not available. Please install python3-tk package")
        return False
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    
    # Basic dependencies that should work
    basic_deps = ["psutil"]
    
    for dep in basic_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True, text=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not install {dep}")
            print(f"   Error: {e.stderr}")
        except Exception as e:
            print(f"⚠️  Warning: Error installing {dep}: {str(e)}")

def install_optional_dependencies():
    """Install optional dependencies for desktop shortcut creation"""
    print("\nInstalling optional dependencies for desktop shortcut...")
    
    optional_deps = ["winshell", "pywin32"]
    
    for dep in optional_deps:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True, text=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not install {dep}")
            print(f"   Error: {e.stderr}")
            return False
        except Exception as e:
            print(f"⚠️  Warning: Error installing {dep}: {str(e)}")
            return False
    return True

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system() != "Windows":
        print("⚠️  Desktop shortcut creation is only available on Windows")
        return
    
    try:
        # Use importlib to dynamically import modules
        import importlib
        
        # Try to import winshell
        winshell = importlib.import_module('winshell')
        win32com_client = importlib.import_module('win32com.client')
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "ROBOCOPY GUI.lnk")
        target = os.path.join(os.getcwd(), "robocopy_gui.py")
        wDir = os.getcwd()
        
        shell = win32com_client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.save()
        
        print("✅ Desktop shortcut created")
    except ImportError as e:
        print("⚠️  Could not create desktop shortcut")
        print("   Missing required modules: winshell and/or pywin32")
        print("   Install with: pip install winshell pywin32")
        print(f"   Import error: {e}")
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {str(e)}")

def run_tests():
    """Run basic functionality tests"""
    print("\nRunning basic tests...")
    
    try:
        # Test importing main modules
        from robocopy_utils import RobocopyValidator, ConfigManager
        print("✅ Utility modules imported successfully")
        
        # Test validator
        validator = RobocopyValidator()
        valid, error = validator.validate_path("C:\\Windows", "directory")
        if valid:
            print("✅ Path validation working")
        else:
            print(f"⚠️  Path validation test failed: {error}")
        
        # Test config manager
        config_mgr = ConfigManager()
        default_config = config_mgr.get_default_config()
        if default_config:
            print("✅ Configuration manager working")
        
        print("✅ All basic tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Tests failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("ROBOCOPY GUI Setup")
    print("=" * 30)
    
    if not check_requirements():
        print("\n❌ Setup failed due to missing requirements")
        return False
    
    install_dependencies()
    
    if not run_tests():
        print("\n❌ Setup completed with errors")
        return False
    
    # Ask user if they want to install optional dependencies for desktop shortcut
    if platform.system() == "Windows":
        try:
            response = input("\nWould you like to install optional dependencies for desktop shortcut creation? (y/N): ")
            if response.lower().startswith('y'):
                if install_optional_dependencies():
                    create_desktop_shortcut()
                else:
                    print("⚠️  Desktop shortcut creation skipped due to installation errors")
            else:
                print("⚠️  Desktop shortcut creation skipped")
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️  Desktop shortcut creation skipped")
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the application:")
    print(f"   python {os.path.join(os.getcwd(), 'robocopy_gui.py')}")
    print("\nTo build standalone executable:")
    print(f"   python {os.path.join(os.getcwd(), 'build.py')}")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
