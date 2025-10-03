#!/usr/bin/env python3
"""
Live test script to verify performance monitoring during an actual ROBOCOPY operation
"""

import os
import tempfile
import time
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_test_scenario():
    """Create a realistic test scenario with multiple files and directories"""
    
    temp_dir = tempfile.mkdtemp()
    source_dir = os.path.join(temp_dir, "robocopy_test_source")
    dest_dir = os.path.join(temp_dir, "robocopy_test_dest")
    
    os.makedirs(source_dir)
    os.makedirs(dest_dir)
    
    print(f"Created test directories:")
    print(f"  Source: {source_dir}")
    print(f"  Destination: {dest_dir}")
    
    # Create various sizes of files to make the operation take some time
    file_sizes = [1024*10, 1024*50, 1024*100, 1024*200, 1024*500]  # Various sizes
    
    print(f"\nCreating test files...")
    for i, size in enumerate(file_sizes):
        for j in range(3):  # 3 files per size category
            filename = f"testfile_{size//1024}kb_{j}.txt"
            filepath = os.path.join(source_dir, filename)
            
            with open(filepath, 'w') as f:
                # Write content to achieve the target size
                content = f"Test file {i}-{j} content. " * (size // 25)
                f.write(content)
            
            print(f"  Created: {filename} ({size//1024} KB)")
    
    # Create subdirectories with files
    for subdir_idx in range(2):
        subdir = os.path.join(source_dir, f"subdir_{subdir_idx}")
        os.makedirs(subdir)
        
        for i in range(5):
            filename = f"sub_file_{i}.txt"
            filepath = os.path.join(subdir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Subdirectory file content {subdir_idx}-{i}. " * 100)
        
        print(f"  Created subdirectory: subdir_{subdir_idx} with 5 files")
    
    total_files = len(file_sizes) * 3 + 2 * 5  # Main files + subdir files
    print(f"\nTotal files created: {total_files}")
    
    return source_dir, dest_dir, temp_dir

def run_monitored_robocopy_test():
    """Run a ROBOCOPY operation with the actual GUI to test monitoring"""
    
    print("🚀 Starting Live ROBOCOPY Performance Monitoring Test")
    print("=" * 60)
    
    # Create test scenario
    source_dir, dest_dir, temp_dir = create_test_scenario()
    
    try:
        # Import and start the GUI
        import tkinter as tk
        from robocopy_gui import AdvancedRobocopyGUI
        
        print(f"\n📱 Starting ROBOCOPY GUI...")
        root = tk.Tk()
        app = AdvancedRobocopyGUI(root)
        
        # Configure the GUI for our test
        app.source_path.set(source_dir)
        app.dest_path.set(dest_dir)
        
        # Use a simple copy operation with verbose output
        if hasattr(app, 'copy_files_var'):
            app.copy_files_var.set(True)
        if hasattr(app, 'copy_subdirs_var'):
            app.copy_subdirs_var.set(True)
        if hasattr(app, 'verbose_var'):
            app.verbose_var.set(True)
        
        # Generate the command
        app.generate_command()
        command = app.current_command
        
        print(f"\n📋 Generated command:")
        print(f"  {command}")
        
        print(f"\n⏰ Starting ROBOCOPY operation...")
        print(f"Monitor the GUI window for real-time progress updates!")
        print(f"Look for:")
        print(f"  - Progress bar moving from 0% to 100%")
        print(f"  - Files Processed count increasing")
        print(f"  - Data Copied amount growing")
        print(f"  - Speed measurements")
        print(f"  - ETA calculations")
        
        # Start the operation
        app.execute_command()
        
        # Keep the GUI running for observation
        print(f"\n👀 GUI is now running. Watch the performance monitoring!")
        print(f"Close the GUI window when the operation completes.")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        logging.exception("Test error details:")
    
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up test directory: {temp_dir}")
        except:
            print(f"\n⚠️  Manual cleanup needed: {temp_dir}")

if __name__ == "__main__":
    run_monitored_robocopy_test()
