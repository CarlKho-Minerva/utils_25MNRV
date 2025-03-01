import ctypes
import sys
import os

def register_app_id():
    """
    Register the application ID with Windows to improve notification appearance
    
    This helps Windows recognize our app and use our app name in notifications.
    """
    try:
        # Get the path to the running script
        app_id = "CarlsWhisper.VoiceAssistant.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        return True
    except Exception as e:
        print(f"Failed to register application ID: {str(e)}")
        return False

def get_python_exe():
    """Get the path to the current Python executable"""
    return sys.executable

if __name__ == "__main__":
    register_app_id()
    print(f"Application ID registered. Python executable: {get_python_exe()}")
