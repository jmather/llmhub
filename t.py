import os
import subprocess

def check_full_disk_access():
    try:
        # Try accessing a restricted directory
        with open("/Library/Application Support/.testfile", "w") as f:
            f.write("Test")
        print("Full Disk Access granted.")
    except PermissionError:
        print("Full Disk Access is required to perform this operation.")
        print("Please grant access by following the instructions.")
        open_full_disk_access_settings()

def open_full_disk_access_settings():
    try:
        # Open the "Full Disk Access" settings in macOS
        subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"], check=True)
    except Exception as e:
        print(f"Failed to open System Preferences: {e}")

if __name__ == "__main__":
    check_full_disk_access()
