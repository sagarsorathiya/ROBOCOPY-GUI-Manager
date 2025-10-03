#!/usr/bin/env python3
"""
Debug script to test ROBOCOPY output parsing and see actual output format
"""

import subprocess
import tempfile
import os
import shutil

def test_robocopy_output():
    """Create a test scenario to see actual ROBOCOPY output"""
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = os.path.join(temp_dir, "source")
        dest_dir = os.path.join(temp_dir, "dest")
        
        os.makedirs(source_dir)
        os.makedirs(dest_dir)
        
        # Create some test files
        for i in range(5):
            test_file = os.path.join(source_dir, f"test_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Test content for file {i} " * 1000)  # Make files reasonably sized
        
        # Create a subdirectory with files
        sub_dir = os.path.join(source_dir, "subdir")
        os.makedirs(sub_dir)
        for i in range(3):
            test_file = os.path.join(sub_dir, f"sub_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Sub directory content for file {i} " * 500)
        
        # Run ROBOCOPY with verbose output to see what we get
        command = f'robocopy "{source_dir}" "{dest_dir}" /E /V /NP /TEE /R:0 /W:0'
        
        print(f"Testing command: {command}")
        print("=" * 50)
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                bufsize=1,
                universal_newlines=True
            )
            
            line_count = 0
            for line in iter(process.stdout.readline, ''):
                if line:
                    line_count += 1
                    clean_line = line.rstrip('\n\r')
                    print(f"Line {line_count:3d}: {repr(clean_line)}")
                    
                    # Test our parsing logic
                    if "New File" in line or "Newer" in line:
                        print(f"    >>> DETECTED FILE COPY: {clean_line}")
                    elif "New Dir" in line:
                        print(f"    >>> DETECTED DIR CREATE: {clean_line}")
                    elif "Files :" in line:
                        print(f"    >>> DETECTED SUMMARY: {clean_line}")
                    elif "%" in line and any(char.isdigit() for char in line):
                        print(f"    >>> DETECTED PROGRESS: {clean_line}")
            
            return_code = process.wait()
            print(f"\nROBOCOPY Return Code: {return_code}")
            
        except Exception as e:
            print(f"Error running test: {e}")

if __name__ == "__main__":
    test_robocopy_output()
