#!/usr/bin/env python3
"""
Comprehensive test to verify both main and detailed progress areas are working
"""

import tkinter as tk
import time
from robocopy_gui import AdvancedRobocopyGUI

def test_both_progress_areas():
    """Test both main progress (Output & Progress) and detailed metrics areas"""
    
    print("Testing both progress areas integration...")
    root = tk.Tk()
    app = AdvancedRobocopyGUI(root)
    
    # Components in main "Output & Progress" section
    main_components = [
        'progress',           # Main progress bar
        'progress_percent',   # Main percentage label
        'progress_label',     # Main status label
        'time_label'          # Main elapsed time
    ]
    
    # Components in "Real-time Performance Metrics" section
    detailed_components = [
        'files_processed_label',
        'dirs_processed_label', 
        'bytes_copied_label',
        'copy_speed_label',
        'eta_label',
        'elapsed_time_label'
    ]
    
    print("\n=== Component Verification ===")
    print("Main Progress Components (Output & Progress):")
    for comp in main_components:
        exists = hasattr(app, comp)
        print(f"  {comp}: {'✅' if exists else '❌'}")
    
    print("\nDetailed Progress Components (Real-time Performance Metrics):")
    for comp in detailed_components:
        exists = hasattr(app, comp)
        print(f"  {comp}: {'✅' if exists else '❌'}")
    
    # Simulate a real operation scenario
    print(f"\n=== Simulation Test ===")
    
    # Initialize operation
    app.operation_start_time = time.time()
    app.performance_stats = {
        'files_copied': 0,
        'dirs_copied': 0,
        'bytes_copied': 0,
        'total_files': 0,
        'speed_mbps': 0.0,
        'errors': 0
    }
    
    # Simulate ROBOCOPY output lines
    test_lines = [
        "\t    New File  \t\t   25600\ttest_file_1.txt",
        "\t    New File  \t\t   51200\ttest_file_2.txt",
        "\t  New Dir          1\tC:\\test\\subdir\\",
        "\t    New File  \t\t   30720\ttest_file_3.txt",
        "   Files :         4         3         0         0         0         0",
        "   Bytes :   107.5 k   107.5 k         0         0         0         0",
        "   Speed :               450.250 MegaBytes/min."
    ]
    
    print("Processing simulated ROBOCOPY output:")
    for i, line in enumerate(test_lines):
        print(f"  Step {i+1}: Parsing line...")
        app.parse_robocopy_output(line)
        
        # Check main progress after each line
        if hasattr(app, 'progress'):
            current_value = app.progress['value']
            print(f"    Main progress bar: {current_value}%")
        
        if hasattr(app, 'progress_percent'):
            current_text = app.progress_percent['text']
            print(f"    Main percentage: {current_text}")
        
        time.sleep(0.1)  # Small delay to simulate real processing
    
    # Final update test
    print(f"\nTesting final performance display update...")
    app.update_performance_display()
    
    # Display final results
    print(f"\n=== Final Results ===")
    stats = app.performance_stats
    print(f"Performance Stats:")
    print(f"  Files: {stats['files_copied']}/{stats['total_files']}")
    print(f"  Directories: {stats['dirs_copied']}")
    print(f"  Bytes: {stats['bytes_copied']}")
    print(f"  Speed: {stats['speed_mbps']:.1f} MB/s")
    
    if hasattr(app, 'progress'):
        final_progress = app.progress['value']
        print(f"Main Progress Bar: {final_progress}%")
    
    if hasattr(app, 'progress_percent'):
        final_percentage = app.progress_percent['text']
        print(f"Main Percentage Label: {final_percentage}")
    
    if hasattr(app, 'progress_label'):
        final_label = app.progress_label['text']
        print(f"Main Progress Label: {final_label}")
    
    root.destroy()
    print(f"\n✅ Both progress areas test completed!")

if __name__ == "__main__":
    test_both_progress_areas()
