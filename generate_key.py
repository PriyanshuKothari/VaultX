from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    if os.path.exists(KEY_FILE):
        print(f"⚠️  Warning: '{KEY_FILE}' already exists!")
        confirm = input("   Generating a new key will make old encrypted files unreadable.\n   Are you sure? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ Key generation cancelled. Existing key kept.")
            return

    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    print(f"✅ New secret key generated and saved to '{KEY_FILE}'")
    print("🔒 Keep this file safe — never share or commit it to GitHub!")

if __name__ == "__main__":
    generate_key()