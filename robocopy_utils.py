#!/usr/bin/env python3
"""
Configuration and validation utilities for ROBOCOPY GUI
"""

import os
import re
import logging

class RobocopyValidator:
    """Validates ROBOCOPY parameters and paths"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_path(self, path, path_type="directory"):
        """
        Validate if a path exists and is accessible
        
        Args:
            path (str): Path to validate
            path_type (str): Type of path ('directory' or 'file')
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not path:
            return False, f"{path_type.capitalize()} path cannot be empty"
        
        if not os.path.exists(path):
            return False, f"{path_type.capitalize()} does not exist: {path}"
        
        if path_type == "directory" and not os.path.isdir(path):
            return False, f"Path is not a directory: {path}"
        
        if path_type == "file" and not os.path.isfile(path):
            return False, f"Path is not a file: {path}"
        
        # Check if path is accessible
        try:
            if path_type == "directory":
                os.listdir(path)
            else:
                with open(path, 'r'):
                    pass
        except PermissionError:
            return False, f"Permission denied accessing: {path}"
        except Exception as e:
            return False, f"Error accessing {path}: {str(e)}"
        
        return True, ""
    
    def validate_numeric_input(self, value, field_name, min_val=0, max_val=None):
        """
        Validate numeric input fields
        
        Args:
            value (str): Value to validate
            field_name (str): Name of the field for error messages
            min_val (int): Minimum allowed value
            max_val (int): Maximum allowed value
        
        Returns:
            tuple: (is_valid, error_message, converted_value)
        """
        if not value:
            return False, f"{field_name} cannot be empty", None
        
        try:
            num_val = int(value)
        except ValueError:
            return False, f"{field_name} must be a number", None
        
        if num_val < min_val:
            return False, f"{field_name} must be at least {min_val}", None
        
        if max_val is not None and num_val > max_val:
            return False, f"{field_name} cannot exceed {max_val}", None
        
        return True, "", num_val
    
    def validate_robocopy_options(self, options_dict):
        """
        Validate ROBOCOPY options for conflicts and correctness
        
        Args:
            options_dict (dict): Dictionary of ROBOCOPY options
        
        Returns:
            tuple: (is_valid, warnings_list, errors_list)
        """
        warnings = []
        errors = []
        
        # Check for conflicting options
        if options_dict.get('mirror_mode') and options_dict.get('copy_subdirs'):
            warnings.append("Mirror mode (/MIR) includes subdirectory copying. /S option is redundant.")
        
        if options_dict.get('mirror_mode') and options_dict.get('copy_empty_subdirs'):
            warnings.append("Mirror mode (/MIR) includes empty subdirectories. /E option is redundant.")
        
        if options_dict.get('copy_subdirs') and options_dict.get('copy_empty_subdirs'):
            warnings.append("/E option includes /S functionality. /S option is redundant.")
        
        # Validate numeric fields
        retries = options_dict.get('retries', '0')
        valid, error, _ = self.validate_numeric_input(retries, "Retries", 0, 10000)
        if not valid:
            errors.append(error)
        
        wait_time = options_dict.get('wait_time', '30')
        valid, error, _ = self.validate_numeric_input(wait_time, "Wait time", 1, 3600)
        if not valid:
            errors.append(error)
        
        threads = options_dict.get('threads', '8')
        valid, error, thread_val = self.validate_numeric_input(threads, "Threads", 1, 128)
        if not valid:
            errors.append(error)
        elif thread_val is not None and thread_val > 64:
            warnings.append("High thread count may impact system performance.")
        
        # Check source and destination
        source = options_dict.get('source_path', '')
        dest = options_dict.get('dest_path', '')
        
        if source and dest:
            # Normalize paths for comparison
            try:
                norm_source = os.path.normpath(os.path.abspath(source)).lower()
                norm_dest = os.path.normpath(os.path.abspath(dest)).lower()
                
                if norm_source == norm_dest:
                    errors.append("Source and destination cannot be the same directory.")
                elif norm_dest.startswith(norm_source + os.sep):
                    errors.append("Destination cannot be a subdirectory of source.")
                elif options_dict.get('mirror_mode') and norm_source.startswith(norm_dest + os.sep):
                    warnings.append("Source is subdirectory of destination with mirror mode. This may cause data loss.")
            except Exception as e:
                warnings.append(f"Could not validate path relationship: {str(e)}")
        
        return len(errors) == 0, warnings, errors
    
    def generate_safe_command(self, options_dict):
        """
        Generate a safe ROBOCOPY command with validation
        
        Args:
            options_dict (dict): Dictionary of options
        
        Returns:
            tuple: (command_string, is_safe, warnings, errors)
        """
        # Validate all options first
        is_valid, warnings, errors = self.validate_robocopy_options(options_dict)
        
        if not is_valid:
            return "", False, warnings, errors
        
        # Validate paths
        source = options_dict.get('source_path', '')
        dest = options_dict.get('dest_path', '')
        
        source_valid, source_error = self.validate_path(source, "directory")
        if not source_valid:
            errors.append(f"Source: {source_error}")
        
        # For destination, just check if parent directory exists
        if dest:
            dest_parent = os.path.dirname(dest)
            if dest_parent and not os.path.exists(dest_parent):
                errors.append(f"Destination parent directory does not exist: {dest_parent}")
        
        if errors:
            return "", False, warnings, errors
        
        # Build command
        cmd_parts = ["robocopy", f'"{source}"', f'"{dest}"']
        
        # Add options in logical order
        if options_dict.get('mirror_mode'):
            cmd_parts.append("/MIR")
        elif options_dict.get('copy_empty_subdirs'):
            cmd_parts.append("/E")
        elif options_dict.get('copy_subdirs'):
            cmd_parts.append("/S")
        
        if options_dict.get('copy_attributes'):
            cmd_parts.append("/COPYALL")
        if options_dict.get('copy_timestamps'):
            cmd_parts.append("/DCOPY:T")
        if options_dict.get('copy_security'):
            cmd_parts.append("/SEC")
        
        # Numeric options
        retries = options_dict.get('retries', '').strip()
        if retries and retries != '0':
            cmd_parts.extend(["/R", retries])
        
        wait_time = options_dict.get('wait_time', '').strip()
        if wait_time:
            cmd_parts.extend(["/W", wait_time])
        
        threads = options_dict.get('threads', '').strip()
        if threads and threads != '1':
            cmd_parts.extend(["/MT", threads])
        
        # Additional flags
        if options_dict.get('purge_dest'):
            cmd_parts.append("/PURGE")
        if options_dict.get('exclude_changed'):
            cmd_parts.append("/XC")
        if options_dict.get('exclude_newer'):
            cmd_parts.append("/XN")
        if options_dict.get('verbose'):
            cmd_parts.append("/V")
        
        # Always add these for better output and logging
        cmd_parts.extend(["/TEE", "/NP", "/LOG+:robocopy.log"])
        
        command = " ".join(cmd_parts)
        return command, True, warnings, []

class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self, config_file="robocopy_config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
    
    def get_default_config(self):
        """Get default configuration"""
        return {
            "source_path": "",
            "dest_path": "",
            "copy_subdirs": False,
            "copy_empty_subdirs": True,
            "copy_attributes": False,
            "copy_timestamps": False,
            "copy_security": False,
            "mirror_mode": False,
            "retries": "3",
            "wait_time": "30",
            "threads": "8",
            "purge_dest": False,
            "exclude_changed": False,
            "exclude_newer": False,
            "verbose": True
        }
    
    def validate_config(self, config):
        """Validate loaded configuration"""
        default_config = self.get_default_config()
        
        # Ensure all required keys exist
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
                self.logger.warning(f"Missing config key '{key}', using default: {default_value}")
        
        # Validate data types
        bool_keys = [k for k, v in default_config.items() if isinstance(v, bool)]
        str_keys = [k for k, v in default_config.items() if isinstance(v, str)]
        
        for key in bool_keys:
            if not isinstance(config[key], bool):
                config[key] = bool(config[key])
                self.logger.warning(f"Fixed data type for '{key}'")
        
        for key in str_keys:
            if not isinstance(config[key], str):
                config[key] = str(config[key])
                self.logger.warning(f"Fixed data type for '{key}'")
        
        return config
