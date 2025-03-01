import os
import sys
import winreg
import shutil
import subprocess
from pathlib import Path
import win32com.client
from PIL import Image, ImageDraw

def create_icon_file():
    """Create a simple icon for the application"""
    width = 64
    height = 64
    color1 = (66, 133, 244)  # Blue
    color2 = (234, 67, 53)   # Red
    
    image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw a microphone-like shape
    dc.rectangle((20, 16, 44, 40), fill=color1)
    dc.ellipse((16, 8, 48, 24), fill=color1)
    dc.rectangle((28, 40, 36, 56), fill=color2)
    dc.ellipse((24, 48, 40, 64), fill=color2)
    
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "carls_whisper.ico")
    
    # Save as ICO
    image.save(icon_path, format="ICO")
    return icon_path

def create_desktop_shortcut():
    """Create a desktop shortcut for the application"""
    try:
        # Get paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tray_script = os.path.join(script_dir, "tray_app.py")
        
        # Create icon
        icon_path = create_icon_file()
        
        # Get Python executable
        pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        
        # Create shortcut on desktop
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "Carl's Whisper.lnk")
        
        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = pythonw_exe
        shortcut.Arguments = f'"{tray_script}"'
        shortcut.WorkingDirectory = script_dir
        shortcut.Description = "Carl's Whisper Voice Assistant"
        shortcut.IconLocation = icon_path
        shortcut.save()
        
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create desktop shortcut: {str(e)}")
        return False

def add_to_startup():
    """Add the application to Windows startup"""
    try:
        # Get paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tray_script = os.path.join(script_dir, "tray_app.py")
        
        # Get Python executable
        pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        
        # Create startup shortcut
        startup_folder = os.path.join(
            os.getenv("APPDATA"), 
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
        )
        startup_path = os.path.join(startup_folder, "Carl's Whisper.lnk")
        
        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(startup_path)
        shortcut.TargetPath = pythonw_exe
        shortcut.Arguments = f'"{tray_script}"'
        shortcut.WorkingDirectory = script_dir
        shortcut.Description = "Carl's Whisper Voice Assistant"
        shortcut.IconLocation = os.path.join(script_dir, "carls_whisper.ico")
        shortcut.save()
        
        print(f"Added to startup: {startup_path}")
        return True
    except Exception as e:
        print(f"Failed to add to startup: {str(e)}")
        return False

def main():
    """Main installer function"""
    print("=== Carl's Whisper Installer ===")
    
    # Create desktop shortcut
    shortcut_choice = input("Create desktop shortcut? (y/n): ").strip().lower()
    if shortcut_choice.startswith('y'):
        create_desktop_shortcut()
    
    # Add to startup
    startup_choice = input("Run on Windows startup? (y/n): ").strip().lower()
    if startup_choice.startswith('y'):
        add_to_startup()
    
    # Launch now?
    launch_choice = input("Launch Carl's Whisper now? (y/n): ").strip().lower()
    if launch_choice.startswith('y'):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tray_script = os.path.join(script_dir, "tray_app.py")
        pythonw_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        
        try:
            subprocess.Popen([pythonw_exe, tray_script])
            print("Carl's Whisper is now running in the system tray.")
        except Exception as e:
            print(f"Error launching application: {str(e)}")
    
    print("\nInstallation completed!")
    print("You can always run the installer again to change these settings.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
