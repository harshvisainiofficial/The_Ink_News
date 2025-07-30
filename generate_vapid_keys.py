#!/usr/bin/env python3
"""
Script to generate VAPID keys for web push notifications.
Run this script once to generate your keys, then update main.py with the generated keys.
"""

from cryptography.hazmat.primitives import serialization

try:
    from py_vapid import Vapid
    
    print("Generating VAPID keys for web push notifications...")
    vapid = Vapid()
    vapid.generate_keys()
    
    private_key = vapid.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    public_key = vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    import base64
    public_key_b64 = base64.urlsafe_b64encode(public_key).decode('utf-8').rstrip('=')
    
    print("\n" + "="*50)
    print("VAPID KEYS GENERATED SUCCESSFULLY")
    print("="*50)
    print(f"\nPrivate Key: {private_key}")
    print(f"\nPublic Key: {public_key_b64}")
    print("\n" + "="*50)
    print("IMPORTANT INSTRUCTIONS:")
    print("="*50)
    print("1. Copy the Private Key and replace 'your-private-key-here' in main.py")
    print("2. Copy the Public Key and replace the existing public key in main.py")
    print("3. Also update the public key in base.html (applicationServerPublicKey variable)")
    print("4. Keep these keys secure and never share the private key publicly!")
    print("5. These keys are used to authenticate your server with push services.")
    print("\nAfter updating the keys, restart your Flask application.")
    print("="*50)
    
except ImportError as e:
    print(f"Error: Required library not found - {e}")
    print("Please install required packages using: pip install py-vapid cryptography")
except Exception as e:
    print(f"Error generating VAPID keys: {e}")
    print("Make sure py-vapid and cryptography are properly installed.")