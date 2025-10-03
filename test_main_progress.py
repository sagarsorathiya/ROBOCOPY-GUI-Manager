#!/usr/bin/env python3
"""
Test script to verify the main progress bar components in the Output & Progress section
"""

import tkinter as tk
from robocopy_gui import AdvancedRobocopyGUI

def test_main_progress_components():
    """Test if main progress components exist and can be updated"""
    
    print("Testing main progress bar components...")
    root = tk.Tk()
    app = AdvancedRobocopyGUI(root)
    
    # Test main progress components existence
    main_components = {
        'progress': 'Main progress bar (Output & Progress section)',
        'progress_percent': 'Main progress percentage label',
        'progress_label': 'Main progress status label', 
        'time_label': 'Main elapsed time label'
    }
    
    print("\nMain Progress Component existence check:")
    for attr, name in main_components.items():
        exists = hasattr(app, attr)
        print(f"  {name}: {'✅ EXISTS' if exists else '❌ MISSING'}")
    
    # Test updating main progress components
    print("\nTesting main progress component updates...")
    
    try:
        # Test main progress bar update
        if hasattr(app, 'progress'):
            app.progress.config(mode='determinate', maximum=100, value=75)
            print("  Main progress bar update: ✅ SUCCESS")
        
        # Test main progress percentage update
        if hasattr(app, 'progress_percent'):
            app.progress_percent.config(text="75%")
            print("  Main progress percentage update: ✅ SUCCESS")
        
        # Test main progress label update
        if hasattr(app, 'progress_label'):
            app.progress_label.config(text="Processing: 75% (3/4 files)")
            print("  Main progress label update: ✅ SUCCESS")
            
        # Test main elapsed time update
        if hasattr(app, 'time_label'):
            app.time_label.config(text="Elapsed: 00:01:30")
            print("  Main elapsed time update: ✅ SUCCESS")
            
    except Exception as e:
        print(f"  Main component update error: ❌ {e}")
    
    # Test the complete update flow
    print("\nTesting complete progress update flow...")
    
    # Simulate performance stats
    app.performance_stats = {
        'files_copied': 3,
        'dirs_copied': 1,
        'bytes_copied': 750000,  # 750 KB
        'total_files': 4,
        'speed_mbps': 12.5,
        'errors': 0
    }
    app.operation_start_time = __import__('time').time() - 90  # 90 seconds ago
    
    try:
        # Test the complete update method
        app.update_performance_display()
        print("  Complete performance update: ✅ SUCCESS")
        
        # Test parsing that should update main progress
        test_line = "   Files :         4         3         0         0         0         0"
        app.parse_robocopy_output(test_line)
        print("  Parsing with progress update: ✅ SUCCESS")
        
    except Exception as e:
        print(f"  Complete update error: ❌ {e}")
    
    root.destroy()
    print("\nMain progress component test completed!")

if __name__ == "__main__":
    test_main_progress_components()
