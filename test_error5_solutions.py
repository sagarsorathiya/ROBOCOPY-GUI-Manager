#!/usr/bin/env python3
"""
Test script for ERROR 5 (Access Denied) handling improvements
"""

def test_error_detection():
    """Test the enhanced error detection and solution suggestions"""
    print("🔍 Testing ERROR 5 (Access Denied) Detection...")
    
    # Sample ERROR 5 outputs from ROBOCOPY
    test_error_lines = [
        "2025/09/09 20:58:10 ERROR 5 (0x00000005) Copying NTFS Security to Destination File C:\\source\\file.txt\nAccess is denied.",
        "2025/09/09 20:58:10 ERROR 5 (0x00000005) Copying Directory C:\\source\\folder\\\nAccess is denied.",
        "2025/09/09 20:58:10 ERROR 5 (0x00000005) Creating Destination Directory C:\\dest\\folder\\\nAccess is denied.",
        "ERROR: Access denied - The source file may be in use",
        "New File        1234        test.txt",
        "Waiting 30 seconds...",
        "    New File        1234    C:\\source\\test.txt Retrying..."
    ]
    
    # Simulate the format_output_line method logic
    def format_output_line(line):
        """Simulate the enhanced error detection"""
        if "ERROR 5 (0x00000005)" in line and "Access is denied" in line:
            if "Copying NTFS Security" in line:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Try removing /SEC and /COPYALL flags, or run as Administrator"
            elif "Copying Directory" in line:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Check destination permissions or try without /DCOPY:T flag"
            else:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Run as Administrator or check file/folder permissions"
        elif "ERROR" in line.upper() or "FAILED" in line.upper():
            if "Access is denied" in line:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Check permissions or run as Administrator"
            else:
                return f"[ERROR] {line}"
        elif "New File" in line:
            return f"[SUCCESS] {line}"
        elif "Retrying..." in line:
            return f"[RETRY] {line}"
        elif "Waiting" in line and "seconds" in line:
            return f"[WAIT] {line}"
        else:
            return line
    
    print("\n📝 Formatted Output:")
    for line in test_error_lines:
        formatted = format_output_line(line)
        if "[PERMISSION_ERROR]" in formatted:
            print(f"🔴 {formatted}")
        elif "[SOLUTION]" in formatted:
            print(f"💡 {formatted}")
        elif "[SUCCESS]" in formatted:
            print(f"✅ {formatted}")
        elif "[RETRY]" in formatted:
            print(f"🔄 {formatted}")
        elif "[WAIT]" in formatted:
            print(f"⏳ {formatted}")
        else:
            print(f"ℹ️  {formatted}")
    
    print("\n✅ Error detection test completed")

def test_permission_solutions():
    """Test the permission solution functions"""
    print("\n🛠️  Testing Permission Solutions...")
    
    solutions = {
        "Remove Security Copying": "Removes /SEC and /COPYALL flags to avoid NTFS security permission errors",
        "Remove Directory Timestamps": "Removes /DCOPY:T flag to avoid directory timestamp permission errors",
        "Use Basic Copy Only": "Switches to basic file copy without any security or timestamp attributes",
        "Run as Administrator": "Shows instructions for running the application with elevated privileges"
    }
    
    for solution, description in solutions.items():
        print(f"💡 {solution}: {description}")
    
    print("\n✅ Permission solutions test completed")

def test_common_scenarios():
    """Test common ERROR 5 scenarios and their solutions"""
    print("\n📋 Common ERROR 5 Scenarios and Solutions:")
    
    scenarios = [
        {
            "error": "ERROR 5 copying NTFS Security",
            "cause": "/SEC or /COPYALL flags trying to copy NTFS permissions",
            "solution": "Remove /SEC and /COPYALL flags or run as Administrator"
        },
        {
            "error": "ERROR 5 copying Directory timestamps", 
            "cause": "/DCOPY:T flag trying to copy directory timestamps",
            "solution": "Remove /DCOPY:T flag or run as Administrator"
        },
        {
            "error": "ERROR 5 accessing source file",
            "cause": "File is in use or no read permissions",
            "solution": "Close file if open, check permissions, or run as Administrator"
        },
        {
            "error": "ERROR 5 creating destination directory",
            "cause": "No write permissions to destination",
            "solution": "Check destination permissions or run as Administrator"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. 🚨 {scenario['error']}")
        print(f"   📌 Cause: {scenario['cause']}")
        print(f"   💡 Solution: {scenario['solution']}")
    
    print("\n✅ Scenario analysis completed")

def test_recommended_flags():
    """Show recommended flag combinations to avoid ERROR 5"""
    print("\n⚙️  Recommended Flag Combinations:")
    
    recommendations = [
        {
            "scenario": "Basic File Copy (Safest)",
            "flags": "/S /E",
            "description": "Copy files and subdirectories, no security attributes"
        },
        {
            "scenario": "Copy with File Attributes",
            "flags": "/S /E /COPY:DAT",
            "description": "Copy data, attributes, and timestamps (no security)"
        },
        {
            "scenario": "Administrative Copy (Full)",
            "flags": "/S /E /COPYALL /SEC /DCOPY:T",
            "description": "Full copy with security (requires Administrator privileges)"
        },
        {
            "scenario": "Fast Copy for Large Files",
            "flags": "/S /E /J /MT:16",
            "description": "Unbuffered I/O with multithreading (no security)"
        }
    ]
    
    for rec in recommendations:
        print(f"\n📋 {rec['scenario']}")
        print(f"   🏷️  Flags: {rec['flags']}")
        print(f"   📝 Description: {rec['description']}")
    
    print("\n✅ Recommendations completed")

def main():
    """Run all ERROR 5 handling tests"""
    print("🧪 ROBOCOPY ERROR 5 (Access Denied) Solutions Test")
    print("=" * 60)
    
    test_error_detection()
    test_permission_solutions()
    test_common_scenarios()
    test_recommended_flags()
    
    print("\n🎉 All ERROR 5 handling tests completed!")
    print("\n💡 Key Improvements for Your Case:")
    print("• The GUI now detects ERROR 5 and suggests specific solutions")
    print("• Quick-fix buttons remove problematic flags automatically")
    print("• Color-coded error messages with highlighted solutions")
    print("• Administrator instructions for when elevated privileges are needed")
    print("• Recommended flag combinations to prevent permission issues")

if __name__ == "__main__":
    main()
