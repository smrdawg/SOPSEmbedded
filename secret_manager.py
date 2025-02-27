import subprocess
import json
import keyring
from pathlib import Path
import base64
import os
from resources import ResourceManager
import sys
import tempfile

class SecretManager:
    def __init__(self, gpg_key_file):
        self.resource_manager = ResourceManager()
        self.system_name = "MySecretApp"
        self.gpg_key_file = self.resource_manager.get_gpg_key_path(gpg_key_file)
        self.sops_binary = self.resource_manager.get_sops_path()
        self.gpg_binary = self.resource_manager.get_gpg_binary()
        
        # Set up environment for GPG
        self.gpg_env = os.environ.copy()
        self.gpg_env["GNUPGHOME"] = self.resource_manager.get_gpg_home()
        
        # Get GPG passphrase from credential manager
        self.gpg_passphrase = self.get_gpg_passphrase()
        if not self.gpg_passphrase:
            raise ValueError("GPG passphrase not found in credential manager")
        
        # Import GPG key
        self._import_gpg_key()

    def _import_gpg_key(self):
        """Imports the GPG key into the keyring"""
        try:
            # Create a temporary batch file for GPG passphrase
            batch_cmd = f"""Key-Type: RSA
            Passphrase: {self.gpg_passphrase}
            %commit
            """
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as batch_file:
                batch_file.write(batch_cmd)
                batch_file.flush()
                
            # Import the key with passphrase
            result = subprocess.run(
                [self.gpg_binary, "--batch", "--import", self.gpg_key_file],
                capture_output=True,
                text=True,
                check=True,
                env=self.gpg_env
            )
            
            # Get the key fingerprint
            self.gpg_key_fingerprint = self._get_key_fingerprint()
            
            # Cleanup batch file
            os.unlink(batch_file.name)
        except subprocess.CalledProcessError as e:
            print(f"Failed to import GPG key: {e}")
            raise

    def _get_key_fingerprint(self):
        """Gets the fingerprint of the imported GPG key"""
        result = subprocess.run(
            [self.gpg_binary, "--list-secret-keys", "--with-colons"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.split('\n'):
            if line.startswith('fpr:'):
                return line.split(':')[9]
        return None

    def encrypt_file(self, input_file, output_file):
        """Encrypts a file using SOPS with the specified GPG key"""
        try:
            cmd = [
                self.sops_binary,
                "--encrypt",
                "--pgp", self.gpg_key_fingerprint,
                "--input-type", "json",
                "--output-type", "json",
                "--output", output_file,
                input_file
            ]
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Encryption failed: {e}")
            return False

    def decrypt_file(self, encrypted_file):
        """Decrypts a SOPS encrypted file"""
        try:
            result = subprocess.run(
                ["sops", "-d", encrypted_file],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Decryption failed: {e}")
            return None

    def store_password(self, username, password):
        """Stores password in Windows Credential Manager"""
        keyring.set_password(self.system_name, username, password)

    def get_password(self, username):
        """Retrieves password from Windows Credential Manager"""
        return keyring.get_password(self.system_name, username)

    def store_gpg_passphrase(self, passphrase):
        """Stores GPG passphrase in Windows Credential Manager"""
        keyring.set_password(self.system_name, "gpg_passphrase", passphrase)

    def get_gpg_passphrase(self):
        """Retrieves GPG passphrase from Windows Credential Manager"""
        return keyring.get_password(self.system_name, "gpg_passphrase")

    def __del__(self):
        """Cleanup temporary files on object destruction"""
        self.resource_manager.cleanup() 