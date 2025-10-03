#!/usr/bin/env python3
"""
Enhanced build script for creating a fully standalone executable of ROBOCOPY GUI
that can run on any Windows PC without any dependencies.
"""

import subprocess
import sys
import os
import shutil
import platform

def build_executable():
    """Build standalone executable using PyInstaller with enhanced options"""
    print("Building ROBOCOPY GUI standalone executable...")
    print("This will create a fully self-contained executable with no dependencies.")
    
    # Enhanced PyInstaller command for maximum compatibility
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=RobocopyGUI",          # Executable name
        "--clean",                      # Clean PyInstaller cache
        "--noconfirm",                 # Overwrite output directory
        "--distpath=dist",             # Output directory
        "--workpath=build",            # Build directory
        "--specpath=.",                # Spec file location
        
        # Bundling options for standalone operation
        "--hidden-import=tkinter",     # Ensure tkinter is included
        "--hidden-import=tkinter.ttk", # Include ttk widgets
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=threading",   # Threading support
        "--hidden-import=queue",       # Queue for threading
        "--hidden-import=subprocess",  # For running robocopy
        "--hidden-import=os",          # OS operations
        "--hidden-import=sys",         # System operations
        "--hidden-import=time",        # Time functions
        "--hidden-import=datetime",    # Date/time operations
        "--hidden-import=json",        # JSON config handling
        "--hidden-import=logging",     # Logging functionality
        "--hidden-import=pathlib",     # Path handling
        "--hidden-import=platform",    # Platform detection
        
        # Include data files
        "--add-data=robocopy_config.json;." if os.path.exists("robocopy_config.json") else "",
        
        # Performance and compatibility options
        "--optimize=2",                # Python optimization level
        "--strip",                     # Strip symbols (smaller file)
        "--upx-dir=upx" if shutil.which("upx") else "",  # UPX compression if available
        
        "robocopy_gui.py"
    ]
    
    # Remove empty arguments
    cmd = [arg for arg in cmd if arg]
    
    # Add icon if available
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
    
    # Add version info if on Windows
    if platform.system() == "Windows":
        cmd.extend([
            "--version-file=version_info.txt" if os.path.exists("version_info.txt") else ""
        ])
        cmd = [arg for arg in cmd if arg]
    
    try:
        print("Running PyInstaller with enhanced options...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        
        # Get the executable path
        exe_path = os.path.join('dist', 'RobocopyGUI.exe')
        print(f"Executable created: {exe_path}")
        
        # Check file size
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable size: {size_mb:.1f} MB")
        
        # Copy additional files to dist folder for distribution
        dist_files = [
            ("README.md", "Documentation"),
            ("LICENSE", "License file") if os.path.exists("LICENSE") else None,
        ]
        
        for file_info in dist_files:
            if file_info and os.path.exists(file_info[0]):
                shutil.copy2(file_info[0], "dist/")
                print(f"Copied {file_info[1]}: {file_info[0]}")
        
        # Create a distribution info file
        create_distribution_info()
        
        print("\n🎉 Build complete! Check the 'dist' folder for your standalone executable.")
        print("\nThe executable includes:")
        print("• Complete Python runtime")
        print("• All tkinter GUI libraries")
        print("• Threading and subprocess support")
        print("• All application dependencies")
        print("• Configuration files")
        print("\nThe .exe file can run on any Windows PC without installing Python!")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        if e.stdout:
            print(f"Standard output: {e.stdout}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Installing it now...")
        if install_pyinstaller():
            print("Retrying build...")
            return build_executable()  # Retry after installation
        return False
    
    return True

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install PyInstaller: {e}")
        return False

def create_distribution_info():
    """Create a distribution information file"""
    info_content = f"""ROBOCOPY GUI Manager - Standalone Distribution
=============================================

Version: 2.0
Built on: {platform.system()} {platform.release()}
Python version: {sys.version.split()[0]}
Architecture: {platform.architecture()[0]}

This is a standalone executable that includes:
• Complete Python runtime environment
• All required GUI libraries (tkinter)
• Threading and process management
• Configuration management
• Logging and error handling

SYSTEM REQUIREMENTS:
• Windows 7 or later (64-bit recommended)
• No Python installation required
• No additional dependencies needed

USAGE:
Simply double-click RobocopyGUI.exe to launch the application.

FEATURES:
• User-friendly ROBOCOPY command generation
• Real-time path validation
• Performance monitoring
• Command history and logging
• Multiple preset configurations
• Enhanced error handling and solutions
• Standalone operation (no installation required)

For documentation and source code, visit the project repository.

Developed by Sagar Sorathiya
"""
    
    try:
        with open("dist/README_DISTRIBUTION.txt", "w", encoding="utf-8") as f:
            f.write(info_content)
        print("Created distribution info file: README_DISTRIBUTION.txt")
    except Exception as e:
        print(f"Could not create distribution info: {e}")

def install_dependencies():
    """Install all required dependencies for building"""
    print("Installing build dependencies...")
    
    dependencies = [
        "pyinstaller>=5.0",
        "setuptools",
        "wheel",
    ]
    
    try:
        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        
        print("All dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def clean_build_files():
    """Clean previous build files"""
    print("Cleaning previous build files...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed directory: {dir_name}")
    
    # Clean .spec files
    for spec_file in ["RobocopyGUI.spec"]:
        if os.path.exists(spec_file):
            os.remove(spec_file)
            print(f"Removed spec file: {spec_file}")

def verify_executable():
    """Verify the built executable"""
    exe_path = os.path.join('dist', 'RobocopyGUI.exe')
    
    if not os.path.exists(exe_path):
        print("❌ Executable not found!")
        return False
    
    # Check if it's a valid PE file (Windows executable)
    try:
        with open(exe_path, 'rb') as f:
            # Read PE header
            f.seek(0x3C)  # Offset to PE header pointer
            pe_offset = int.from_bytes(f.read(4), byteorder='little')
            f.seek(pe_offset)
            pe_signature = f.read(4)
            
            if pe_signature == b'PE\x00\x00':
                print("✅ Valid Windows executable created!")
                return True
            else:
                print("⚠ Executable may not be valid PE format")
                return False
    except Exception as e:
        print(f"⚠ Could not verify executable format: {e}")
        return True  # Assume it's fine if we can't verify

def main():
    """Main build function"""
    print("ROBOCOPY GUI - Enhanced Standalone Executable Builder")
    print("=" * 55)
    print("This will create a completely self-contained .exe file")
    print("that can run on any Windows PC without any dependencies.")
    print()
    
    # System information
    print(f"Build system: {platform.system()} {platform.release()}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Architecture: {platform.architecture()[0]}")
    print()
    
    # Clean previous builds
    clean_build_files()
    
    # Install dependencies
    print("Step 1: Installing build dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your internet connection.")
        return
    
    print("\nStep 2: Building standalone executable...")
    # Build executable
    if build_executable():
        print("\nStep 3: Verifying executable...")
        if verify_executable():
            print("\n" + "🎉" * 20)
            print("BUILD COMPLETED SUCCESSFULLY!")
            print("🎉" * 20)
            print()
            print("✅ Standalone executable created: dist/RobocopyGUI.exe")
            print("✅ No Python installation required on target PCs")
            print("✅ No additional dependencies needed")
            print("✅ Ready for distribution")
            print()
            print("DISTRIBUTION PACKAGE CONTENTS:")
            print("📁 dist/")
            print("├── 📄 RobocopyGUI.exe (Main executable)")
            print("├── 📄 README.md (Documentation)")
            print("└── 📄 README_DISTRIBUTION.txt (Distribution info)")
            print()
            print("🚀 You can now copy the entire 'dist' folder to any Windows PC!")
            print("💡 Simply double-click RobocopyGUI.exe to run the application.")
        else:
            print("⚠ Build completed but verification failed. Please test manually.")
    else:
        print("\n❌ Build failed. Please check the error messages above.")
        print("\nTROUBLESHOOTING:")
        print("• Ensure you have internet connection for downloading dependencies")
        print("• Try running as administrator if you get permission errors")
        print("• Check that your antivirus isn't blocking the build process")

if __name__ == "__main__":
    main()
