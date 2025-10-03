#!/usr/bin/env python3
"""
Quick test script to verify performance monitoring works
"""

import os
import tempfile
import threading
import time
from robocopy_gui import AdvancedRobocopyGUI
import tkinter as tk

def test_performance_monitoring():
    """Test the performance monitoring with a real ROBOCOPY operation"""
    
    print("Creating test GUI...")
    root = tk.Tk()
    app = AdvancedRobocopyGUI(root)
    
    # Create test directories
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "test_source")
        dest_dir = os.path.join(temp_dir, "test_dest")
        
        os.makedirs(source_dir)
        os.makedirs(dest_dir)
        
        # Create test files
        for i in range(10):
            test_file = os.path.join(source_dir, f"test_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Test content for file {i} " * 1000)
        
        # Set up the GUI for testing
        app.source_path.set(source_dir)
        app.dest_path.set(dest_dir)
        
        # Generate command
        app.generate_command()
        command = app.current_command
        
        print(f"Testing command: {command}")
        
        # Initialize performance stats
        app.performance_stats = {
            'files_copied': 0,
            'dirs_copied': 0,
            'bytes_copied': 0,
            'total_files': 0,
            'speed_mbps': 0.0,
            'errors': 0
        }
        
        # Test parsing with actual ROBOCOPY output format
        test_lines = [
            "\t    New File  \t\t   24000\ttest_file_0.txt",
            "\t    New File  \t\t   24000\ttest_file_1.txt", 
            "\t  New Dir          3\tC:\\temp\\subdir\\",
            "   Files :        10        10         0         0         0         0",
            "   Bytes :   240.0 k   240.0 k         0         0         0         0",
            "   Speed :               606.179 MegaBytes/min."
        ]
        
        print("\nTesting output parsing:")
        for line in test_lines:
            print(f"Parsing: {line}")
            app.parse_robocopy_output(line)
            print(f"Stats after parsing: {app.performance_stats}")
        
        print(f"\nFinal performance stats:")
        print(f"Files copied: {app.performance_stats['files_copied']}")
        print(f"Dirs copied: {app.performance_stats['dirs_copied']}")
        print(f"Bytes copied: {app.performance_stats['bytes_copied']}")
        print(f"Total files: {app.performance_stats['total_files']}")
        print(f"Speed: {app.performance_stats['speed_mbps']:.2f} MB/s")
    
    root.destroy()
    print("Test completed!")

if __name__ == "__main__":
    test_performance_monitoring()
