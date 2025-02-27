import tkinter as tk
from tkinter import ttk, messagebox
from secret_manager import SecretManager
import json
from pathlib import Path

class SecretManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secret Manager")
        
        # Initialize SecretManager with the GPG key file
        self.secret_manager = SecretManager("private.gpg")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Username
        ttk.Label(self.root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.root)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(self.root, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons
        ttk.Button(self.root, text="Store Password", 
                  command=self.store_password).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.root, text="Retrieve Password", 
                  command=self.retrieve_password).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Encrypt Secrets", 
                  command=self.encrypt_secrets).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.root, text="Decrypt Secrets", 
                  command=self.decrypt_secrets).grid(row=3, column=1, padx=5, pady=5)
        
        # GPG Passphrase Frame
        gpg_frame = ttk.LabelFrame(self.root, text="GPG Settings")
        gpg_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ttk.Label(gpg_frame, text="GPG Passphrase:").grid(row=0, column=0, padx=5, pady=5)
        self.gpg_passphrase_entry = ttk.Entry(gpg_frame, show="*")
        self.gpg_passphrase_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(gpg_frame, text="Store GPG Passphrase", 
                  command=self.store_gpg_passphrase).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def store_password(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username and password:
            self.secret_manager.store_password(username, password)
            messagebox.showinfo("Success", "Password stored successfully!")
        else:
            messagebox.showerror("Error", "Please enter both username and password")

    def retrieve_password(self):
        username = self.username_entry.get()
        
        if username:
            password = self.secret_manager.get_password(username)
            if password:
                self.password_entry.delete(0, tk.END)
                self.password_entry.insert(0, password)
            else:
                messagebox.showerror("Error", "Password not found")
        else:
            messagebox.showerror("Error", "Please enter a username")

    def encrypt_secrets(self):
        secrets = {
            "username": self.username_entry.get(),
            "password": self.password_entry.get()
        }
        
        # Save temporary JSON file
        temp_file = Path("temp_secrets.json")
        encrypted_file = Path("encrypted_secrets.json")
        
        with open(temp_file, "w") as f:
            json.dump(secrets, f)
        
        if self.secret_manager.encrypt_file(str(temp_file), str(encrypted_file)):
            messagebox.showinfo("Success", "Secrets encrypted successfully!")
        else:
            messagebox.showerror("Error", "Encryption failed")
        
        # Clean up temporary file
        temp_file.unlink()

    def decrypt_secrets(self):
        encrypted_file = Path("encrypted_secrets.json")
        if not encrypted_file.exists():
            messagebox.showerror("Error", "No encrypted file found")
            return
            
        decrypted_data = self.secret_manager.decrypt_file(str(encrypted_file))
        if decrypted_data:
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.username_entry.insert(0, decrypted_data.get("username", ""))
            self.password_entry.insert(0, decrypted_data.get("password", ""))
            messagebox.showinfo("Success", "Secrets decrypted successfully!")
        else:
            messagebox.showerror("Error", "Decryption failed")

    def store_gpg_passphrase(self):
        passphrase = self.gpg_passphrase_entry.get()
        if passphrase:
            self.secret_manager.store_gpg_passphrase(passphrase)
            messagebox.showinfo("Success", "GPG passphrase stored successfully!")
            self.gpg_passphrase_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter a GPG passphrase")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecretManagerApp(root)
    root.mainloop() 