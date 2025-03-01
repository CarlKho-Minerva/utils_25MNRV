import os
import sys
import winshell
from win32com.client import Dispatch

def create_desktop_shortcut():
    """Create a desktop shortcut for the whisper assistant with proper app identity"""
    try:
        # Get the path to the current script
        script_path = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_path, "main.py")
        
        # Get Python executable path
        python_exe = sys.executable
        
        # Get the desktop path
        desktop = winshell.desktop()
        
        # Create shortcut path
        shortcut_path = os.path.join(desktop, "Carl's Whisper.lnk")
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{main_script}"'
        shortcut.WorkingDirectory = script_path
        shortcut.Description = "Carl's Whisper Voice Assistant"
        shortcut.IconLocation = os.path.join(script_path, "temp", "carls_whisper.ico")
        shortcut.save()
        
        print(f"Shortcut created at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {str(e)}")
        return False

if __name__ == "__main__":
    create_desktop_shortcut()
