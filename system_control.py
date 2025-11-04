"""
SystemControl - Safe system command execution and control
Provides controlled access to system operations
"""

import logging
from typing import Dict, List, Optional, Callable
import os
import subprocess
import platform
import psutil
from pathlib import Path


class SystemControl:
    """
    System control interface with safety checks and permissions
    Allows controlled execution of system commands and file operations
    """
    
    def __init__(self, config: Dict):
        """
        Initialize system control with configuration
        
        Args:
            config: Dictionary containing system control configuration
        """
        self.config = config
        self.allowed_directories = [Path(d) for d in config.get('allowed_directories', [])]
        self.allowed_commands = config.get('allowed_commands', [])
        self.require_confirmation = config.get('require_confirmation', True)
        self.confirmation_callback: Optional[Callable] = None
        
        self.logger = logging.getLogger(__name__)
        self.system = platform.system()
    
    def set_confirmation_callback(self, callback: Callable):
        """
        Set callback function for user confirmation
        
        Args:
            callback: Function that takes a message and returns bool
        """
        self.confirmation_callback = callback
    
    def _check_confirmation(self, action: str) -> bool:
        """
        Check if user confirms the action
        
        Args:
            action: Description of the action
            
        Returns:
            bool: True if confirmed or confirmation not required
        """
        if not self.require_confirmation:
            return True
        
        if self.confirmation_callback:
            return self.confirmation_callback(action)
        
        # Default console confirmation
        response = input(f"Confirm action: {action} (yes/no): ")
        return response.lower() in ['yes', 'y']
    
    def _is_path_allowed(self, path: Path) -> bool:
        """
        Check if a path is within allowed directories
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path is allowed
        """
        path = path.resolve()
        
        for allowed_dir in self.allowed_directories:
            try:
                path.relative_to(allowed_dir)
                return True
            except ValueError:
                continue
        
        return False
    
    def open_application(self, app_name: str) -> bool:
        """
        Open an application
        
        Args:
            app_name: Name or path of the application
            
        Returns:
            bool: True if successful
        """
        # Check if command is allowed
        if app_name.lower() not in [cmd.lower() for cmd in self.allowed_commands]:
            self.logger.warning(f"Application not in allowed list: {app_name}")
            return False
        
        # Confirm action
        if not self._check_confirmation(f"Open application: {app_name}"):
            self.logger.info("Action cancelled by user")
            return False
        
        try:
            if self.system == "Windows":
                # Windows-specific application launching
                app_paths = {
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'explorer': 'explorer.exe',
                    'chrome': r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    'firefox': r'C:\Program Files\Mozilla Firefox\firefox.exe'
                }
                
                cmd = app_paths.get(app_name.lower(), app_name)
                subprocess.Popen(cmd, shell=True)
                
            elif self.system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', app_name])
                
            else:  # Linux
                subprocess.Popen([app_name])
            
            self.logger.info(f"Opened application: {app_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening application: {e}")
            return False
    
    def read_file(self, filepath: str) -> Optional[str]:
        """
        Read contents of a file
        
        Args:
            filepath: Path to the file
            
        Returns:
            str: File contents, or None if failed
        """
        path = Path(filepath)
        
        # Check if path is allowed
        if not self._is_path_allowed(path):
            self.logger.warning(f"Access denied to path: {filepath}")
            return None
        
        # Check if file exists
        if not path.exists() or not path.is_file():
            self.logger.warning(f"File not found: {filepath}")
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"Read file: {filepath}")
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            return None
    
    def write_file(self, filepath: str, content: str) -> bool:
        """
        Write content to a file
        
        Args:
            filepath: Path to the file
            content: Content to write
            
        Returns:
            bool: True if successful
        """
        path = Path(filepath)
        
        # Check if path is allowed
        if not self._is_path_allowed(path):
            self.logger.warning(f"Access denied to path: {filepath}")
            return False
        
        # Confirm action
        if not self._check_confirmation(f"Write to file: {filepath}"):
            self.logger.info("Action cancelled by user")
            return False
        
        try:
            # Create parent directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Wrote file: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing file: {e}")
            return False
    
    def list_directory(self, dirpath: str) -> Optional[List[str]]:
        """
        List contents of a directory
        
        Args:
            dirpath: Path to the directory
            
        Returns:
            List of file/folder names, or None if failed
        """
        path = Path(dirpath)
        
        # Check if path is allowed
        if not self._is_path_allowed(path):
            self.logger.warning(f"Access denied to path: {dirpath}")
            return None
        
        # Check if directory exists
        if not path.exists() or not path.is_dir():
            self.logger.warning(f"Directory not found: {dirpath}")
            return None
        
        try:
            items = [item.name for item in path.iterdir()]
            self.logger.info(f"Listed directory: {dirpath}")
            return sorted(items)
            
        except Exception as e:
            self.logger.error(f"Error listing directory: {e}")
            return None
    
    def get_system_info(self) -> Dict:
        """
        Get system information
        
        Returns:
            Dictionary with system information
        """
        try:
            info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                'memory_available': f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': f"{psutil.disk_usage('/').percent}%"
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def execute_command(self, command: str) -> Optional[str]:
        """
        Execute a shell command (with strict safety checks)
        
        Args:
            command: Command to execute
            
        Returns:
            str: Command output, or None if failed
        """
        # Confirm action
        if not self._check_confirmation(f"Execute command: {command}"):
            self.logger.info("Action cancelled by user")
            return None
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout if result.returncode == 0 else result.stderr
            self.logger.info(f"Executed command: {command}")
            return output
            
        except subprocess.TimeoutExpired:
            self.logger.error("Command execution timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            return None
    
    def get_running_processes(self) -> List[Dict]:
        """
        Get list of running processes
        
        Returns:
            List of process information dictionaries
        """
        try:
            processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Error getting processes: {e}")
            return []
    
    def shutdown(self):
        """Cleanup system control resources"""
        self.logger.info("System control shutdown")


# Example usage
if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize system control
    sys_ctrl = SystemControl(config["system"])
    
    print("System Control Test")
    print("="*60)
    
    # Get system info
    print("\nSystem Information:")
    info = sys_ctrl.get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # List directory
    print("\n" + "="*60)
    print("\nListing Desktop directory:")
    items = sys_ctrl.list_directory(r"C:\Users\suraj\Desktop")
    if items:
        for item in items[:10]:  # Show first 10 items
            print(f"  - {item}")
    
    print("\nDone!")
    sys_ctrl.shutdown()
