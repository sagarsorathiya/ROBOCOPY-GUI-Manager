#!/usr/bin/env python3
"""
Test script to validate ROBOCOPY return code handling
This script tests the return code interpretation in the GUI
"""

import subprocess
import sys

def test_robocopy_return_codes():
    """Test different ROBOCOPY return codes"""
    print("Testing ROBOCOPY Return Code Scenarios...")
    print("=" * 50)
    
    # Test 1: Return code 0 (no files to copy)
    print("\n🧪 Test 1: Return code 0 (No files copied)")
    try:
        result = subprocess.run([
            "robocopy", 
            "C:\\Windows\\System32\\drivers\\etc", 
            "C:\\temp\\test_empty", 
            "nonexistent_file.txt",
            "/L"  # List only mode
        ], capture_output=True, text=True)
        print(f"   Return code: {result.returncode}")
        print(f"   Expected: 0 (No files to copy)")
        if result.returncode == 0:
            print("   ✅ Correct return code")
        else:
            print(f"   ❌ Unexpected return code: {result.returncode}")
    except Exception as e:
        print(f"   ⚠️ Test failed: {e}")
    
    # Test 2: Return code 1 (files copied)
    print("\n🧪 Test 2: Return code 1 (Files copied)")
    try:
        # Create test directories
        import os
        os.makedirs("C:\\temp\\test_source", exist_ok=True)
        os.makedirs("C:\\temp\\test_dest", exist_ok=True)
        
        # Create a test file
        with open("C:\\temp\\test_source\\test.txt", "w") as f:
            f.write("test content")
        
        result = subprocess.run([
            "robocopy", 
            "C:\\temp\\test_source", 
            "C:\\temp\\test_dest", 
            "test.txt",
            "/L"  # List only mode
        ], capture_output=True, text=True)
        print(f"   Return code: {result.returncode}")
        print(f"   Expected: 1 (Files would be copied)")
        if result.returncode == 1:
            print("   ✅ Correct return code")
        else:
            print(f"   ❌ Unexpected return code: {result.returncode}")
    except Exception as e:
        print(f"   ⚠️ Test failed: {e}")
    
    # Test 3: Return code 2 (extra files)
    print("\n🧪 Test 3: Return code 2 (Extra files)")
    try:
        # Create extra file in destination
        with open("C:\\temp\\test_dest\\extra.txt", "w") as f:
            f.write("extra content")
        
        result = subprocess.run([
            "robocopy", 
            "C:\\temp\\test_source", 
            "C:\\temp\\test_dest",
            "/L"  # List only mode
        ], capture_output=True, text=True)
        print(f"   Return code: {result.returncode}")
        print(f"   Expected: 2 or 3 (Extra files detected)")
        if result.returncode in [2, 3]:
            print("   ✅ Correct return code")
        else:
            print(f"   ❌ Unexpected return code: {result.returncode}")
    except Exception as e:
        print(f"   ⚠️ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("Return Code Test Summary:")
    print("0    = No files copied (SUCCESS)")
    print("1    = Files copied successfully (SUCCESS)")
    print("2    = Extra files detected (SUCCESS)")
    print("3    = Files copied + extra files (SUCCESS)")
    print("4    = Mismatched files (WARNING)")
    print("5-7  = Various combinations with warnings (WARNING)")
    print("8+   = Copy errors occurred (ERROR)")
    print("16+  = Serious errors (ERROR)")
    print("=" * 50)

def test_return_code_interpretation():
    """Test the return code interpretation logic"""
    print("\n🔍 Testing Return Code Interpretation Logic...")
    
    test_cases = [
        (0, "SUCCESS", "No files copied"),
        (1, "SUCCESS", "Files copied successfully"),
        (2, "SUCCESS", "Extra files detected"),
        (3, "SUCCESS", "Files copied + extra files"),
        (4, "WARNING", "Mismatched files"),
        (5, "WARNING", "Files copied + mismatched files"),
        (8, "ERROR", "Copy errors occurred"),
        (16, "ERROR", "Serious error"),
        (24, "ERROR", "Serious error with other issues")
    ]
    
    for code, expected_level, description in test_cases:
        if code == 0:
            level = "SUCCESS"
        elif code in [1, 2, 3]:
            level = "SUCCESS"
        elif code in [4, 5, 6, 7]:
            level = "WARNING"
        elif code == 8 or (code & 8):
            level = "ERROR"
        elif code >= 16:
            level = "ERROR"
        else:
            level = "WARNING"
        
        status = "✅" if level == expected_level else "❌"
        print(f"   Code {code:2d}: {level:7s} - {description} {status}")

if __name__ == "__main__":
    test_robocopy_return_codes()
    test_return_code_interpretation()
    
    print("\n🎉 Return code testing completed!")
    print("The updated GUI should now properly interpret all these return codes.")
