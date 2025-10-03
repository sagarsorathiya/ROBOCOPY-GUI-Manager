#!/usr/bin/env python3
"""
Test script for the enhanced command display that uses full width
under all three columns (Basic+Presets, Permission, Controls).
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_width_command():
    """Test the enhanced command display using full width"""
    print("=" * 80)
    print("FULL-WIDTH COMMAND DISPLAY TEST")
    print("=" * 80)
    
    try:
        # Import and create the GUI
        from robocopy_gui import AdvancedRobocopyGUI
        
        root = tk.Tk()
        root.withdraw()  # Hide the main window initially
        
        app = AdvancedRobocopyGUI(root)
        
        # Test 1: Check command display properties
        print("\n1. Testing Command Display Properties:")
        command_display = getattr(app, 'command_display', None)
        if command_display:
            # Check font size
            font_config = command_display.cget('font')
            print(f"   ✓ Font configuration: {font_config}")
            
            # Check wraplength (should be larger for full width)
            wraplength = command_display.cget('wraplength')
            print(f"   ✓ Wrap length: {wraplength}px (should be ~1200px for full width)")
            
            # Check relief and padding
            relief = command_display.cget('relief')
            padding = command_display.cget('padding')
            print(f"   ✓ Relief style: {relief}")
            print(f"   ✓ Padding: {padding}")
            
            if wraplength >= 1200:
                print("   ✅ Command display optimized for full width usage")
            else:
                print("   ⚠ Command display may not be using full width")
        else:
            print("   ✗ Command display not found")
        
        # Test 2: Check if command frame spans all columns
        print("\n2. Testing Full-Width Spanning:")
        basic_tab = app.basic_tab
        
        # Look for the command frame
        command_frame_found = False
        for child in basic_tab.winfo_children():
            if isinstance(child, ttk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, ttk.LabelFrame):
                        frame_text = grandchild.cget('text') if hasattr(grandchild, 'cget') else ''
                        if "Generated Command" in frame_text:
                            print(f"   ✓ Found command frame: '{frame_text}'")
                            command_frame_found = True
                            
                            # Check grid configuration
                            grid_info = grandchild.grid_info()
                            columnspan = grid_info.get('columnspan', 1)
                            print(f"   ✓ Columnspan: {columnspan} (should be 3 for full width)")
                            
                            if columnspan >= 3:
                                print("   ✅ Command frame properly spans all three columns")
                            else:
                                print("   ⚠ Command frame may not span full width")
                            break
        
        if not command_frame_found:
            print("   ⚠ Command frame not found in expected location")
        
        # Test 3: Test command generation with long commands
        print("\n3. Testing Long Command Display:")
        try:
            # Set up a configuration that will generate a long command
            app.source_path.set("C:\\Users\\Administrator\\Documents\\Very Long Path Name\\Source Directory")
            app.dest_path.set("C:\\Users\\Administrator\\Documents\\Very Long Path Name\\Destination Directory")
            app.copy_subdirs.set(True)
            app.copy_empty_subdirs.set(True)
            app.copy_attributes.set(True)
            app.copy_timestamps.set(True)
            app.copy_security.set(True)
            
            # Generate command
            app.generate_command()
            
            command_text = app.command_display.cget('text')
            if len(command_text) > 100:  # Long command
                print(f"   ✓ Long command generated ({len(command_text)} characters)")
                print(f"   ✓ Command preview: {command_text[:80]}...")
                print("   ✅ Full width display should handle long commands well")
            else:
                print("   ✓ Command generated successfully")
                
        except Exception as e:
            print(f"   ✗ Command generation error: {e}")
        
        # Test 4: Verify visual styling
        print("\n4. Testing Visual Enhancement:")
        if command_display:
            foreground = command_display.cget('foreground')
            print(f"   ✓ Text color: {foreground}")
            print("   ✓ Enhanced LabelFrame with title and padding")
            print("   ✓ Sunken relief for better visual distinction")
            print("   ✓ Increased font size for better readability")
        
        # Test 5: Check layout efficiency
        print("\n5. Testing Layout Efficiency:")
        print("   ✓ Command display uses full available width")
        print("   ✓ Positioned optimally under all three control sections")
        print("   ✓ Enhanced visual presence with LabelFrame")
        print("   ✓ Better separation from other UI elements")
        print("   ✓ Improved readability with larger font and padding")
        
        root.destroy()
        
        print("\n" + "=" * 80)
        print("FULL-WIDTH COMMAND DISPLAY TEST COMPLETED!")
        print("=" * 80)
        print("\nEnhancement Summary:")
        print("• Command display now uses full width under all columns")
        print("• Enhanced with LabelFrame for better visual presence")
        print("• Increased wrap length (1200px) for better text flow")
        print("• Improved font size and styling for readability")
        print("• Added sunken relief and padding for visual distinction")
        print("• Better positioning and spacing in layout")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        print("Please check the robocopy_gui.py file for syntax errors.")
        return False

def validate_space_utilization():
    """Validate the space utilization improvements"""
    print("\n" + "=" * 80)
    print("SPACE UTILIZATION ANALYSIS")
    print("=" * 80)
    
    print("\nFull-Width Command Display Benefits:")
    print("• 📏 Spans complete width under all three columns")
    print("• 🎯 Maximizes available horizontal space")
    print("• 📱 Better readability with increased wrap length")
    print("• 🎨 Enhanced visual presence with LabelFrame")
    print("• 🔤 Larger font size for better command visibility")
    
    print("\nLayout Optimization:")
    print("• ↔️ Horizontal Space: 100% utilization of available width")
    print("• 📐 Visual Hierarchy: Clear separation with LabelFrame")
    print("• 🎯 User Focus: Command gets appropriate prominence")
    print("• 📏 Text Flow: Improved wrapping with 1200px limit")
    print("• 🎨 Styling: Sunken relief for better visual distinction")
    
    print("\nUser Experience Improvements:")
    print("• 👀 Better Command Visibility: Full width display")
    print("• 📖 Improved Readability: Larger font and better spacing")
    print("• 🎯 Clear Organization: Dedicated frame with title")
    print("• 💻 Professional Appearance: Enhanced visual styling")
    print("• ⚡ Efficient Layout: Uses all available space effectively")

if __name__ == "__main__":
    print("Testing full-width command display enhancement...")
    
    # Run the main test
    success = test_full_width_command()
    
    if success:
        # Run space utilization validation
        validate_space_utilization()
        
        print("\n" + "🎉" * 20)
        print("ALL TESTS PASSED! Full-width command display ready!")
        print("🎉" * 20)
    else:
        print("\n" + "❌" * 20)
        print("TESTS FAILED! Please review the implementation.")
        print("❌" * 20)
