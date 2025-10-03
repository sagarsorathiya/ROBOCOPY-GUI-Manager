#!/usr/bin/env python3
"""
ROBOCOPY GUI Manager - Advanced Edition
A comprehensive user-friendly interface for Windows ROBOCOPY command management.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import json
import logging
from datetime import datetime
import queue
import sys
import time
import webbrowser

class ToolTip:
    """Creates a tooltip for a given widget"""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None

    def enter(self, event=None):
        self.show_tooltip()

    def leave(self, event=None):
        self.hide_tooltip()

    def show_tooltip(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Tahoma", 8, "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class AdvancedRobocopyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROBOCOPY GUI Manager - Advanced Edition")
        self.root.geometry("1400x900")  # Increased window size for better visibility
        self.root.minsize(1000, 700)
        
        # Configure modern styling
        self.setup_styles()
        
        # Configure logging
        self.setup_logging()
        
        # Initialize variables
        self.source_path = tk.StringVar()
        self.dest_path = tk.StringVar()
        self.current_process = None
        self.operation_in_progress = False  # Track if operation is running
        self.output_queue = queue.Queue()
        self.operation_start_time = None
        self.files_copied = 0
        self.bytes_copied = 0
        
        # Progress tracking variables
        self.progress_var = tk.DoubleVar()
        self.auto_scroll_var = tk.BooleanVar(value=True)
        
        # Configuration file for saving/loading settings
        self.config_file = "robocopy_config.json"
        
        # Enhanced performance monitoring
        self.performance_stats = {
            'files_copied': 0,
            'dirs_copied': 0,
            'bytes_copied': 0,
            'total_files': 0,
            'speed_mbps': 0.0,
            'errors': 0
        }
        
        # Create GUI elements
        self.create_menu()
        self.create_widgets()
        self.load_config()
        
        # Start GUI keep-alive mechanism for responsiveness during long operations
        self.start_keepalive()
        
        # Load command history
        self.root.after(500, self.load_command_history)
        
        # Start output queue checker
        self.root.after(100, self.check_output_queue)
        
        # Start performance monitor
        self.start_performance_timer()
        self.root.after(1000, self.update_performance_stats)
        
        # Auto-refresh log on startup
        self.root.after(1000, self.refresh_log)
    
    def setup_styles(self):
        """Setup modern styling for the application"""
        style = ttk.Style()
        
        # Configure notebook style for tabs
        style.configure('Custom.TNotebook', background='#f0f0f0')
        style.configure('Custom.TNotebook.Tab', padding=[20, 10])
        
        # Configure frame styles
        style.configure('Title.TFrame', background='#e8e8e8', relief='raised')
        style.configure('Content.TFrame', background='#f8f8f8')
        
        # Configure button styles
        style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TButton', foreground='green')
        style.configure('Warning.TButton', foreground='orange')
        style.configure('Danger.TButton', foreground='red')
        
        # Enhanced progress bar style
        style.configure('Enhanced.Horizontal.TProgressbar', 
                       background='#4CAF50',
                       troughcolor='#E0E0E0',
                       borderwidth=1,
                       lightcolor='#81C784',
                       darkcolor='#388E3C')
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Configuration", command=self.new_config)
        file_menu.add_command(label="Open Configuration...", command=self.load_config_file)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_command(label="Save Configuration As...", command=self.save_config_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export Log", command=self.export_log)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Performance Monitor", command=self.show_performance_monitor)
        tools_menu.add_command(label="Command History", command=self.show_command_history)
        tools_menu.add_command(label="Validate Paths", command=self.validate_all_paths)
        tools_menu.add_separator()
        tools_menu.add_command(label="ROBOCOPY Documentation", command=self.open_robocopy_docs)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="Return Codes", command=self.show_return_codes)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('robocopy_gui.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_widgets(self):
        """Create and arrange GUI widgets with advanced features"""
        # Main container with notebook for tabs
        self.notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.basic_tab = ttk.Frame(self.notebook)
        self.advanced_tab = ttk.Frame(self.notebook)
        self.monitoring_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.basic_tab, text="Basic Settings")
        self.notebook.add(self.advanced_tab, text="Advanced Options")
        self.notebook.add(self.monitoring_tab, text="Performance Monitor")
        self.notebook.add(self.logs_tab, text="Logs & History")
        
        # Create content for each tab
        self.create_basic_tab()
        
        # Initialize basic variables if they don't exist yet (for compatibility)
        if not hasattr(self, 'retries'):
            self.retries = tk.StringVar(value="3")
        if not hasattr(self, 'wait_time'):
            self.wait_time = tk.StringVar(value="30")
        if not hasattr(self, 'threads'):
            self.threads = tk.StringVar(value="16")
        if not hasattr(self, 'verbose'):
            self.verbose = tk.BooleanVar(value=True)
        
        self.create_advanced_tab()
        self.create_monitoring_tab()
        self.create_logs_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_basic_tab(self):
        """Create basic settings tab"""
        main_frame = ttk.Frame(self.basic_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Source directory selection with validation (moved up to row 0)
        source_label = ttk.Label(main_frame, text="Source Directory:")
        source_label.grid(row=0, column=0, sticky="w", pady=5)
        ToolTip(source_label, "Select the source directory to copy files from.\nThis is the folder containing files you want to copy.")
        
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)
        source_frame.columnconfigure(0, weight=1)
        
        self.source_entry = ttk.Entry(source_frame, textvariable=self.source_path, width=60)
        self.source_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.source_entry.bind("<KeyRelease>", self.on_source_change)
        
        source_browse_btn = ttk.Button(source_frame, text="Browse", command=self.browse_source)
        source_browse_btn.grid(row=0, column=1)
        ToolTip(source_browse_btn, "Click to select source directory using file browser")
        
        self.source_status = ttk.Label(source_frame, text="", foreground="gray")
        self.source_status.grid(row=1, column=0, columnspan=2, sticky="w")
        
        # Destination directory selection with validation
        dest_label = ttk.Label(main_frame, text="Destination Directory:")
        dest_label.grid(row=1, column=0, sticky="w", pady=5)
        ToolTip(dest_label, "Select the destination directory where files will be copied.\nThis folder will be created if it doesn't exist.")
        
        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=5)
        dest_frame.columnconfigure(0, weight=1)
        
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_path, width=60)
        self.dest_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.dest_entry.bind("<KeyRelease>", self.on_dest_change)
        
        dest_browse_btn = ttk.Button(dest_frame, text="Browse", command=self.browse_dest)
        dest_browse_btn.grid(row=0, column=1)
        ToolTip(dest_browse_btn, "Click to select destination directory using file browser")
        
        self.dest_status = ttk.Label(dest_frame, text="", foreground="gray")
        self.dest_status.grid(row=1, column=0, columnspan=2, sticky="w")
        
        # Compact three-column layout: Options+Presets | Solutions | Controls
        options_container_frame = ttk.Frame(main_frame)
        options_container_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        options_container_frame.columnconfigure(0, weight=2)  # Basic options+presets get more space
        options_container_frame.columnconfigure(1, weight=2)  # Solutions get equal space
        options_container_frame.columnconfigure(2, weight=1)  # Controls get less space
        
        # Column 1 - Basic Copy Options with Quick Presets beside
        basic_options_frame = ttk.LabelFrame(options_container_frame, text="Basic Copy Options & Quick Presets", padding="8")
        basic_options_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        basic_options_frame.columnconfigure(0, weight=1)  # Options column
        basic_options_frame.columnconfigure(1, weight=1)  # Presets column
        
        self.create_basic_copy_options_with_presets(basic_options_frame)
        
        # Column 2 - Permission Error Solutions (compact)
        solutions_frame = ttk.LabelFrame(options_container_frame, text="Permission Error Solutions", padding="8")
        solutions_frame.grid(row=0, column=1, sticky="nsew", padx=3)
        solutions_frame.columnconfigure(0, weight=1)
        
        self.create_permission_solutions(solutions_frame)
        
        # Column 3 - Control Buttons (compact vertical layout)
        controls_frame = ttk.LabelFrame(options_container_frame, text="Controls", padding="8")
        controls_frame.grid(row=0, column=2, sticky="nsew", padx=(3, 0))
        controls_frame.columnconfigure(0, weight=1)
        
        self.create_control_buttons(controls_frame)
        
        # Enhanced command preview spanning full width under all three columns
        command_frame = ttk.LabelFrame(main_frame, text="Generated Command", padding="10")
        command_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 10))
        command_frame.columnconfigure(0, weight=1)
        
        # Command display with enhanced styling and full width utilization
        self.command_display = ttk.Label(command_frame, text="Click 'Generate' to see command...", 
                                        font=("Consolas", 10), foreground="blue", wraplength=1200, 
                                        justify=tk.LEFT, relief="sunken", padding="8")
        self.command_display.grid(row=0, column=0, sticky="ew", pady=2)
        ToolTip(self.command_display, "This shows the actual ROBOCOPY command that will be executed.\nSpans full width under all control sections for maximum visibility.")
        
        # Real-time output with enhanced formatting (much bigger area)
        output_frame = ttk.LabelFrame(main_frame, text="Output & Progress", padding="8")
        output_frame.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(3, weight=1)  # Give more weight to output text area
        main_frame.rowconfigure(4, weight=3)  # Much more weight for output frame (was 2, now 3)
        
        # Progress information frame
        progress_info_frame = ttk.Frame(output_frame)
        progress_info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        progress_info_frame.columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(progress_info_frame, text="Ready to start", 
                                       font=("Segoe UI", 10, "bold"))  # Slightly bigger font
        self.progress_label.grid(row=0, column=0, sticky="w")
        
        self.time_label = ttk.Label(progress_info_frame, text="Elapsed: 00:00:00",
                                   font=("Segoe UI", 10))
        self.time_label.grid(row=0, column=1, sticky="e")
        
        # Progress bar removed from Basic Settings - use Real-time Performance Metrics tab for detailed progress tracking
        
        # Auto-scroll controls frame
        scroll_controls_frame = ttk.Frame(output_frame)
        scroll_controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        
        self.auto_scroll = tk.BooleanVar(value=True)  # Default to auto-scroll enabled
        auto_scroll_check = ttk.Checkbutton(scroll_controls_frame, text="Auto-scroll output", 
                                           variable=self.auto_scroll)
        auto_scroll_check.grid(row=0, column=0, sticky="w")
        
        # Output line counter
        self.line_count_label = ttk.Label(scroll_controls_frame, text="Lines: 0", 
                                         font=("Segoe UI", 9))
        self.line_count_label.grid(row=0, column=1, padx=(20, 0))
        
        # Clear output button
        clear_btn = ttk.Button(scroll_controls_frame, text="Clear Output", 
                              command=self.clear_output)
        clear_btn.grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        # Copy output button
        copy_btn = ttk.Button(scroll_controls_frame, text="Copy All", 
                             command=self.copy_output)
        copy_btn.grid(row=0, column=3, sticky="e", padx=(5, 0))
        
        scroll_controls_frame.columnconfigure(0, weight=1)
        
        # Output text with syntax highlighting (much bigger)
        self.output_text = scrolledtext.ScrolledText(output_frame, height=25, wrap=tk.WORD,
                                                    font=("Consolas", 10))  # Increased height significantly (was 20, now 25)
        self.output_text.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        
        # Configure text tags for colored output
        self.output_text.tag_configure("success", foreground="green", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("error", foreground="red", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("warning", foreground="orange", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("info", foreground="blue")
        self.output_text.tag_configure("summary", foreground="navy", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("command", foreground="purple", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("highlight", background="yellow")
        
        # Enhanced error type tags for better error handling
        self.output_text.tag_configure("permission_error", foreground="red", background="#ffeeee", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("disk_error", foreground="red", background="#ffe6e6", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("path_error", foreground="red", background="#ffeeff", font=("Consolas", 9, "bold"))
        self.output_text.tag_configure("solution", foreground="darkblue", background="#e6f3ff", font=("Consolas", 9, "italic"))
        self.output_text.tag_configure("retry", foreground="darkorange", font=("Consolas", 9))
        self.output_text.tag_configure("wait", foreground="gray", font=("Consolas", 9, "italic"))
    
    def create_basic_copy_options(self, parent):
        """Create compact basic copy option checkboxes"""
        # Configure parent for single column compact layout
        parent.columnconfigure(0, weight=1)
        
        self.copy_subdirs = tk.BooleanVar()
        self.copy_empty_subdirs = tk.BooleanVar()
        self.copy_attributes = tk.BooleanVar()
        self.copy_timestamps = tk.BooleanVar()
        self.copy_security = tk.BooleanVar()
        self.mirror_mode = tk.BooleanVar()
        
        # Compact single-column layout
        # Copy subdirectories
        subdirs_cb = ttk.Checkbutton(parent, text="Copy subdirectories (/S)", 
                                   variable=self.copy_subdirs, command=self.generate_command)
        subdirs_cb.grid(row=0, column=0, sticky="w", pady=1)
        ToolTip(subdirs_cb, "Copy subdirectories, but not empty ones.\nUse this to copy files in subdirectories while skipping empty folders.")
        
        # Copy empty subdirectories  
        empty_subdirs_cb = ttk.Checkbutton(parent, text="Copy empty subdirectories (/E)", 
                                         variable=self.copy_empty_subdirs, command=self.generate_command)
        empty_subdirs_cb.grid(row=1, column=0, sticky="w", pady=1)
        ToolTip(empty_subdirs_cb, "Copy subdirectories, including empty ones.\nThis ensures the exact directory structure is replicated.")
        
        # Copy attributes
        attributes_cb = ttk.Checkbutton(parent, text="Copy all file attributes (/COPYALL)", 
                                      variable=self.copy_attributes, command=self.generate_command)
        attributes_cb.grid(row=2, column=0, sticky="w", pady=1)
        ToolTip(attributes_cb, "Copy all file information including:\n• Data\n• Attributes\n• Timestamps\n• Security (NTFS ACLs)\n• Owner info\n• Auditing info")
        
        # Copy timestamps
        timestamps_cb = ttk.Checkbutton(parent, text="Copy directory timestamps (/DCOPY:T)", 
                                      variable=self.copy_timestamps, command=self.generate_command)
        timestamps_cb.grid(row=3, column=0, sticky="w", pady=1)
        ToolTip(timestamps_cb, "Copy directory timestamps.\nPreserves when directories were created/modified.")
        
        # Copy security
        security_cb = ttk.Checkbutton(parent, text="Copy security info (/SEC)", 
                                    variable=self.copy_security, command=self.generate_command)
        security_cb.grid(row=4, column=0, sticky="w", pady=1)
        ToolTip(security_cb, "Copy files with security (equivalent to /COPY:DATS).\nIncludes file permissions and ownership.")
        
        # Mirror mode
        mirror_cb = ttk.Checkbutton(parent, text="Mirror mode (/MIR) ⚠️", 
                                  variable=self.mirror_mode, command=self.on_mirror_change)
        mirror_cb.grid(row=5, column=0, sticky="w", pady=1)
        ToolTip(mirror_cb, "⚠️ MIRROR MODE - USE WITH CAUTION!\n\nMirror a directory tree (equivalent to /E plus /PURGE).\nThis will DELETE files in destination that don't exist in source!\n\nOnly use this if you want an exact mirror of the source.")
    
    def create_basic_copy_options_with_presets(self, parent):
        """Create basic copy options with quick presets side by side"""
        # Configure parent for two-column layout
        parent.columnconfigure(0, weight=1)  # Options column
        parent.columnconfigure(1, weight=1)  # Presets column
        
        # Left side - Basic Copy Options
        options_frame = ttk.Frame(parent)
        options_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        self.copy_subdirs = tk.BooleanVar()
        self.copy_empty_subdirs = tk.BooleanVar()
        self.copy_attributes = tk.BooleanVar()
        self.copy_timestamps = tk.BooleanVar()
        self.copy_security = tk.BooleanVar()
        self.mirror_mode = tk.BooleanVar()
        
        # Copy options in compact layout
        ttk.Label(options_frame, text="Copy Options:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        subdirs_cb = ttk.Checkbutton(options_frame, text="Copy subdirectories (/S)", 
                                   variable=self.copy_subdirs, command=self.generate_command)
        subdirs_cb.grid(row=1, column=0, sticky="w", pady=1)
        ToolTip(subdirs_cb, "Copy subdirectories, but not empty ones.")
        
        empty_subdirs_cb = ttk.Checkbutton(options_frame, text="Copy empty subdirectories (/E)", 
                                         variable=self.copy_empty_subdirs, command=self.generate_command)
        empty_subdirs_cb.grid(row=2, column=0, sticky="w", pady=1)
        ToolTip(empty_subdirs_cb, "Copy subdirectories, including empty ones.")
        
        attributes_cb = ttk.Checkbutton(options_frame, text="Copy all file attributes (/COPYALL)", 
                                      variable=self.copy_attributes, command=self.generate_command)
        attributes_cb.grid(row=3, column=0, sticky="w", pady=1)
        ToolTip(attributes_cb, "Copy all file information including security.")
        
        timestamps_cb = ttk.Checkbutton(options_frame, text="Copy directory timestamps (/DCOPY:T)", 
                                      variable=self.copy_timestamps, command=self.generate_command)
        timestamps_cb.grid(row=4, column=0, sticky="w", pady=1)
        ToolTip(timestamps_cb, "Copy directory timestamps.")
        
        security_cb = ttk.Checkbutton(options_frame, text="Copy security info (/SEC)", 
                                    variable=self.copy_security, command=self.generate_command)
        security_cb.grid(row=5, column=0, sticky="w", pady=1)
        ToolTip(security_cb, "Copy files with security permissions.")
        
        mirror_cb = ttk.Checkbutton(options_frame, text="Mirror mode (/MIR) ⚠️", 
                                  variable=self.mirror_mode, command=self.on_mirror_change)
        mirror_cb.grid(row=6, column=0, sticky="w", pady=1)
        ToolTip(mirror_cb, "⚠️ MIRROR MODE - Deletes files in destination not in source!")
        
        # Right side - Quick Presets (compact vertical)
        presets_frame = ttk.Frame(parent)
        presets_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ttk.Label(presets_frame, text="Quick Presets:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        backup_btn = ttk.Button(presets_frame, text="📁 Backup", command=lambda: self.apply_preset("backup"))
        backup_btn.grid(row=1, column=0, pady=2, sticky="ew")
        ToolTip(backup_btn, "Backup preset: Copy all files and subdirectories with attributes")
        
        sync_btn = ttk.Button(presets_frame, text="🔄 Sync/Mirror", command=lambda: self.apply_preset("mirror"))
        sync_btn.grid(row=2, column=0, pady=2, sticky="ew")
        ToolTip(sync_btn, "Mirror preset: Synchronize source and destination\n(WARNING: Deletes files)")
        
        move_btn = ttk.Button(presets_frame, text="📦 Move", command=lambda: self.apply_preset("move"))
        move_btn.grid(row=3, column=0, pady=2, sticky="ew")
        ToolTip(move_btn, "Move preset: Copy files and delete from source")
        
        custom_btn = ttk.Button(presets_frame, text="⚙️ Custom", command=lambda: self.apply_preset("custom"))
        custom_btn.grid(row=4, column=0, pady=2, sticky="ew")
        ToolTip(custom_btn, "Custom preset: Clear all settings for manual configuration")
        
        # Configure preset buttons to expand
        presets_frame.columnconfigure(0, weight=1)
    
    def on_mirror_change(self):
        """Handle mirror mode toggle with warning"""
        if self.mirror_mode.get():
            result = messagebox.askyesno(
                "Mirror Mode Warning",
                "⚠️ MIRROR MODE WARNING ⚠️\n\n"
                "Mirror mode will DELETE files in the destination that don't exist in the source!\n\n"
                "This can result in permanent data loss if used incorrectly.\n\n"
                "Are you sure you want to enable Mirror Mode?",
                icon="warning"
            )
            if not result:
                self.mirror_mode.set(False)
                return
        self.generate_command()
    
    def create_permission_solutions(self, parent):
        """Create compact permission error solutions"""
        # Solution buttons in compact vertical layout
        ttk.Button(parent, text="Remove Security (/SEC)", 
                  command=self.fix_remove_security).grid(row=0, column=0, pady=1, sticky="ew")
        
        ttk.Button(parent, text="Remove Timestamps (/DCOPY:T)", 
                  command=self.fix_remove_dcopy).grid(row=1, column=0, pady=1, sticky="ew")
        
        ttk.Button(parent, text="Basic Copy Only", 
                  command=self.fix_basic_copy).grid(row=2, column=0, pady=1, sticky="ew")
        
        ttk.Button(parent, text="Admin Instructions", 
                  command=self.show_admin_instructions).grid(row=3, column=0, pady=1, sticky="ew")
        
        # Add tooltip for the solutions panel
        ToolTip(parent, "Quick fixes for common permission errors encountered during ROBOCOPY operations")
    
    def create_control_buttons(self, parent):
        """Create compact control buttons in vertical layout"""
        # Main control buttons
        generate_btn = ttk.Button(parent, text="🔄 Generate", 
                                 command=self.generate_command, style='Action.TButton')
        generate_btn.grid(row=0, column=0, pady=2, sticky="ew")
        ToolTip(generate_btn, "Generate and preview the ROBOCOPY command\nbased on your current settings")
        
        execute_btn = ttk.Button(parent, text="▶️ Execute", 
                               command=self.execute_command, style='Success.TButton')
        execute_btn.grid(row=1, column=0, pady=2, sticky="ew")
        ToolTip(execute_btn, "Execute the ROBOCOPY command\n(Make sure to generate and review first)")
        
        stop_btn = ttk.Button(parent, text="⏹️ Stop", 
                            command=self.stop_command, style='Danger.TButton')
        stop_btn.grid(row=2, column=0, pady=2, sticky="ew")
        ToolTip(stop_btn, "Stop the currently running ROBOCOPY operation")
        
        # Configuration buttons
        ttk.Separator(parent, orient='horizontal').grid(row=3, column=0, sticky="ew", pady=5)
        
        save_btn = ttk.Button(parent, text="💾 Save", command=self.save_config)
        save_btn.grid(row=4, column=0, pady=2, sticky="ew")
        ToolTip(save_btn, "Save current settings to configuration file\nfor later use")
        
        load_btn = ttk.Button(parent, text="📁 Load", command=self.load_config_file)
        load_btn.grid(row=5, column=0, pady=2, sticky="ew")
        ToolTip(load_btn, "Load previously saved configuration")
    
    def apply_preset(self, preset_type):
        """Apply predefined configuration presets"""
        presets = {
            "backup": {
                "copy_subdirs": False,
                "copy_empty_subdirs": True,
                "copy_attributes": True,
                "copy_timestamps": True,
                "copy_security": True,
                "mirror_mode": False,
                "retries": "3",
                "wait_time": "30",
                "threads": "8",
                "verbose": True
            },
            "mirror": {
                "copy_subdirs": False,
                "copy_empty_subdirs": False,
                "copy_attributes": False,
                "copy_timestamps": False,
                "copy_security": False,
                "mirror_mode": True,
                "retries": "1",
                "wait_time": "30",
                "threads": "16",
                "verbose": True
            },
            "move": {
                "copy_subdirs": False,
                "copy_empty_subdirs": True,
                "copy_attributes": True,
                "copy_timestamps": True,
                "copy_security": False,
                "mirror_mode": False,
                "move_files": True,
                "retries": "1",
                "wait_time": "30",
                "threads": "4",
                "verbose": True
            },
            "custom": {
                "copy_subdirs": False,
                "copy_empty_subdirs": False,
                "copy_attributes": False,
                "copy_timestamps": False,
                "copy_security": False,
                "mirror_mode": False,
                "retries": "0",
                "wait_time": "30",
                "threads": "8",
                "verbose": False
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            
            # Apply basic options
            self.copy_subdirs.set(preset.get("copy_subdirs", False))
            self.copy_empty_subdirs.set(preset.get("copy_empty_subdirs", False))
            self.copy_attributes.set(preset.get("copy_attributes", False))
            self.copy_timestamps.set(preset.get("copy_timestamps", False))
            self.copy_security.set(preset.get("copy_security", False))
            
            # Handle mirror mode with warning
            if preset.get("mirror_mode", False):
                self.mirror_mode.set(True)
                self.on_mirror_change()
            else:
                self.mirror_mode.set(False)
            
            # Apply advanced options if they exist
            if hasattr(self, 'retries'):
                self.retries.set(preset.get("retries", "3"))
            if hasattr(self, 'wait_time'):
                self.wait_time.set(preset.get("wait_time", "30"))
            if hasattr(self, 'threads'):
                self.threads.set(preset.get("threads", "8"))
            if hasattr(self, 'verbose'):
                self.verbose.set(preset.get("verbose", True))
            
            # Show preset applied message
            self.update_status(f"Applied {preset_type.title()} preset configuration")
            self.generate_command()
    
    def on_source_change(self, event=None):
        """Handle source path changes with real-time validation"""
        path = self.source_path.get()
        if not path:
            self.source_status.config(text="", foreground="gray")
            return
            
        if os.path.exists(path) and os.path.isdir(path):
            try:
                file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                dir_count = len([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
                self.source_status.config(text=f"✓ Valid source ({file_count} files, {dir_count} directories)", 
                                        foreground="green")
            except PermissionError:
                self.source_status.config(text="⚠ Access denied - check permissions", foreground="orange")
        else:
            self.source_status.config(text="✗ Invalid path or not a directory", foreground="red")
        
        self.generate_command()
    
    def on_dest_change(self, event=None):
        """Handle destination path changes with real-time validation"""
        path = self.dest_path.get()
        if not path:
            self.dest_status.config(text="", foreground="gray")
            return
            
        if os.path.exists(path):
            if os.path.isdir(path):
                self.dest_status.config(text="✓ Destination exists and is accessible", foreground="green")
            else:
                self.dest_status.config(text="✗ Path exists but is not a directory", foreground="red")
        else:
            parent_dir = os.path.dirname(path)
            if parent_dir and os.path.exists(parent_dir):
                self.dest_status.config(text="✓ Will be created (parent directory exists)", foreground="blue")
            else:
                self.dest_status.config(text="⚠ Parent directory does not exist", foreground="orange")
        
        self.generate_command()
    
    def validate_number(self, value):
        """Validate numeric input for spinboxes"""
        if value == "":
            return True  # Allow empty string
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def update_status(self, message):
        """Update status bar message"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            # Auto-clear status after 5 seconds
            self.root.after(5000, lambda: self.status_label.config(text="Ready"))
    def create_advanced_tab(self):
        """Create advanced options tab with performance optimizations"""
        main_frame = ttk.Frame(self.advanced_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Performance section
        perf_frame = ttk.LabelFrame(main_frame, text="Performance & Threading", padding="10")
        perf_frame.pack(fill=tk.X, pady=(0, 10))
        perf_frame.columnconfigure(1, weight=1)
        
        # Multi-threading for speed
        ttk.Label(perf_frame, text="Thread Count:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.threads = tk.StringVar(value="16")  # Increased default for better performance
        threads_spinbox = ttk.Spinbox(perf_frame, from_=1, to=128, textvariable=self.threads, width=10,
                                     validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        threads_spinbox.grid(row=0, column=1, sticky="w")
        ToolTip(threads_spinbox, "Number of threads for parallel copying.\nMore threads = faster copying for many small files.\nRecommended: 8-32 for HDDs, 16-64 for SSDs")
        
        # Retry settings
        ttk.Label(perf_frame, text="Retry Count:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.retries = tk.StringVar(value="3")
        retries_spinbox = ttk.Spinbox(perf_frame, from_=0, to=100, textvariable=self.retries, width=10,
                                     validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        retries_spinbox.grid(row=1, column=1, sticky="w")
        ToolTip(retries_spinbox, "Number of retries for failed files.\nHigher values increase reliability but may slow down on problematic files.")
        
        ttk.Label(perf_frame, text="Wait Time (seconds):").grid(row=2, column=0, sticky="w", padx=(0, 10))
        self.wait_time = tk.StringVar(value="30")
        wait_spinbox = ttk.Spinbox(perf_frame, from_=1, to=3600, textvariable=self.wait_time, width=10,
                                  validate='key', validatecommand=(self.root.register(self.validate_number), '%P'))
        wait_spinbox.grid(row=2, column=1, sticky="w")
        ToolTip(wait_spinbox, "Wait time between retries in seconds.\nLonger waits may help with network issues but slow overall process.")
        
        # Advanced copy options
        advanced_copy_frame = ttk.LabelFrame(main_frame, text="Advanced Copy Options", padding="10")
        advanced_copy_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File selection options
        self.move_files = tk.BooleanVar()
        self.purge_dest = tk.BooleanVar()
        self.exclude_changed = tk.BooleanVar()
        self.exclude_newer = tk.BooleanVar()
        self.exclude_older = tk.BooleanVar()
        self.only_newer = tk.BooleanVar()
        
        move_cb = ttk.Checkbutton(advanced_copy_frame, text="Move files (delete from source) (/MOV)", 
                                variable=self.move_files)
        move_cb.grid(row=0, column=0, sticky="w", pady=2)
        ToolTip(move_cb, "⚠️ Move files instead of copying them.\nFiles will be DELETED from source after copying!")
        
        purge_cb = ttk.Checkbutton(advanced_copy_frame, text="Purge destination (/PURGE)", 
                                 variable=self.purge_dest)
        purge_cb.grid(row=1, column=0, sticky="w", pady=2)
        ToolTip(purge_cb, "Delete files in destination that don't exist in source.\nUse with caution - can cause data loss!")
        
        exclude_changed_cb = ttk.Checkbutton(advanced_copy_frame, text="Exclude changed files (/XC)", 
                                           variable=self.exclude_changed)
        exclude_changed_cb.grid(row=2, column=0, sticky="w", pady=2)
        ToolTip(exclude_changed_cb, "Skip files that exist in destination but have different content.")
        
        exclude_newer_cb = ttk.Checkbutton(advanced_copy_frame, text="Exclude newer files (/XN)", 
                                         variable=self.exclude_newer)
        exclude_newer_cb.grid(row=0, column=1, sticky="w", pady=2, padx=(20, 0))
        ToolTip(exclude_newer_cb, "Skip files that are newer in the destination.")
        
        exclude_older_cb = ttk.Checkbutton(advanced_copy_frame, text="Exclude older files (/XO)", 
                                         variable=self.exclude_older)
        exclude_older_cb.grid(row=1, column=1, sticky="w", pady=2, padx=(20, 0))
        ToolTip(exclude_older_cb, "Skip files that are older in the destination.")
        
        only_newer_cb = ttk.Checkbutton(advanced_copy_frame, text="Copy only newer files (/XL)", 
                                      variable=self.only_newer)
        only_newer_cb.grid(row=2, column=1, sticky="w", pady=2, padx=(20, 0))
        ToolTip(only_newer_cb, "Copy only files that are newer in the source.")
        
        # Logging and monitoring
        logging_frame = ttk.LabelFrame(main_frame, text="Logging & Monitoring", padding="10")
        logging_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.verbose = tk.BooleanVar(value=True)
        self.create_log = tk.BooleanVar(value=True)
        self.show_progress = tk.BooleanVar(value=True)
        self.list_only = tk.BooleanVar()
        
        verbose_cb = ttk.Checkbutton(logging_frame, text="Verbose output (/V)", 
                                   variable=self.verbose)
        verbose_cb.grid(row=0, column=0, sticky="w", pady=2)
        ToolTip(verbose_cb, "Show detailed information about each file being processed.")
        
        log_cb = ttk.Checkbutton(logging_frame, text="Create log file", 
                               variable=self.create_log)
        log_cb.grid(row=0, column=1, sticky="w", pady=2, padx=(20, 0))
        ToolTip(log_cb, "Create a detailed log file of the operation.")
        
        progress_cb = ttk.Checkbutton(logging_frame, text="Show progress (/NP disabled)", 
                                    variable=self.show_progress)
        progress_cb.grid(row=1, column=0, sticky="w", pady=2)
        ToolTip(progress_cb, "Show progress percentage for each file (may slow down operation).")
        
        list_only_cb = ttk.Checkbutton(logging_frame, text="List only (don't copy) (/L)", 
                                     variable=self.list_only)
        list_only_cb.grid(row=1, column=1, sticky="w", pady=2, padx=(20, 0))
        ToolTip(list_only_cb, "List files that would be copied without actually copying them.\nUseful for testing your configuration.")
    
    def create_monitoring_tab(self):
        """Create performance monitoring tab with enhanced real-time metrics"""
        main_frame = ttk.Frame(self.monitoring_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Performance metrics frame
        metrics_frame = ttk.LabelFrame(main_frame, text="Real-time Performance Metrics", padding="10")
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Configure grid columns for better layout
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)
        
        # Files and directories processed
        self.files_processed_label = ttk.Label(metrics_frame, text="Files Processed: 0", font=("Segoe UI", 10, "bold"))
        self.files_processed_label.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        self.dirs_processed_label = ttk.Label(metrics_frame, text="Directories: 0")
        self.dirs_processed_label.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        # Current file being processed
        self.current_file_label = ttk.Label(metrics_frame, text="Processing: Ready to start...", 
                                           foreground="blue", font=("Segoe UI", 9))
        self.current_file_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Data metrics
        self.bytes_copied_label = ttk.Label(metrics_frame, text="Data Copied: 0 B")
        self.bytes_copied_label.grid(row=2, column=0, sticky="w", padx=(0, 20))
        
        self.copy_speed_label = ttk.Label(metrics_frame, text="Speed: 0 MB/s")
        self.copy_speed_label.grid(row=2, column=1, sticky="w", padx=(0, 20))
        
        # Time metrics
        self.elapsed_time_label = ttk.Label(metrics_frame, text="Elapsed: 00:00:00")
        self.elapsed_time_label.grid(row=3, column=0, sticky="w", padx=(0, 20))
        
        self.eta_label = ttk.Label(metrics_frame, text="ETA: Calculating...")
        self.eta_label.grid(row=3, column=1, sticky="w", padx=(0, 20))
        
        # Progress indicator frame
        progress_frame = ttk.LabelFrame(main_frame, text="Operation Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar with label
        self.progress_label = ttk.Label(progress_frame, text="Ready to start operation")
        self.progress_label.pack(anchor="w", pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Progress percentage label
        self.progress_percent = ttk.Label(progress_frame, text="0%", font=("Segoe UI", 9, "bold"))
        self.progress_percent.pack(anchor="w", pady=(0, 5))
        
        # Operation status
        self.operation_status_label = ttk.Label(progress_frame, text="Status: Idle", font=("Segoe UI", 9, "italic"))
        self.operation_status_label.pack(anchor="w")
        
        # Real-time monitoring options
        options_frame = ttk.LabelFrame(main_frame, text="Monitoring Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-refresh performance metrics", 
                       variable=self.auto_refresh_var).pack(anchor="w")
        
        self.show_detailed_progress = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Show detailed file progress", 
                       variable=self.show_detailed_progress).pack(anchor="w")
        
        # Operation Summary Display (added for completion summary)
        summary_frame = ttk.LabelFrame(main_frame, text="Operation Summary", padding="10")
        summary_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.summary_text = tk.Text(summary_frame, height=12, wrap=tk.WORD, 
                                    font=("Consolas", 9), relief=tk.SUNKEN, bg="#f5f5f5")
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.summary_text.tag_configure("success", foreground="green", font=("Consolas", 9, "bold"))
        self.summary_text.tag_configure("warning", foreground="orange", font=("Consolas", 9, "bold"))
        self.summary_text.tag_configure("error", foreground="red", font=("Consolas", 9, "bold"))
        self.summary_text.tag_configure("header", foreground="navy", font=("Consolas", 10, "bold"))
        
        # Initial message
        self.summary_text.insert(tk.END, "Ready to start operation.\n\n")
        self.summary_text.insert(tk.END, "Operation summary will appear here after completion.", "header")
        self.summary_text.config(state=tk.DISABLED)
        
        # Performance tips
        tips_frame = ttk.LabelFrame(main_frame, text="Performance Tips", padding="10")
        tips_frame.pack(fill=tk.BOTH, expand=True)
        
        tips_text = tk.Text(tips_frame, height=6, wrap=tk.WORD, font=("Segoe UI", 9), 
                           relief=tk.FLAT, bg=self.root['bg'])
        tips_text.pack(fill=tk.BOTH, expand=True)
        
        tips_content = """💡 Performance Tips:
• Use /MT:16-32 for optimal multi-threading on modern systems
• Enable /J (unbuffered I/O) for large files on fast storage
• Monitor network usage when copying over network connections
• Use /DCOPY:T to preserve directory timestamps efficiently
• Consider /NOOFFLOAD for better compatibility with some storage systems"""
        
        tips_text.insert(tk.END, tips_content)
        tips_text.config(state=tk.DISABLED)
    
    def create_logs_tab(self):
        """Create logs and history tab"""
        main_frame = ttk.Frame(self.logs_tab, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log viewer
        log_frame = ttk.LabelFrame(main_frame, text="Operation Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(log_controls, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(log_controls, text="Refresh", command=self.refresh_log).pack(side=tk.LEFT)
        
        # Log text area with enhanced formatting
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD, 
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure log text tags for colored output
        self.log_text.tag_configure("error", foreground="red", font=("Consolas", 9, "bold"))
        self.log_text.tag_configure("warning", foreground="orange", font=("Consolas", 9, "bold"))
        self.log_text.tag_configure("info", foreground="blue")
        self.log_text.tag_configure("success", foreground="green", font=("Consolas", 9, "bold"))
        
        # Command history
        history_frame = ttk.LabelFrame(main_frame, text="Command History", padding="10")
        history_frame.pack(fill=tk.X)
        
        self.history_listbox = tk.Listbox(history_frame, height=5, font=("Consolas", 9))
        self.history_listbox.pack(fill=tk.X, pady=(0, 5))
        
        history_controls = ttk.Frame(history_frame)
        history_controls.pack(fill=tk.X)
        
        ttk.Button(history_controls, text="Load Selected", command=self.load_from_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(history_controls, text="Clear History", command=self.clear_history).pack(side=tk.LEFT)
    
    def create_status_bar(self):
        """Create status bar at bottom of window"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Version label
        version_label = ttk.Label(status_frame, text="Advanced ROBOCOPY GUI v2.0", relief=tk.SUNKEN)
        version_label.pack(side=tk.RIGHT, padx=(0, 5))
    
    def start_performance_timer(self):
        """Start the performance metrics update timer"""
        # Update both detailed and main progress displays
        self.update_performance_display()
        
        # Also update main elapsed time if operation is running
        if hasattr(self, 'operation_start_time') and self.operation_start_time and hasattr(self, 'time_label'):
            elapsed_seconds = time.time() - self.operation_start_time
            elapsed_str = self.format_time(elapsed_seconds)
            self.time_label.config(text=f"Elapsed: {elapsed_str}")
        
        # Schedule next update in 1 second
        self.root.after(1000, self.start_performance_timer)
    
    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def format_bytes(self, bytes_value):
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def update_performance_stats(self):
        """Update performance statistics during operation with smart scheduling"""
        if hasattr(self, 'files_processed_label') and hasattr(self, 'performance_stats'):
            # Only update if operation is running
            if self.operation_start_time and self.current_process and self.current_process.poll() is None:
                # Update file and directory counts
                self.files_processed_label.config(text=f"Files Processed: {self.performance_stats['files_copied']}")
                self.dirs_processed_label.config(text=f"Directories: {self.performance_stats['dirs_copied']}")
                
                # Format bytes using the new method
                bytes_copied = self.performance_stats['bytes_copied']
                size_str = self.format_bytes(bytes_copied)
                self.bytes_copied_label.config(text=f"Data Copied: {size_str}")
                
                # Calculate and display speed
                if self.operation_start_time:
                    elapsed = time.time() - self.operation_start_time
                    if elapsed > 1:  # Avoid division by zero and initial fluctuations
                        speed_bps = bytes_copied / elapsed
                        speed_mbps = speed_bps / (1024 * 1024)
                        self.performance_stats['speed_mbps'] = speed_mbps
                        if hasattr(self, 'copy_speed_label'):
                            self.copy_speed_label.config(text=f"Speed: {speed_mbps:.1f} MB/s")
                
                # Update elapsed time
                if self.operation_start_time:
                    elapsed = time.time() - self.operation_start_time
                    elapsed_str = self.format_time(elapsed)
                    if hasattr(self, 'elapsed_time_label'):
                        self.elapsed_time_label.config(text=f"Elapsed: {elapsed_str}")
                
                # Update operation status
                if hasattr(self, 'operation_status_label'):
                    self.operation_status_label.config(text="Status: Operation in progress...")
                
                # Schedule faster updates during operation
                self.root.after(500, self.update_performance_stats)
            else:
                # Reset status when not running
                if hasattr(self, 'operation_status_label'):
                    self.operation_status_label.config(text="Status: Idle")
                
                # Schedule slower updates when idle
                self.root.after(2000, self.update_performance_stats)
        else:
            # Schedule next update
            self.root.after(1000, self.update_performance_stats)
    
    def create_additional_options(self, parent):
        """Create additional option controls"""
        additional_frame = ttk.LabelFrame(parent, text="Additional Options")
        additional_frame.grid(row=0, column=1, sticky="new", padx=(5, 0))
        additional_frame.columnconfigure(1, weight=1)
        
        # Retry options
        ttk.Label(additional_frame, text="Retries:").grid(row=0, column=0, sticky="w")
        self.retries = tk.StringVar(value="3")
        ttk.Entry(additional_frame, textvariable=self.retries, width=10).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(additional_frame, text="Wait time (sec):").grid(row=1, column=0, sticky="w")
        self.wait_time = tk.StringVar(value="30")
        ttk.Entry(additional_frame, textvariable=self.wait_time, width=10).grid(row=1, column=1, sticky="w", padx=5)
        
        # Threading
        ttk.Label(additional_frame, text="Threads:").grid(row=2, column=0, sticky="w")
        self.threads = tk.StringVar(value="8")
        ttk.Entry(additional_frame, textvariable=self.threads, width=10).grid(row=2, column=1, sticky="w", padx=5)
        
        # Additional flags
        self.purge_dest = tk.BooleanVar()
        self.exclude_changed = tk.BooleanVar()
        self.exclude_newer = tk.BooleanVar()
        self.verbose = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(additional_frame, text="Purge destination (/PURGE)", 
                       variable=self.purge_dest).grid(row=3, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(additional_frame, text="Exclude changed files (/XC)", 
                       variable=self.exclude_changed).grid(row=4, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(additional_frame, text="Exclude newer files (/XN)", 
                       variable=self.exclude_newer).grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(additional_frame, text="Verbose output (/V)", 
                       variable=self.verbose).grid(row=6, column=0, columnspan=2, sticky="w")
    
    def browse_source(self):
        """Browse for source directory"""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_path.set(directory)
            self.generate_command()
    
    def browse_dest(self):
        """Browse for destination directory"""
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dest_path.set(directory)
            self.generate_command()
    
    def fix_remove_security(self):
        """Remove security-related copy flags that cause permission errors"""
        self.copy_security.set(False)
        self.copy_attributes.set(False)
        self.generate_command()
        messagebox.showinfo("Permission Fix", "Removed /SEC and /COPYALL flags. These copy NTFS security permissions which often cause ERROR 5.")
    
    def fix_remove_dcopy(self):
        """Remove directory timestamp copy flag"""
        self.copy_timestamps.set(False)
        self.generate_command()
        messagebox.showinfo("Permission Fix", "Removed /DCOPY:T flag. This copies directory timestamps which may require special permissions.")
    
    def fix_basic_copy(self):
        """Set up basic copy without advanced permissions"""
        self.copy_security.set(False)
        self.copy_attributes.set(False)
        self.copy_timestamps.set(False)
        self.generate_command()
        messagebox.showinfo("Permission Fix", "Switched to basic copy mode. Files will be copied without security attributes or timestamps.")
    
    def show_admin_instructions(self):
        """Show instructions for running as administrator"""
        instructions = """To run ROBOCOPY with Administrator privileges:

1. Close this application
2. Right-click on Command Prompt or PowerShell
3. Select "Run as administrator"
4. Navigate to: {}
5. Run: python robocopy_gui.py

OR

1. Right-click on robocopy_gui.py
2. Select "Run as administrator" (if available)

Administrator privileges allow copying NTFS security permissions and accessing protected files.""".format(os.getcwd())
        
        messagebox.showinfo("Administrator Instructions", instructions)
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Output cleared.\n", "info")
        self.update_line_count()
        self.logger.info("Output area cleared by user")
    
    def copy_output(self):
        """Copy all output text to clipboard"""
        try:
            output_content = self.output_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(output_content)
            self.output_text.insert(tk.END, "\n📋 Output copied to clipboard\n", "info")
            if hasattr(self, 'auto_scroll') and self.auto_scroll.get():
                self.output_text.see(tk.END)
            self.update_line_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy output: {str(e)}")
    
    def update_line_count(self):
        """Update the line count display"""
        try:
            if hasattr(self, 'line_count_label') and hasattr(self, 'output_text'):
                # Get the number of lines in the text widget
                line_count = int(self.output_text.index('end-1c').split('.')[0]) - 1
                self.line_count_label.config(text=f"Lines: {line_count}")
        except Exception as e:
            pass  # Silently ignore errors in line counting
    
    
    def generate_command(self):
        """Generate ROBOCOPY command based on current settings with advanced options"""
        if not self.source_path.get() or not self.dest_path.get():
            self.command_display.config(text="Please select source and destination directories.", foreground="red")
            return
        
        cmd = ["robocopy", f'"{self.source_path.get()}"', f'"{self.dest_path.get()}"']
        
        # Add file specifications if any
        # cmd.append("*.*")  # Default to all files
        
        # Add copy options
        if self.mirror_mode.get():
            cmd.append("/MIR")
        else:
            if self.copy_subdirs.get():
                cmd.append("/S")
            if self.copy_empty_subdirs.get():
                cmd.append("/E")
        
        if self.copy_attributes.get():
            cmd.append("/COPYALL")
        if self.copy_timestamps.get():
            cmd.append("/DCOPY:T")
        if self.copy_security.get():
            cmd.append("/SEC")
        
        # Advanced options
        if hasattr(self, 'move_files') and self.move_files.get():
            cmd.append("/MOV")
        
        if hasattr(self, 'purge_dest') and self.purge_dest.get():
            cmd.append("/PURGE")
        
        if hasattr(self, 'exclude_changed') and self.exclude_changed.get():
            cmd.append("/XC")
        
        if hasattr(self, 'exclude_newer') and self.exclude_newer.get():
            cmd.append("/XN")
        
        if hasattr(self, 'exclude_older') and self.exclude_older.get():
            cmd.append("/XO")
        
        if hasattr(self, 'only_newer') and self.only_newer.get():
            cmd.append("/XL")
        
        # Performance options with validation - using colon syntax
        retries_val = self.retries.get().strip() if self.retries.get() else ""
        if retries_val and retries_val.isdigit() and int(retries_val) > 0:
            cmd.append(f"/R:{retries_val}")
        
        wait_val = self.wait_time.get().strip() if self.wait_time.get() else ""
        if wait_val and wait_val.isdigit() and int(wait_val) > 0:
            cmd.append(f"/W:{wait_val}")
        
        threads_val = self.threads.get().strip() if self.threads.get() else ""
        if threads_val and threads_val.isdigit() and int(threads_val) > 1:
            cmd.append(f"/MT:{threads_val}")
        
        # Logging options
        if hasattr(self, 'verbose') and self.verbose.get():
            cmd.append("/V")
        
        if hasattr(self, 'list_only') and self.list_only.get():
            cmd.append("/L")
        
        if hasattr(self, 'create_log') and self.create_log.get():
            cmd.extend(["/LOG+:robocopy_operation.log"])
        
        # Always add these for better output (unless show_progress is disabled)
        cmd.append("/TEE")
        if not (hasattr(self, 'show_progress') and self.show_progress.get()):
            cmd.append("/NP")
        
        # Performance optimization flags
        cmd.append("/J")  # Unbuffered I/O for large files
        cmd.append("/NOOFFLOAD")  # Disable Windows copy offload mechanism
        
        command_str = " ".join(cmd)
        self.command_display.config(text=command_str, foreground="blue")
        
        # Add to history with timestamp
        if hasattr(self, 'history_listbox'):
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            history_entry = f"[{timestamp}] {command_str}"
            self.history_listbox.insert(0, history_entry)
            if self.history_listbox.size() > 20:  # Keep only last 20 commands
                self.history_listbox.delete(20, tk.END)
            
            # Also save to history file
            self.save_command_history(history_entry)
        
        self.logger.info(f"Generated command: {command_str}")
        self.update_status("Command generated successfully")
        
        # Store command for execution
        self.current_command = command_str
    
    def start_keepalive(self):
        """Start GUI keep-alive mechanism to prevent freezing during long operations"""
        self.keepalive_gui()
    
    def keepalive_gui(self):
        """Periodic GUI update to keep interface responsive"""
        try:
            # Force GUI to process events
            self.root.update_idletasks()
        except Exception as e:
            self.logger.error(f"Error in GUI keep-alive: {e}")
        
        # Schedule next keep-alive check every 50ms
        self.root.after(50, self.keepalive_gui)
    
    def execute_command(self):
        """Execute the generated ROBOCOPY command with validation"""
        command = getattr(self, 'current_command', '')
        if not command or "Please select" in command:
            messagebox.showerror("Error", "Please generate a valid command first.")
            return
        
        if self.current_process and self.current_process.poll() is None:
            messagebox.showwarning("Warning", "A command is already running. Please stop it first.")
            return
        
        # Validate command parameters - updated for colon syntax
        if "/W:" in command:
            # Check if /W: parameter has a valid value
            parts = command.split()
            w_param = None
            for part in parts:
                if part.startswith("/W:"):
                    w_param = part[3:]  # Extract value after /W:
                    break
            
            if w_param is None:
                messagebox.showerror("Error", "Invalid /W parameter: missing wait time value")
                return
            
            if not w_param.isdigit() or int(w_param) <= 0:
                messagebox.showerror("Error", f"Invalid /W parameter: '{w_param}' is not a valid wait time")
                return
        
        # Similar validation for /R parameter
        if "/R:" in command:
            parts = command.split()
            r_param = None
            for part in parts:
                if part.startswith("/R:"):
                    r_param = part[3:]  # Extract value after /R:
                    break
            
            if r_param is None:
                messagebox.showerror("Error", "Invalid /R parameter: missing retry count value")
                return
            
            if not r_param.isdigit():
                messagebox.showerror("Error", f"Invalid /R parameter: '{r_param}' is not a valid retry count")
                return
        
        # Similar validation for /MT parameter
        if "/MT:" in command:
            parts = command.split()
            mt_param = None
            for part in parts:
                if part.startswith("/MT:"):
                    mt_param = part[4:]  # Extract value after /MT:
                    break
            
            if mt_param is None:
                messagebox.showerror("Error", "Invalid /MT parameter: missing thread count value")
                return
            
            if not mt_param.isdigit() or int(mt_param) <= 0:
                messagebox.showerror("Error", f"Invalid /MT parameter: '{mt_param}' is not a valid thread count")
                return
        
        # Clear any previous process state
        if self.current_process:
            try:
                if self.current_process.poll() is None:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=1)
            except:
                pass
        self.current_process = None
        self.operation_in_progress = False
        
        # Clear output
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Executing: {command}\n\n", "command")
        
        # Start progress bar (check if Basic Settings progress bar exists)
        if hasattr(self, 'progress'):
            self.progress.start()
        if hasattr(self, 'progress_label'):
            self.progress_label.config(text="Operation in progress...")
        
        # Force GUI update before starting operation
        self.root.update_idletasks()
        
        # Mark operation as in progress
        self.operation_in_progress = True
        
        self.logger.info("Starting new operation - old state cleared")
        
        # Execute command in thread
        threading.Thread(target=self.run_command, args=(command,), daemon=True).start()
        self.update_status("Command execution started")
        
        # Force GUI update after starting thread
        self.root.update_idletasks()
    
    def run_command(self, command):
        """Enhanced command execution with performance tracking"""
        try:
            self.logger.info(f"Executing command: {command}")
            self.operation_in_progress = True
            
            # Initialize performance tracking
            self.operation_start_time = time.time()
            self.performance_stats = {
                'files_copied': 0,
                'dirs_copied': 0,
                'bytes_copied': 0,
                'total_files': 0,
                'speed_mbps': 0.0,
                'errors': 0
            }
            
            self.logger.info(f"Performance tracking initialized at {self.operation_start_time}")
            
            # Reset progress bar to determinate mode for real progress tracking
            if hasattr(self, 'progress'):
                self.progress.config(mode='determinate', maximum=100, value=0)
                self.logger.debug("Main progress bar reset to determinate mode")
            
            # Reset main progress percentage label
            if hasattr(self, 'progress_percent'):
                self.progress_percent.config(text="0%")
            
            # Reset main progress label
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text="Starting operation...")
            
            # Reset main elapsed time
            if hasattr(self, 'time_label'):
                self.time_label.config(text="Elapsed: 00:00:00")
            
            # Reset performance labels if they exist
            if hasattr(self, 'files_processed_label'):
                self.files_processed_label.config(text="Files Processed: 0")
            if hasattr(self, 'dirs_processed_label'):
                self.dirs_processed_label.config(text="Directories: 0")
            if hasattr(self, 'bytes_copied_label'):
                self.bytes_copied_label.config(text="Data Copied: 0 B")
            if hasattr(self, 'copy_speed_label'):
                self.copy_speed_label.config(text="Speed: 0.0 MB/s")
            if hasattr(self, 'eta_label'):
                self.eta_label.config(text="ETA: Calculating...")
            
            self.logger.debug("All performance labels reset")
            
            # Use shell=True for Windows compatibility
            self.current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.logger.info(f"Process started with PID: {self.current_process.pid}")
            
            # Start output reading thread
            threading.Thread(target=self.read_output, daemon=True).start()
            
            # Start checking output queue
            self.check_output_queue()
            
            return_code = self.current_process.wait()
            
            # ROBOCOPY Return Codes:
            # 0 = No files copied. No failure was encountered.
            # 1 = Files copied successfully. No failure was encountered.
            # 2 = Some Extra files or directories were detected.
            # 4 = Some Mismatched files or directories were detected.
            # 8 = Some files or directories could not be copied.
            # 16 = Serious error. Robocopy did not copy any files.
            
            if return_code == 0:
                self.output_queue.put(('success', "\n✅ Operation completed successfully! (No files needed copying)\n"))
                self.logger.info("Operation completed successfully - no files copied")
            elif return_code == 1:
                self.output_queue.put(('success', "\n✅ Operation completed successfully! (Files copied)\n"))
                self.logger.info("Operation completed successfully - files copied")
            elif return_code == 2:
                self.output_queue.put(('success', "\n✅ Operation completed successfully! (Extra files detected)\n"))
                self.logger.info("Operation completed successfully - extra files detected")
            elif return_code == 3:  # 1 + 2
                self.output_queue.put(('success', "\n✅ Operation completed successfully! (Files copied + extra files detected)\n"))
                self.logger.info("Operation completed successfully - files copied and extra files detected")
            elif return_code == 4:
                self.output_queue.put(('warning', "\n⚠️ Operation completed with warnings (Mismatched files detected)\n"))
                self.logger.warning("Operation completed with warnings - mismatched files detected")
            elif return_code == 5:  # 1 + 4
                self.output_queue.put(('warning', "\n⚠️ Operation completed with warnings (Files copied + mismatched files)\n"))
                self.logger.warning("Operation completed with warnings - files copied and mismatched files")
            elif return_code == 6:  # 2 + 4
                self.output_queue.put(('warning', "\n⚠️ Operation completed with warnings (Extra + mismatched files)\n"))
                self.logger.warning("Operation completed with warnings - extra and mismatched files")
            elif return_code == 7:  # 1 + 2 + 4
                self.output_queue.put(('warning', "\n⚠️ Operation completed with warnings (Files copied + extra + mismatched)\n"))
                self.logger.warning("Operation completed with warnings - files copied, extra and mismatched files")
            elif return_code == 8:
                self.output_queue.put(('error', "\n❌ Some files could not be copied (copy errors occurred)\n"))
                self.logger.error("Some files could not be copied")
            elif return_code >= 16:
                self.output_queue.put(('error', f"\n❌ Serious error occurred! Return code: {return_code}\n"))
                self.logger.error(f"Serious error occurred with return code: {return_code}")
            else:
                # Handle combinations with 8 (copy errors)
                if return_code & 8:  # Bitwise check for copy errors
                    self.output_queue.put(('error', f"\n❌ Operation completed with copy errors! Return code: {return_code}\n"))
                    self.logger.error(f"Operation completed with copy errors - return code: {return_code}")
                else:
                    self.output_queue.put(('warning', f"\n⚠️ Operation completed with warnings! Return code: {return_code}\n"))
                    self.logger.warning(f"Operation completed with warnings - return code: {return_code}")
            
            # Display Operation Summary after completion
            self.show_operation_summary(return_code)
                    
        except Exception as e:
            error_msg = f"\n❌ Error executing command: {str(e)}\n"
            self.output_queue.put(('error', error_msg))
            self.logger.error(f"Error executing command: {str(e)}")
        finally:
            self.output_queue.put(('control', 'STOP_PROGRESS'))
            self.operation_in_progress = False  # Mark operation as complete
            self.current_process = None  # Clear process reference
            self.operation_start_time = None  # Clear start time
            self.logger.info("Operation completed, flags cleared and process reference removed")
    
    def read_output(self):
        """Read output from subprocess in a separate thread"""
        try:
            if self.current_process and self.current_process.stdout:
                for line in iter(self.current_process.stdout.readline, ''):
                    if line:
                        clean_line = line.rstrip('\n\r')
                        self.output_queue.put(clean_line)
                self.current_process.stdout.close()
        except Exception as e:
            logging.error(f"Error reading output: {e}")
    
    def format_output_line(self, line):
        """Format output line with appropriate styling markers and error detection"""
        # Detect ERROR 5 (Access Denied) and provide helpful information
        if "ERROR 5 (0x00000005)" in line and "Access is denied" in line:
            # Extract the operation type and file path
            if "Copying NTFS Security" in line:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Try removing /SEC and /COPYALL flags, or run as Administrator"
            elif "Copying Directory" in line:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Check destination permissions or try without /DCOPY:T flag"
            else:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Run as Administrator or check file/folder permissions"
        
        # Add color coding markers for different types of output
        elif "ERROR" in line.upper() or "FAILED" in line.upper():
            # Check for specific error types
            if "Access is denied" in line:
                return f"[PERMISSION_ERROR] {line}\n[SOLUTION] Check permissions or run as Administrator"
            elif "disk full" in line.lower():
                return f"[DISK_ERROR] {line}\n[SOLUTION] Free up disk space on destination"
            elif "path not found" in line.lower():
                return f"[PATH_ERROR] {line}\n[SOLUTION] Verify source and destination paths exist"
            else:
                return f"[ERROR] {line}"
        elif "WARNING" in line.upper() or "EXTRA" in line:
            return f"[WARNING] {line}"
        elif "New File" in line or "Newer" in line or "Modified" in line:
            return f"[SUCCESS] {line}"
        elif "New Dir" in line:
            return f"[INFO] {line}"
        elif "Total" in line and "Copied" in line:
            return f"[SUMMARY] {line}"
        elif "Retrying..." in line:
            return f"[RETRY] {line}"
        elif "Waiting" in line and "seconds" in line:
            return f"[WAIT] {line}"
        else:
            return line
    
    def update_performance_display(self):
        """Enhanced update performance display with real-time data"""
        if not hasattr(self, 'current_process') or not self.current_process:
            return
            
        try:
            # Update elapsed time in both locations
            if hasattr(self, 'operation_start_time') and self.operation_start_time:
                elapsed_seconds = time.time() - self.operation_start_time
                elapsed_str = self.format_time(elapsed_seconds)
                # Update main progress area elapsed time
                if hasattr(self, 'time_label'):
                    self.time_label.config(text=f"Elapsed: {elapsed_str}")
                # Update detailed metrics elapsed time
                if hasattr(self, 'elapsed_time_label'):
                    self.elapsed_time_label.config(text=f"Elapsed: {elapsed_str}")
            
            # Update performance metrics from parsed output
            if hasattr(self, 'performance_stats'):
                stats = self.performance_stats
                
                # Update files processed using the correct label name
                files_text = f"Files Processed: {stats.get('files_copied', 0)}"
                if hasattr(self, 'files_processed_label'):
                    self.files_processed_label.config(text=files_text)
                
                # Update directories processed using the correct label name  
                dirs_text = f"Directories: {stats.get('dirs_copied', 0)}"
                if hasattr(self, 'dirs_processed_label'):
                    self.dirs_processed_label.config(text=dirs_text)
                
                # Update data copied using the correct label name
                bytes_copied = stats.get('bytes_copied', 0)
                data_text = f"Data Copied: {self.format_bytes(bytes_copied)}"
                if hasattr(self, 'bytes_copied_label'):
                    self.bytes_copied_label.config(text=data_text)
                
                # Update speed using the correct label name
                speed = stats.get('speed_mbps', 0)
                speed_text = f"Speed: {speed:.1f} MB/s"
                if hasattr(self, 'copy_speed_label'):
                    self.copy_speed_label.config(text=speed_text)
                
                # Calculate and update progress percentage in BOTH locations
                total_files = stats.get('total_files', 0)
                files_copied = stats.get('files_copied', 0)
                if total_files > 0 and files_copied >= 0:
                    progress_percent = min(100, (files_copied / total_files) * 100)
                    
                    # Update MAIN progress bar (in Output & Progress section)
                    if hasattr(self, 'progress'):
                        self.progress.config(mode='determinate', maximum=100, value=progress_percent)
                    
                    # Update MAIN progress percentage label
                    if hasattr(self, 'progress_percent'):
                        self.progress_percent.config(text=f"{progress_percent:.1f}%")
                    
                    # Update MAIN progress label with detailed info
                    if hasattr(self, 'progress_label'):
                        if progress_percent >= 100:
                            self.progress_label.config(text=f"Operation Complete - {files_copied} files processed")
                        else:
                            self.progress_label.config(text=f"Processing: {progress_percent:.1f}% ({files_copied}/{total_files} files)")
                
                # Calculate ETA using the correct label name
                if hasattr(self, 'eta_label') and speed > 0 and total_files > 0 and files_copied > 0:
                    remaining_files = total_files - files_copied
                    if remaining_files > 0:
                        # Estimate based on current speed and remaining work
                        avg_file_size = bytes_copied / files_copied if files_copied > 0 else 1024
                        remaining_bytes = remaining_files * avg_file_size
                        eta_seconds = remaining_bytes / (speed * 1024 * 1024)  # Convert MB/s to bytes/s
                        eta_str = self.format_time(eta_seconds)
                        self.eta_label.config(text=f"ETA: {eta_str}")
                    else:
                        self.eta_label.config(text="ETA: Complete")
                elif hasattr(self, 'eta_label'):
                    self.eta_label.config(text="ETA: Calculating...")
                
                # Update operation status with current stats
                if hasattr(self, 'operation_status_label'):
                    if total_files > 0:
                        progress_percent = (files_copied / total_files) * 100
                        status_text = f"Status: {progress_percent:.1f}% Complete - {files_copied}/{total_files} files, {self.format_bytes(bytes_copied)}"
                    else:
                        status_text = f"Status: Processing - {files_copied} files, {self.format_bytes(bytes_copied)}"
                    self.operation_status_label.config(text=status_text)
        
        except Exception as e:
            logging.error(f"Error updating performance display: {e}")

    def parse_robocopy_output(self, line):
        """Enhanced parser for ROBOCOPY output to extract performance metrics"""
        try:
            if not hasattr(self, 'performance_stats'):
                self.performance_stats = {
                    'files_copied': 0,
                    'dirs_copied': 0,
                    'bytes_copied': 0,
                    'total_files': 0,
                    'speed_mbps': 0.0,
                    'errors': 0
                }
            
            import re
            original_line = line  # Keep original for debug
            
            # Parse file copy progress - Updated for actual ROBOCOPY format
            # Format: "    New File               24000        test_file_0.txt"
            if "New File" in line and "\t" in line:
                # Extract file size using regex for tab-separated format
                size_match = re.search(r'New File\s+(\d+)\s+', line)
                if size_match:
                    file_size = int(size_match.group(1))
                    self.performance_stats['bytes_copied'] += file_size
                    self.performance_stats['files_copied'] += 1
                    self.logger.debug(f"Parsed file copy: {file_size} bytes, total files: {self.performance_stats['files_copied']}, total bytes: {self.performance_stats['bytes_copied']}")
                    
                    # Update main progress if we have total files count
                    if self.performance_stats.get('total_files', 0) > 0:
                        progress = (self.performance_stats['files_copied'] / self.performance_stats['total_files']) * 100
                        
                        # Update MAIN progress bar
                        if hasattr(self, 'progress'):
                            self.progress.config(mode='determinate', maximum=100, value=progress)
                        
                        # Update MAIN progress percentage label
                        if hasattr(self, 'progress_percent'):
                            self.progress_percent.config(text=f"{progress:.1f}%")
                        
                        # Update MAIN progress label
                        if hasattr(self, 'progress_label'):
                            files_copied = self.performance_stats['files_copied']
                            total_files = self.performance_stats['total_files']
                            if progress >= 100:
                                self.progress_label.config(text=f"Operation Complete - {files_copied} files processed")
                            else:
                                self.progress_label.config(text=f"Processing: {progress:.1f}% ({files_copied}/{total_files} files)")
                    
                    return  # Important: return to avoid duplicate processing
            
            # Parse directory creation - Updated format
            # Format: "  New Dir          3    C:\path\to\dir\"
            elif "New Dir" in line:
                self.performance_stats['dirs_copied'] += 1
                self.logger.debug(f"Parsed directory creation, total dirs: {self.performance_stats['dirs_copied']}")
                return
            
            # Parse files summary from final report
            # Format: "   Files :         8         8         0         0         0         0"
            elif line.strip().startswith("Files :"):
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 2:
                    total_files = int(numbers[0])  # First number is total files
                    copied_files = int(numbers[1])  # Second number is copied files
                    self.performance_stats['total_files'] = total_files
                    # Update files copied from summary (more accurate than counting)
                    self.performance_stats['files_copied'] = copied_files
                    self.logger.info(f"Parsed files summary: {copied_files}/{total_files} files")
                    
                    # Update main progress immediately when we get totals
                    if total_files > 0:
                        progress = (copied_files / total_files) * 100
                        
                        # Update MAIN progress bar
                        if hasattr(self, 'progress'):
                            self.progress.config(mode='determinate', maximum=100, value=progress)
                        
                        # Update MAIN progress percentage label
                        if hasattr(self, 'progress_percent'):
                            self.progress_percent.config(text=f"{progress:.1f}%")
                        
                        # Update MAIN progress label
                        if hasattr(self, 'progress_label'):
                            if progress >= 100:
                                self.progress_label.config(text=f"Operation Complete - {copied_files} files processed")
                            else:
                                self.progress_label.config(text=f"Processing: {progress:.1f}% ({copied_files}/{total_files} files)")
                        
                        self.logger.info(f"Main progress updated to {progress:.1f}%")
                    return
            
            # Parse bytes summary 
            # Format: "   Bytes :   165.5 k   165.5 k         0         0         0         0"
            elif line.strip().startswith("Bytes :"):
                # Extract the first size value (total bytes)
                size_match = re.search(r'Bytes :\s+([0-9.,]+\s*[kmgt]?)', line, re.IGNORECASE)
                if size_match:
                    size_str = size_match.group(1).strip()
                    bytes_copied = self.parse_size_string(size_str)
                    if bytes_copied > 0:
                        self.performance_stats['bytes_copied'] = bytes_copied
                        self.logger.info(f"Parsed bytes summary: {bytes_copied} bytes ({size_str})")
                        return
            
            # Parse speed information
            # Format: "   Speed :               606.179 MegaBytes/min."
            elif "Speed :" in line and "MegaBytes/min" in line:
                speed_match = re.search(r'Speed :\s+([0-9.,]+)\s+MegaBytes/min', line)
                if speed_match:
                    speed_mb_per_min = float(speed_match.group(1).replace(',', ''))
                    # Convert MB/min to MB/s
                    self.performance_stats['speed_mbps'] = speed_mb_per_min / 60.0
                    self.logger.info(f"Parsed speed: {self.performance_stats['speed_mbps']:.2f} MB/s ({speed_mb_per_min} MB/min)")
                    return
            
            # Calculate progress percentage if we have total files
            if (self.performance_stats['total_files'] > 0 and 
                self.performance_stats['files_copied'] > 0):
                progress = (self.performance_stats['files_copied'] / self.performance_stats['total_files']) * 100
                
                # Update MAIN progress bar (in Output & Progress section) IMMEDIATELY
                if hasattr(self, 'progress'):
                    self.progress.config(mode='determinate', maximum=100, value=progress)
                
                # Update MAIN progress percentage label IMMEDIATELY
                if hasattr(self, 'progress_percent'):
                    self.progress_percent.config(text=f"{progress:.1f}%")
                
                # Update MAIN progress label with detailed info IMMEDIATELY
                if hasattr(self, 'progress_label'):
                    files_copied = self.performance_stats['files_copied']
                    total_files = self.performance_stats['total_files']
                    if progress >= 100:
                        self.progress_label.config(text=f"Operation Complete - {files_copied} files processed")
                    else:
                        self.progress_label.config(text=f"Processing: {progress:.1f}% ({files_copied}/{total_files} files)")
                
                self.logger.debug(f"Progress updated immediately: {progress:.1f}%")
        
        except Exception as e:
            logging.error(f"Error parsing ROBOCOPY output line '{line}': {e}")
    
    def parse_size_string(self, size_str):
        """Parse size strings like '165.5 k' into bytes"""
        try:
            import re
            # Remove commas and extra spaces
            size_str = size_str.replace(',', '').strip()
            
            # Extract number and unit
            match = re.match(r'([0-9.]+)\s*([kmgt]?)', size_str.lower())
            if not match:
                return 0
            
            number = float(match.group(1))
            unit = match.group(2) if match.group(2) else ''
            
            multipliers = {
                '': 1,
                'k': 1024,
                'm': 1024**2,
                'g': 1024**3,
                't': 1024**4
            }
            
            return int(number * multipliers.get(unit, 1))
        except:
            return 0
    
    def check_output_queue(self):
        """Enhanced output queue processing with real-time metrics and GUI responsiveness"""
        try:
            processed_lines = 0
            max_lines_per_update = 10  # Process max 10 lines per GUI update cycle to keep responsive
            max_output_lines = 5000  # Limit output text to 5000 lines to prevent memory issues
            
            while not self.output_queue.empty() and processed_lines < max_lines_per_update:
                item = self.output_queue.get_nowait()
                processed_lines += 1
                
                # Handle both tuple (msg_type, text) and plain string messages
                if isinstance(item, tuple) and len(item) == 2:
                    msg_type, line = item
                    # Handle control messages
                    if msg_type == 'control':
                        if line == 'STOP_PROGRESS':
                            # Progress stopped - handled elsewhere
                            pass
                        continue
                else:
                    # Plain string message (legacy format)
                    line = item
                
                # Parse the line for performance metrics
                self.parse_robocopy_output(line)
                
                # Format and display the line
                formatted_line = self.format_output_line(line)
                
                # Add to output display
                self.output_text.insert(tk.END, formatted_line + "\n")
                
                # Limit output text size to prevent memory issues and GUI freezing
                line_count = int(self.output_text.index('end-1c').split('.')[0])
                if line_count > max_output_lines:
                    # Delete oldest 100 lines to keep buffer manageable
                    self.output_text.delete(1.0, "100.0")
                
                # Auto-scroll if enabled
                if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                    self.output_text.see(tk.END)
                
                # Update line count
                if hasattr(self, 'line_count_label'):
                    self.line_count_label.config(text=f"Lines: {line_count}")
            
            # Update performance display after processing lines
            if processed_lines > 0:
                self.update_performance_display()
                # Force GUI update to prevent freezing
                self.root.update_idletasks()
                
                # Debug: Log current stats (reduce logging frequency)
                if hasattr(self, 'performance_stats') and processed_lines >= max_lines_per_update:
                    stats = self.performance_stats
                    self.logger.debug(f"Performance update - Files: {stats.get('files_copied', 0)}/{stats.get('total_files', 0)}, "
                                    f"Bytes: {stats.get('bytes_copied', 0)}, Speed: {stats.get('speed_mbps', 0):.1f}")
        
        except queue.Empty:
            pass
        except Exception as e:
            logging.error(f"Error processing output queue: {e}")
        
        # Schedule next check - faster polling for better responsiveness
        if hasattr(self, 'current_process') and self.current_process:
            self.root.after(100, self.check_output_queue)  # Check every 100ms instead of 500ms

    def stop_command(self):
        """Stop the currently running command"""
        # Check if operation is in progress or process exists
        if self.operation_in_progress or (self.current_process and self.current_process.poll() is None):
            try:
                # Wait a moment for process to initialize if operation just started
                if self.operation_in_progress and not self.current_process:
                    self.logger.info("Operation starting, waiting for process initialization...")
                    import time
                    for _ in range(10):  # Wait up to 1 second
                        time.sleep(0.1)
                        if self.current_process:
                            break
                
                # Now check if we have a process to stop
                if self.current_process:
                    poll_result = self.current_process.poll()
                    if poll_result is None:
                        # Process is running - terminate it
                        self.logger.info("Attempting to stop running command...")
                        self.current_process.terminate()
                        
                        # Give process time to terminate gracefully
                        try:
                            self.current_process.wait(timeout=3)
                        except:
                            # Force kill if it doesn't terminate gracefully
                            self.logger.warning("Process did not terminate gracefully, forcing kill...")
                            self.current_process.kill()
                        
                        self.output_text.insert(tk.END, "\n🛑 Command stopped by user\n")
                        if hasattr(self, 'auto_scroll_var') and self.auto_scroll_var.get():
                            self.output_text.see(tk.END)
                        
                        # Reset progress
                        if hasattr(self, 'progress'):
                            self.progress.stop()
                            self.progress.config(mode='determinate', value=0)
                        
                        if hasattr(self, 'progress_label'):
                            self.progress_label.config(text="Operation stopped by user")
                        
                        # Stop the output queue checking and mark operation as complete
                        self.current_process = None
                        self.operation_in_progress = False
                        
                        self.logger.info("Command stopped by user")
                        self.update_status("Operation stopped")
                        messagebox.showinfo("Stopped", "Operation stopped successfully")
                    else:
                        # Process already finished
                        self.operation_in_progress = False
                        self.logger.info("Process has already finished")
                        messagebox.showinfo("Info", "Command has already completed.")
                else:
                    # Operation flag set but no process created yet
                    self.operation_in_progress = False
                    self.logger.warning("Operation flag was set but no process was created")
                    messagebox.showinfo("Info", "Operation was starting but could not be stopped.")
                    
            except Exception as e:
                self.operation_in_progress = False
                self.logger.error(f"Error stopping command: {str(e)}")
                messagebox.showerror("Error", f"Error stopping command: {str(e)}")
        else:
            messagebox.showinfo("Info", "No command is currently running.")
            self.logger.info("Stop button clicked but no process is running")
    
    def save_config(self):
        """Save current configuration to file"""
        config = {
            "source_path": self.source_path.get(),
            "dest_path": self.dest_path.get(),
            "copy_subdirs": self.copy_subdirs.get(),
            "copy_empty_subdirs": self.copy_empty_subdirs.get(),
            "copy_attributes": self.copy_attributes.get(),
            "copy_timestamps": self.copy_timestamps.get(),
            "copy_security": self.copy_security.get(),
            "mirror_mode": self.mirror_mode.get(),
            "retries": self.retries.get(),
            "wait_time": self.wait_time.get(),
            "threads": self.threads.get(),
            "purge_dest": self.purge_dest.get(),
            "exclude_changed": self.exclude_changed.get(),
            "exclude_newer": self.exclude_newer.get(),
            "verbose": self.verbose.get()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", f"Configuration saved to {self.config_file}")
            self.logger.info("Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            self.logger.error(f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.source_path.set(config.get("source_path", ""))
            self.dest_path.set(config.get("dest_path", ""))
            self.copy_subdirs.set(config.get("copy_subdirs", False))
            self.copy_empty_subdirs.set(config.get("copy_empty_subdirs", False))
            self.copy_attributes.set(config.get("copy_attributes", False))
            self.copy_timestamps.set(config.get("copy_timestamps", False))
            self.copy_security.set(config.get("copy_security", False))
            self.mirror_mode.set(config.get("mirror_mode", False))
            self.retries.set(config.get("retries", "3"))
            self.wait_time.set(config.get("wait_time", "30"))
            self.threads.set(config.get("threads", "8"))
            self.purge_dest.set(config.get("purge_dest", False))
            self.exclude_changed.set(config.get("exclude_changed", False))
            self.exclude_newer.set(config.get("exclude_newer", False))
            self.verbose.set(config.get("verbose", True))
            
            self.logger.info("Configuration loaded")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
    
    def load_config_file(self):
        """Load configuration from a selected file"""
        file_path = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.config_file = file_path
            self.load_config()
            messagebox.showinfo("Success", f"Configuration loaded from {file_path}")

    # ============================================================================
    # NEW ADVANCED METHODS
    # ============================================================================
    
    def new_config(self):
        """Create new configuration"""
        self.apply_preset("custom")
        self.source_path.set("")
        self.dest_path.set("")
        self.update_status("New configuration created")
    
    def save_config_as(self):
        """Save configuration to a selected file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Configuration As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.config_file = file_path
            self.save_config()
    
    def export_log(self):
        """Export current log to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                log_content = self.output_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("Success", f"Log exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export log: {str(e)}")
    
    def show_performance_monitor(self):
        """Switch to performance monitoring tab"""
        self.notebook.select(2)  # Select monitoring tab
    
    def show_command_history(self):
        """Switch to logs tab"""
        self.notebook.select(3)  # Select logs tab
    
    def validate_all_paths(self):
        """Validate source and destination paths"""
        messages = []
        
        # Validate source
        source = self.source_path.get()
        if not source:
            messages.append("❌ Source path is empty")
        elif not os.path.exists(source):
            messages.append("❌ Source path does not exist")
        elif not os.path.isdir(source):
            messages.append("❌ Source path is not a directory")
        else:
            messages.append("✅ Source path is valid")
        
        # Validate destination
        dest = self.dest_path.get()
        if not dest:
            messages.append("❌ Destination path is empty")
        else:
            if os.path.exists(dest):
                if os.path.isdir(dest):
                    messages.append("✅ Destination path exists and is valid")
                else:
                    messages.append("❌ Destination path exists but is not a directory")
            else:
                parent = os.path.dirname(dest)
                if os.path.exists(parent):
                    messages.append("✅ Destination will be created (parent exists)")
                else:
                    messages.append("❌ Destination parent directory does not exist")
        
        messagebox.showinfo("Path Validation", "\n".join(messages))
    
    def open_robocopy_docs(self):
        """Open ROBOCOPY documentation"""
        webbrowser.open("https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy")
    
    def show_user_guide(self):
        """Show user guide window"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        
        guide_text = scrolledtext.ScrolledText(guide_window, wrap=tk.WORD, padx=10, pady=10)
        guide_text.pack(fill=tk.BOTH, expand=True)
        
        guide_content = """
ROBOCOPY GUI Manager - User Guide

=== BASIC USAGE ===
1. Select source directory (where files are copied FROM)
2. Select destination directory (where files are copied TO)
3. Choose your copy options or use a preset
4. Click "Generate Command" to preview
5. Click "Execute" to start copying

=== PRESETS ===
• Backup: Complete backup with all attributes and security
• Sync/Mirror: Keep destination identical to source (deletes extra files!)
• Move: Move files (delete from source after copying)
• Custom: Start with no options selected

=== PERFORMANCE TIPS ===
• Use more threads (16-32) for many small files
• Use fewer threads (4-8) for large files
• Enable /MT for faster copying on modern systems
• Monitor performance in the Performance Monitor tab

=== SAFETY WARNINGS ===
⚠️ Mirror Mode: Will DELETE files in destination not in source
⚠️ Move Mode: Will DELETE files from source after copying
⚠️ Purge Option: Will DELETE extra files in destination

=== KEYBOARD SHORTCUTS ===
• Ctrl+N: New configuration
• Ctrl+O: Open configuration
• Ctrl+S: Save configuration
• F5: Refresh/Generate command
• Ctrl+E: Execute command
• Esc: Stop operation

=== TOOLTIPS ===
Hover over any option or button to see detailed help information.
        """
        
        guide_text.insert(tk.END, guide_content)
        guide_text.config(state=tk.DISABLED)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x300")
        
        shortcuts_text = scrolledtext.ScrolledText(shortcuts_window, wrap=tk.WORD, padx=10, pady=10)
        shortcuts_text.pack(fill=tk.BOTH, expand=True)
        
        shortcuts_content = """
Keyboard Shortcuts

File Operations:
Ctrl+N          New configuration
Ctrl+O          Open configuration
Ctrl+S          Save configuration
Ctrl+Shift+S    Save configuration as...
Ctrl+E          Export log

Operations:
F5              Generate/refresh command
Ctrl+Enter      Execute command
Esc             Stop current operation
Ctrl+L          List files only (test mode)

Navigation:
Ctrl+1          Basic Settings tab
Ctrl+2          Advanced Options tab
Ctrl+3          Performance Monitor tab
Ctrl+4          Logs & History tab

View:
Ctrl+Plus       Increase font size
Ctrl+Minus      Decrease font size
F11             Toggle fullscreen
        """
        
        shortcuts_text.insert(tk.END, shortcuts_content)
        shortcuts_text.config(state=tk.DISABLED)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About ROBOCOPY GUI Manager",
            "ROBOCOPY GUI Manager - Advanced Edition\n"
            "Version 2.0\n\n"
            "A comprehensive user-friendly interface for Windows ROBOCOPY\n"
            "command management with advanced features and performance monitoring.\n\n"
            "Features:\n"
            "• Intuitive tabbed interface\n"
            "• Real-time path validation\n"
            "• Performance monitoring\n"
            "• Command history\n"
            "• Helpful tooltips and guides\n"
            "• Multiple preset configurations\n"
            "• Enhanced error handling\n\n"
            "Developed for system administrators and power users.\n\n"
            "Developed by Sagar Sorathiya"
        )
    
    def show_operation_summary(self, return_code):
        """Display comprehensive operation summary after completion"""
        try:
            # Calculate elapsed time
            elapsed_time = 0
            if hasattr(self, 'operation_start_time') and self.operation_start_time:
                elapsed_time = time.time() - self.operation_start_time
            
            # Get current metrics from performance tracking
            files_processed = self.performance_stats.get('files_copied', 0)
            dirs_processed = self.performance_stats.get('dirs_copied', 0)
            bytes_copied = self.performance_stats.get('bytes_copied', 0)
            
            # Format elapsed time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Format data size
            data_str = self.format_bytes(bytes_copied)
            
            # Determine status icon and title
            if return_code in [0, 1, 2, 3]:
                status_icon = "✅"
                status_text = "SUCCESS"
                title_color = "#28a745"
            elif return_code in [4, 5, 6, 7]:
                status_icon = "⚠️"
                status_text = "WARNING"
                title_color = "#ffc107"
            else:
                status_icon = "❌"
                status_text = "ERROR"
                title_color = "#dc3545"
            
            # Build summary message
            summary_lines = []
            summary_lines.append("=" * 60)
            summary_lines.append(f"  {status_icon}  OPERATION SUMMARY  {status_icon}")
            summary_lines.append("=" * 60)
            summary_lines.append(f"\nStatus: {status_text} (Return Code: {return_code})")
            summary_lines.append(f"\n📁 Files Processed:    {files_processed:,}")
            summary_lines.append(f"📂 Directories:        {dirs_processed:,}")
            summary_lines.append(f"💾 Data Transferred:   {data_str}")
            summary_lines.append(f"⏱️  Time Elapsed:      {time_str}")
            
            if elapsed_time > 0 and bytes_copied > 0:
                speed = bytes_copied / elapsed_time
                speed_str = f"{self.format_bytes(speed)}/s"
                summary_lines.append(f"⚡ Average Speed:      {speed_str}")
            
            summary_lines.append("\n" + "=" * 60)
            
            # Add return code explanation
            if return_code == 0:
                summary_lines.append("\n📝 No files needed copying - already synchronized")
            elif return_code == 1:
                summary_lines.append("\n📝 Files copied successfully!")
            elif return_code == 2:
                summary_lines.append("\n📝 Extra files detected in destination")
            elif return_code == 3:
                summary_lines.append("\n📝 Files copied + extra files detected")
            elif return_code == 4:
                summary_lines.append("\n⚠️ Mismatched files detected")
            elif return_code >= 8:
                summary_lines.append("\n❌ Some files could not be copied - check errors above")
            
            summary_lines.append("\n" + "=" * 60 + "\n")
            
            # Display in output area
            summary_text = "\n".join(summary_lines)
            self.output_queue.put(('info', summary_text))
            
            # Also display in Performance Monitor tab summary area
            if hasattr(self, 'summary_text'):
                try:
                    self.summary_text.config(state=tk.NORMAL)
                    self.summary_text.delete(1.0, tk.END)
                    
                    # Add header with appropriate tag
                    tag = "success" if return_code in [0, 1, 2, 3] else "warning" if return_code in [4, 5, 6, 7] else "error"
                    self.summary_text.insert(tk.END, f"{status_icon}  OPERATION SUMMARY  {status_icon}\n", "header")
                    self.summary_text.insert(tk.END, "=" * 60 + "\n\n", tag)
                    
                    # Add summary details
                    self.summary_text.insert(tk.END, f"Status: {status_text} (Return Code: {return_code})\n\n", tag)
                    self.summary_text.insert(tk.END, f"📁 Files Processed:    {files_processed:,}\n")
                    self.summary_text.insert(tk.END, f"📂 Directories:        {dirs_processed:,}\n")
                    self.summary_text.insert(tk.END, f"💾 Data Transferred:   {data_str}\n")
                    self.summary_text.insert(tk.END, f"⏱️  Time Elapsed:      {time_str}\n")
                    
                    if elapsed_time > 0 and bytes_copied > 0:
                        speed = bytes_copied / elapsed_time
                        speed_str = f"{self.format_bytes(speed)}/s"
                        self.summary_text.insert(tk.END, f"⚡ Average Speed:      {speed_str}\n")
                    
                    self.summary_text.insert(tk.END, "\n" + "=" * 60 + "\n\n")
                    
                    # Add explanation
                    if return_code == 0:
                        self.summary_text.insert(tk.END, "📝 No files needed copying - already synchronized\n")
                    elif return_code == 1:
                        self.summary_text.insert(tk.END, "📝 Files copied successfully!\n", "success")
                    elif return_code == 2:
                        self.summary_text.insert(tk.END, "📝 Extra files detected in destination\n")
                    elif return_code == 3:
                        self.summary_text.insert(tk.END, "📝 Files copied + extra files detected\n", "success")
                    elif return_code == 4:
                        self.summary_text.insert(tk.END, "⚠️ Mismatched files detected\n", "warning")
                    elif return_code >= 8:
                        self.summary_text.insert(tk.END, "❌ Some files could not be copied - check Output tab for details\n", "error")
                    
                    self.summary_text.config(state=tk.DISABLED)
                    
                    # Switch to Performance Monitor tab to show summary
                    self.notebook.select(self.monitoring_tab)
                    
                except Exception as e:
                    self.logger.error(f"Error updating summary in Performance Monitor: {e}")
            
            # Also show as popup for immediate attention
            messagebox.showinfo(
                f"Operation {status_text}",
                f"{status_icon} ROBOCOPY Operation Completed!\n\n"
                f"Status: {status_text} (Code: {return_code})\n"
                f"Files: {files_processed:,} files\n"
                f"Directories: {dirs_processed:,} folders\n"
                f"Data: {data_str}\n"
                f"Time: {time_str}\n"
                f"\nCheck the Output tab for detailed results.",
                parent=self.root
            )
            
        except Exception as e:
            self.logger.error(f"Error showing operation summary: {e}")
    
    def show_return_codes(self):
        """Show ROBOCOPY return codes explanation"""
        return_codes_window = tk.Toplevel(self.root)
        return_codes_window.title("ROBOCOPY Return Codes Guide")
        return_codes_window.geometry("600x500")
        return_codes_window.transient(self.root)
        return_codes_window.grab_set()
        
        # Create scrollable text widget
        frame = ttk.Frame(return_codes_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        return_codes_content = """ROBOCOPY Return Codes Explanation

ROBOCOPY uses bit flags to indicate different conditions. The return code is a combination of these flags:

SUCCESS CODES (Green ✅):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0    No files copied, no failures encountered
     • Source and destination are already synchronized
     • Nothing needed to be done

1    Files copied successfully
     • One or more files were copied successfully
     • No errors occurred

2    Extra files or directories detected
     • Some files exist in destination but not in source
     • Usually indicates successful operation with extra files

3    Files copied + extra files detected (1+2)
     • Combination of codes 1 and 2
     • Files were copied and extra files were found

WARNING CODES (Yellow ⚠️):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4    Mismatched files or directories detected
     • Some files or directories don't match between source and destination
     • Check file attributes, timestamps, or security settings

5    Files copied + mismatched files (1+4)
     • Files were copied but some mismatches were detected

6    Extra files + mismatched files (2+4)
     • Extra files found and some files don't match

7    Files copied + extra files + mismatched (1+2+4)
     • All three conditions above occurred

ERROR CODES (Red ❌):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8    Some files or directories could not be copied
     • Copy failures occurred
     • Check permissions, disk space, or file locks

16   Serious error - ROBOCOPY did not copy any files
     • Fatal error occurred
     • Check source/destination paths, permissions, or syntax

COMBINATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Return codes can be combinations of the above flags:
• 9 (1+8): Files copied but some copy failures occurred
• 10 (2+8): Extra files detected but some copy failures occurred
• 12 (4+8): Mismatched files and some copy failures occurred

TIPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Return codes 0-7 are generally successful operations
• Return codes with 8 indicate copy errors occurred
• Return codes 16+ indicate serious errors
• Check the detailed output for specific error messages
• Use /V flag for verbose output to get more details"""
        
        text_widget.insert(tk.END, return_codes_content)
        text_widget.config(state=tk.DISABLED)
        
        # Add close button
        close_button = ttk.Button(return_codes_window, text="Close", command=return_codes_window.destroy)
        close_button.pack(pady=10)
    
    def clear_log(self):
        """Clear the log display"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.update_status("Log cleared")
    
    def save_log(self):
        """Save current log to file"""
        self.export_log()
    
    def refresh_log(self):
        """Refresh log display with enhanced formatting"""
        if hasattr(self, 'log_text'):
            try:
                if os.path.exists('robocopy_gui.log'):
                    with open('robocopy_gui.log', 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    self.log_text.delete(1.0, tk.END)
                    
                    # Format log content with color coding
                    for line in log_content.split('\n'):
                        if 'ERROR' in line:
                            self.log_text.insert(tk.END, line + '\n', 'error')
                        elif 'WARNING' in line:
                            self.log_text.insert(tk.END, line + '\n', 'warning')
                        elif 'INFO' in line:
                            self.log_text.insert(tk.END, line + '\n', 'info')
                        else:
                            self.log_text.insert(tk.END, line + '\n')
                    
                    self.log_text.see(tk.END)
                    self.update_status("Log refreshed")
                else:
                    self.log_text.delete(1.0, tk.END)
                    self.log_text.insert(tk.END, "No log file found. Start an operation to generate logs.")
            except Exception as e:
                self.logger.error(f"Failed to refresh log: {str(e)}")
                messagebox.showerror("Error", f"Failed to refresh log: {str(e)}")
    
    def save_command_history(self, history_entry):
        """Save command to history file"""
        try:
            with open('command_history.txt', 'a', encoding='utf-8') as f:
                f.write(history_entry + '\n')
        except Exception as e:
            self.logger.error(f"Failed to save command history: {str(e)}")
    
    def load_command_history(self):
        """Load command history from file"""
        try:
            if os.path.exists('command_history.txt'):
                with open('command_history.txt', 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Load last 20 commands
                for line in reversed(lines[-20:]):
                    if line.strip():
                        self.history_listbox.insert(tk.END, line.strip())
        except Exception as e:
            self.logger.error(f"Failed to load command history: {str(e)}")
    
    def load_from_history(self):
        """Load selected command from history with improved parsing"""
        selection = self.history_listbox.curselection()
        if selection:
            history_entry = self.history_listbox.get(selection[0])
            
            # Extract command from timestamped entry
            if history_entry.startswith('[') and '] ' in history_entry:
                command = history_entry.split('] ', 1)[1]  # Remove timestamp
            else:
                command = history_entry
            
            self.command_display.config(text=command, foreground="blue")
            self.current_command = command
            self.update_status("Command loaded from history")
        else:
            messagebox.showinfo("Info", "Please select a command from the history list first.")
    
    def clear_history(self):
        """Clear command history with confirmation"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all command history?"):
            self.history_listbox.delete(0, tk.END)
            try:
                if os.path.exists('command_history.txt'):
                    os.remove('command_history.txt')
            except Exception as e:
                self.logger.error(f"Failed to delete history file: {str(e)}")
            self.update_status("Command history cleared")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = AdvancedRobocopyGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.current_process and app.current_process.poll() is None:
            if messagebox.askokcancel("Quit", "A command is running. Do you want to stop it and quit?"):
                app.stop_command()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
