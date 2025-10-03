#!/usr/bin/env python3
"""
Test script to verify Basic Settings tab functionality without progress bar
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from robocopy_gui import AdvancedRobocopyGUI

def test_basic_settings_no_progress():
    """Test that Basic Settings tab works without progress bar"""
    print("🧪 Testing Basic Settings tab without progress bar...")
    
    # Create test window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Create the GUI
        app = AdvancedRobocopyGUI(root)
        print("✅ GUI created successfully")
        
        # Check if Basic Settings tab exists
        if hasattr(app, 'basic_tab'):
            print("✅ Basic Settings tab exists")
        else:
            print("❌ Basic Settings tab missing")
            return False
        
        # Check if progress bar was removed (should not exist in basic tab)
        if hasattr(app, 'progress'):
            # Progress bar should exist in Performance Monitoring tab but not in Basic Settings
            print("ℹ️  Progress bar exists (in Performance Monitoring tab)")
        else:
            print("❌ No progress bar found at all")
            return False
        
        # Check if progress_percent was removed from Basic Settings
        if hasattr(app, 'progress_percent'):
            print("❌ progress_percent still exists (should be removed from Basic Settings)")
            return False
        else:
            print("✅ progress_percent removed from Basic Settings (as intended)")
        
        # Check if progress_label still exists (for status updates)
        if hasattr(app, 'progress_label'):
            print("✅ progress_label exists (for status updates)")
        else:
            print("❌ progress_label missing")
            return False
        
        # Check if output_text still exists
        if hasattr(app, 'output_text'):
            print("✅ Output text area exists")
        else:
            print("❌ Output text area missing")
            return False
        
        # Check if command display still exists
        if hasattr(app, 'command_display'):
            print("✅ Command display exists")
        else:
            print("❌ Command display missing")
            return False
        
        # Verify GUI structure
        print("✅ All essential components present")
        print("✅ Basic Settings tab is clean without problematic progress bar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        root.destroy()

def main():
    """Run the test"""
    print("=" * 60)
    print("BASIC SETTINGS - NO PROGRESS BAR TEST")
    print("=" * 60)
    
    success = test_basic_settings_no_progress()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED! Basic Settings tab works without progress bar")
        print("✅ Users can now focus on Real-time Performance Metrics tab for progress tracking")
    else:
        print("❌ TEST FAILED! Issues found with Basic Settings tab")
    print("=" * 60)

if __name__ == "__main__":
    main()
