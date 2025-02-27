import sys
import os
from pathlib import Path
import shutil
import tempfile

class ResourceManager:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.bin_dir = self.project_dir / "bin"
        
        # Set up paths for binaries
        if sys.platform == "win32":
            self.gpg_dir = self.bin_dir / "gpg4win"
            self.gpg_binary = self.gpg_dir / "bin" / "gpg.exe"
            self.sops_binary = self.bin_dir / "sops.exe"
        else:
            self.gpg_dir = self.bin_dir / "gnupg"
            self.gpg_binary = self.gpg_dir / "gpg"
            self.sops_binary = self.bin_dir / "sops"
        
        # Create GPG home directory if it doesn't exist
        self.gpg_home = self.project_dir / ".gnupg"
        self.gpg_home.mkdir(exist_ok=True)
        os.chmod(str(self.gpg_home), 0o700)  # Required permissions for GPG

    def get_sops_path(self):
        """Returns path to SOPS binary in project directory"""
        if not self.sops_binary.exists():
            raise FileNotFoundError(f"SOPS binary not found at {self.sops_binary}")
        return str(self.sops_binary)

    def get_gpg_binary(self):
        """Returns path to GPG binary"""
        if not self.gpg_binary.exists():
            raise FileNotFoundError(f"GPG binary not found at {self.gpg_binary}")
        return str(self.gpg_binary)

    def get_gpg_home(self):
        """Returns path to GPG home directory"""
        return str(self.gpg_home)

    def get_gpg_key_path(self, key_file):
        """Returns path to GPG key file in project directory"""
        key_path = self.project_dir / "keys" / key_file
        if not key_path.exists():
            raise FileNotFoundError(f"GPG key file not found at {key_path}")
        return str(key_path)

    def initialize_temp_directory(self):
        """Creates a temporary directory for extracted resources"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def extract_sops_binary(self):
        """Extracts SOPS binary to temporary location and returns path"""
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            sops_name = "sops.exe" if sys.platform == "win32" else "sops"
            sops_path = self.get_resource_path(sops_name)
            temp_sops = self.temp_dir / sops_name
            
            if not temp_sops.exists():
                shutil.copy2(sops_path, temp_sops)
                if sys.platform != "win32":
                    temp_sops.chmod(0o755)  # Make executable on Unix
            
            return str(temp_sops)
        else:
            # Development mode - assume SOPS is in PATH
            return "sops"

    def extract_gpg_key(self, key_file):
        """Extracts GPG key to temporary location"""
        if getattr(sys, 'frozen', False):
            key_path = self.get_resource_path(key_file)
            temp_key = self.temp_dir / key_file
            
            if not temp_key.exists():
                shutil.copy2(key_path, temp_key)
            
            return str(temp_key)
        else:
            return key_file

    def cleanup(self):
        """Cleanup temporary files"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir) 