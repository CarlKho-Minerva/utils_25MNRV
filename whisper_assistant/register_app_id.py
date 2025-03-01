import ctypes
import sys
import os
import winreg

def register_app_id(app_name="Carl's Whisper"):
    """Register application identity with Windows"""
    try:
        app_id = "CarlsWhisper.VoiceAssistant.1.0"
        
        # Set app ID for current process
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        
        # Register app ID in the registry for persistent settings
        key_path = r"Software\Classes\AppUserModelId\{}".format(app_id)
        
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path)
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "IconPath", 0, winreg.REG_SZ, 
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), "carls_whisper.ico"))
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Registry registration failed: {str(e)}")
            return False
    except Exception as e:
        print(f"Failed to register application ID: {str(e)}")
        return False

def get_python_exe():
    """Get the path to the current Python executable"""
    return sys.executable

if __name__ == "__main__":
    register_app_id()
    print("Application ID registered successfully")
    print(f"Python executable: {get_python_exe()}")
