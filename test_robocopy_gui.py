#!/usr/bin/env python3
"""
Test script for ROBOCOPY GUI functionality
"""

import sys
import os
sys.path.append('.')

from robocopy_utils import RobocopyValidator, ConfigManager

def test_validator():
    """Test the validation functions"""
    print("Testing ROBOCOPY Validator...")
    validator = RobocopyValidator()
    
    # Test path validation
    print("\n1. Path Validation Tests:")
    valid, error = validator.validate_path("C:\\Windows", "directory")
    print(f"   C:\\Windows validation: {valid} - {error}")
    
    valid, error = validator.validate_path("nonexistent_path", "directory")
    print(f"   Nonexistent path validation: {valid} - {error}")
    
    # Test numeric validation
    print("\n2. Numeric Validation Tests:")
    valid, error, value = validator.validate_numeric_input("5", "Test Number", 1, 10)
    print(f"   Valid number (5): {valid} - {error} - Value: {value}")
    
    valid, error, value = validator.validate_numeric_input("abc", "Test Number", 1, 10)
    print(f"   Invalid number (abc): {valid} - {error} - Value: {value}")
    
    # Test options validation
    print("\n3. Options Validation Tests:")
    test_options = {
        'source_path': 'C:\\Windows',
        'dest_path': 'C:\\Temp',
        'mirror_mode': True,
        'copy_subdirs': True,  # Should generate warning
        'retries': '3',
        'wait_time': '30',
        'threads': '8'
    }
    
    is_valid, warnings, errors = validator.validate_robocopy_options(test_options)
    print(f"   Options validation: {is_valid}")
    print(f"   Warnings: {warnings}")
    print(f"   Errors: {errors}")
    
    # Test command generation
    print("\n4. Command Generation Test:")
    command, safe, warnings, errors = validator.generate_safe_command(test_options)
    print(f"   Generated command: {command}")
    print(f"   Is safe: {safe}")
    print(f"   Warnings: {warnings}")
    print(f"   Errors: {errors}")

def test_config_manager():
    """Test configuration management"""
    print("\n\nTesting Configuration Manager...")
    config_mgr = ConfigManager("test_config.json")
    
    # Test default config
    default_config = config_mgr.get_default_config()
    print(f"Default config keys: {list(default_config.keys())}")
    
    # Test config validation
    test_config = {
        'source_path': 'C:\\Test',
        'mirror_mode': 'true',  # Wrong type, should be fixed
        'retries': 5  # Wrong type, should be fixed
    }
    
    validated_config = config_mgr.validate_config(test_config)
    print(f"Validated config: {validated_config}")

def main():
    """Run all tests"""
    print("ROBOCOPY GUI - Testing Utilities")
    print("=" * 40)
    
    try:
        test_validator()
        test_config_manager()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
