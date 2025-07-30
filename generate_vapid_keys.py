#!/usr/bin/env python3
"""
Script to generate VAPID keys for web push notifications.
Run this script once to generate your keys, then update main.py with the generated keys.
"""

try:
    from pywebpush import generate_vapid_keys
    
    print("Generating VAPID keys for web push notifications...")
    vapid_keys = generate_vapid_keys()
    
    print("\n" + "="*50)
    print("VAPID KEYS GENERATED SUCCESSFULLY")
    print("="*50)
    print(f"\nPrivate Key: {vapid_keys['private_key']}")
    print(f"\nPublic Key: {vapid_keys['public_key']}")
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
    
except ImportError:
    print("Error: pywebpush library not found.")
    print("Please install it using: pip install pywebpush")
except Exception as e:
    print(f"Error generating VAPID keys: {e}")
    print("Make sure pywebpush is properly installed.")