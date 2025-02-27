# Secret Manager with SOPS and GPG

A Python desktop application that provides secure secret management using Mozilla SOPS and GPG, with Windows Credential Manager integration.

## Why This Exists

This tool was developed in response to a real security vulnerability discovered during a Red Team assessment. In a white-box penetration test, the Red Team was able to:
1. Locate the key generation mechanism
2. Extract the key
3. Successfully exploit the system using the compromised key

This application provides a more secure approach by:
- Separating the key from its passphrase
- Storing the passphrase in Windows Credential Manager, which is protected by the user's credentials
- Using the passphrase as a second factor, similar to a product key

Even if an attacker gains access to the GPG key, they would still need:
1. Access to the user's Windows credentials to retrieve the passphrase from Credential Manager
2. Or the passphrase itself, which is never stored in plaintext

This two-factor approach significantly increases the difficulty of key compromise, as both the key file and the securely stored passphrase would need to be compromised.

## Why This Approach?

There are several approaches to securing secrets in desktop applications, each with their own trade-offs:

### Windows Data Protection API (DPAPI)
- Built into Windows
- Ties encryption directly to user credentials
- Simpler implementation
- Drawback: Windows-only, less portable

### Hardware Security Modules (HSM)
- Highest level of security
- Physical security for keys
- Drawback: Expensive, complex setup, requires hardware

### Trusted Platform Module (TPM)
- Hardware-based security
- Built into many modern systems
- Drawback: Not universally available, complex implementation

### Cloud Key Management (Azure Key Vault/AWS KMS)
- Cloud-based key management
- Very secure
- Drawback: Requires internet connectivity, subscription costs

### This Solution (SOPS + GPG + Credential Manager)
- More secure than basic encryption
- More portable than DPAPI
- Less complex/expensive than HSM/TPM
- Works offline unlike cloud solutions
- Uses established, well-tested tools (SOPS, GPG)
- Reasonable balance of security, cost, and complexity

## Features
- Encrypt/decrypt secrets using SOPS with GPG
- Store passwords securely in Windows Credential Manager
- Self-contained GPG and SOPS binaries
- Isolated GPG environment from system installation
- Simple GUI interface

## Project Structure 