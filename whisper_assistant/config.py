import os
import tempfile
import re
import json
import urllib.request
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
HOLD_DURATION = float(os.getenv("HOLD_DURATION", "0.8"))  # seconds to hold key before recording
RECORDING_SAMPLE_RATE = 44100  # Hz
MAX_RECORDING_LENGTH = float(os.getenv("MAX_RECORDING_LENGTH", "60.0"))  # max seconds to record

# Use temp directory for audio file to avoid permission issues
TEMP_DIR = os.path.join(tempfile.gettempdir(), "whisper_assistant")
os.makedirs(TEMP_DIR, exist_ok=True)
AUDIO_TEMP_FILE = os.path.join(TEMP_DIR, "recording.wav")

KEY_TO_MONITOR = os.getenv("KEY_TO_MONITOR", "shift_r")  # Default to right shift key

# API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Available Whisper models and their capabilities
WHISPER_MODELS = {
    "whisper-1": {"description": "Standard model", "multilingual": True, "default": True},
    "tts-1": {"description": "Text to speech model", "multilingual": False, "default": False},
    "tts-1-hd": {"description": "High definition TTS model", "multilingual": False, "default": False},
}

# User selected model
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")

# Language settings
LANGUAGE = os.getenv("LANGUAGE", "en")  # Default to English, use 'auto' for auto-detection
LANGUAGES = {
    "auto": "Auto-detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "ar": "Arabic"
}

# User preferences
AUTO_PASTE = os.getenv("AUTO_PASTE", "True").lower() == "true"
SHOW_VISUAL_FEEDBACK = os.getenv("SHOW_VISUAL_FEEDBACK", "True").lower() == "true"
KEEP_HISTORY = os.getenv("KEEP_HISTORY", "True").lower() == "true"
SHORT_NOTIFICATIONS = os.getenv("SHORT_NOTIFICATIONS", "True").lower() == "true"
AUTO_UPDATE_CHECK = os.getenv("AUTO_UPDATE_CHECK", "True").lower() == "true"

# Notification appearance
APP_NAME = os.getenv("APP_NAME", "Carl's Whisper")
APP_ID = os.getenv("APP_ID", "CarlsWhisper.VoiceAssistant.1.0")

# Version information
APP_VERSION = "1.1.0"
GITHUB_REPO = "https://api.github.com/repos/yourusername/whisper_assistant/releases/latest"

def check_for_updates():
    """Check if there's a newer version available"""
    try:
        # Get the latest release info from GitHub (placeholder URL)
        with urllib.request.urlopen(GITHUB_REPO) as response:
            data = json.loads(response.read().decode())
            latest_version = data['tag_name'].lstrip('v')
            
            # Compare versions
            if latest_version > APP_VERSION:
                return {
                    'available': True,
                    'version': latest_version,
                    'url': data['html_url']
                }
    except:
        pass
    
    return {'available': False}

def update_config(key, value):
    """Update a configuration setting in the .env file"""
    try:
        dotenv_path = find_dotenv()
        if not dotenv_path:
            # If .env doesn't exist, create it in the current directory
            dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            if not os.path.exists(dotenv_path):
                with open(dotenv_path, 'w') as f:
                    f.write(f"# Carl's Whisper Configuration\n")
        
        # Read the .env file
        with open(dotenv_path, 'r') as f:
            lines = f.readlines()
        
        # Check if the key already exists
        key_exists = False
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line.split('=')[0].strip() == key:
                    lines[i] = f"{key}={value}\n"
                    key_exists = True
                    break
        
        # If the key doesn't exist, add it
        if not key_exists:
            lines.append(f"{key}={value}\n")
        
        # Write the updated .env file
        with open(dotenv_path, 'w') as f:
            f.writelines(lines)
        
        # Update the global variable
        if key == 'KEY_TO_MONITOR':
            globals()['KEY_TO_MONITOR'] = value
        elif key == 'HOLD_DURATION':
            globals()['HOLD_DURATION'] = float(value)
        elif key == 'WHISPER_MODEL':
            globals()['WHISPER_MODEL'] = value
        elif key == 'LANGUAGE':
            globals()['LANGUAGE'] = value
        
        return True
    except Exception as e:
        print(f"Error updating config: {str(e)}")
        return False
