#!/usr/bin/env python3
"""
Test script to validate ROBOCOPY parameter generation
This script tests the parameter validation fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robocopy_gui import AdvancedRobocopyGUI
import tkinter as tk

def test_parameter_validation():
    """Test the parameter validation functionality"""
    print("Testing ROBOCOPY parameter validation...")
    
    # Create a test GUI instance
    root = tk.Tk()
    root.withdraw()  # Hide the window for testing
    
    app = AdvancedRobocopyGUI(root)
    
    # Test 1: Valid numeric inputs
    print("\nTest 1: Valid numeric inputs")
    app.retries.set("3")
    app.wait_time.set("30")
    app.threads.set("8")
    
    # Set source and destination
    app.source_path.set("C:\\temp\\source")
    app.dest_path.set("C:\\temp\\dest")
    
    # Generate command
    app.generate_command()
    command = app.command_text.get(1.0, tk.END).strip()
    print(f"Generated command: {command}")
    
    # Check if parameters are properly formatted with colon syntax
    if "/R:3" in command and "/W:30" in command and "/MT:8" in command:
        print("✅ Test 1 PASSED: Valid parameters generated correctly")
    else:
        print("❌ Test 1 FAILED: Parameters not generated correctly")
        print(f"  Expected: '/R:3', '/W:30', '/MT:8'")
        print(f"  Found in command: {'/R:3' in command}, {'/W:30' in command}, {'/MT:8' in command}")
    
    # Test 2: Empty numeric inputs
    print("\nTest 2: Empty numeric inputs")
    app.retries.set("")
    app.wait_time.set("")
    app.threads.set("")
    
    app.generate_command()
    command = app.command_text.get(1.0, tk.END).strip()
    print(f"Generated command: {command}")
    
    # Check if empty parameters are handled correctly (should use defaults or not include)
    if "/R:" not in command and "/W:" not in command and "/MT:" not in command:
        print("✅ Test 2 PASSED: Empty parameters handled correctly")
    else:
        print("❌ Test 2 FAILED: Empty parameters not handled correctly")
    
    # Test 3: Invalid numeric inputs
    print("\nTest 3: Invalid numeric inputs")
    app.retries.set("abc")
    app.wait_time.set("xyz")
    app.threads.set("invalid")
    
    app.generate_command()
    command = app.command_text.get(1.0, tk.END).strip()
    print(f"Generated command: {command}")
    
    # Check if invalid parameters are handled correctly
    if "/R:abc" not in command and "/W:xyz" not in command and "/MT:invalid" not in command:
        print("✅ Test 3 PASSED: Invalid parameters handled correctly")
    else:
        print("❌ Test 3 FAILED: Invalid parameters not handled correctly")
    
    # Test 4: Test validation function
    print("\nTest 4: Testing validate_number function")
    valid_result = app.validate_number("123")
    invalid_result = app.validate_number("abc")
    empty_result = app.validate_number("")
    
    print(f"  validate_number('123') = {valid_result} (should be True)")
    print(f"  validate_number('abc') = {invalid_result} (should be False)")
    print(f"  validate_number('') = {empty_result} (should be True)")
    
    if valid_result and not invalid_result and empty_result:
        print("✅ Test 4 PASSED: validate_number function works correctly")
    else:
        print("❌ Test 4 FAILED: validate_number function not working correctly")
    
    root.destroy()
    print("\n🎉 Parameter validation testing completed!")

if __name__ == "__main__":
    test_parameter_validation()
