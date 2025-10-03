#!/usr/bin/env python3
"""
Test script to verify the progress bar and performance labels are working correctly
"""

import os
import tempfile
import threading
import time
import tkinter as tk
from robocopy_gui import AdvancedRobocopyGUI

def test_gui_components():
    """Test if GUI components exist and can be updated"""
    
    print("Testing GUI component existence...")
    root = tk.Tk()
    app = AdvancedRobocopyGUI(root)
    
    # Test component existence
    components = {
        'progress': 'Progress bar',
        'progress_label': 'Progress label',
        'files_processed_label': 'Files processed label', 
        'dirs_processed_label': 'Directories label',
        'bytes_copied_label': 'Data copied label',
        'copy_speed_label': 'Speed label',
        'eta_label': 'ETA label',
        'elapsed_time_label': 'Elapsed time label'
    }
    
    print("\nComponent existence check:")
    for attr, name in components.items():
        exists = hasattr(app, attr)
        print(f"  {name}: {'✅ EXISTS' if exists else '❌ MISSING'}")
    
    # Test updating components
    print("\nTesting component updates...")
    
    # Initialize performance stats
    app.performance_stats = {
        'files_copied': 5,
        'dirs_copied': 2, 
        'bytes_copied': 123456,
        'total_files': 10,
        'speed_mbps': 15.5,
        'errors': 0
    }
    app.operation_start_time = time.time() - 30  # 30 seconds ago
    
    try:
        # Test the update method
        app.update_performance_display()
        print("  Performance display update: ✅ SUCCESS")
        
        # Test progress bar mode change
        if hasattr(app, 'progress'):
            app.progress.config(mode='determinate', maximum=100, value=50)
            print("  Progress bar mode change: ✅ SUCCESS")
        
        # Test label updates
        if hasattr(app, 'progress_label'):
            app.progress_label.config(text="Test: 50% (5/10 files)")
            print("  Progress label update: ✅ SUCCESS")
            
    except Exception as e:
        print(f"  Component update error: ❌ {e}")
    
    # Test parsing simulation
    print("\nTesting parsing with sample data...")
    app.performance_stats = {
        'files_copied': 0,
        'dirs_copied': 0,
        'bytes_copied': 0,
        'total_files': 0,
        'speed_mbps': 0.0,
        'errors': 0
    }
    
    test_lines = [
        "\t    New File  \t\t   50000\ttest_file_1.txt",
        "\t    New File  \t\t   60000\ttest_file_2.txt", 
        "\t  New Dir          1\tC:\\test\\subdir\\",
        "   Files :         8         8         0         0         0         0",
        "   Bytes :   880.0 k   880.0 k         0         0         0         0",
        "   Speed :               350.125 MegaBytes/min."
    ]
    
    for i, line in enumerate(test_lines):
        app.parse_robocopy_output(line)
        print(f"  Line {i+1} parsed - Files: {app.performance_stats['files_copied']}, "
              f"Bytes: {app.performance_stats['bytes_copied']}, "
              f"Speed: {app.performance_stats['speed_mbps']:.1f}")
    
    print(f"\nFinal parsed stats:")
    print(f"  Files: {app.performance_stats['files_copied']}/{app.performance_stats['total_files']}")
    print(f"  Directories: {app.performance_stats['dirs_copied']}")
    print(f"  Data: {app.performance_stats['bytes_copied']} bytes")
    print(f"  Speed: {app.performance_stats['speed_mbps']:.2f} MB/s")
    
    # Test final update
    try:
        app.update_performance_display()
        print(f"  Final display update: ✅ SUCCESS")
    except Exception as e:
        print(f"  Final display update: ❌ {e}")
    
    root.destroy()
    print("\nTest completed!")

if __name__ == "__main__":
    test_gui_components()
