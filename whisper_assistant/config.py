import os
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
HOLD_DURATION = float(os.getenv("HOLD_DURATION", "1.0"))  # seconds to hold key before recording
RECORDING_SAMPLE_RATE = 44100  # Hz
MAX_RECORDING_LENGTH = float(os.getenv("MAX_RECORDING_LENGTH", "60.0"))  # max seconds to record

# Use temp directory for audio file to avoid permission issues
TEMP_DIR = os.path.join(tempfile.gettempdir(), "whisper_assistant")
os.makedirs(TEMP_DIR, exist_ok=True)
AUDIO_TEMP_FILE = os.path.join(TEMP_DIR, "recording.wav")

KEY_TO_MONITOR = os.getenv("KEY_TO_MONITOR", "shift_r")  # Default to right shift key

# API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")  # OpenAI Whisper model to use

# User preferences
AUTO_PASTE = os.getenv("AUTO_PASTE", "True").lower() == "true"
SHOW_VISUAL_FEEDBACK = os.getenv("SHOW_VISUAL_FEEDBACK", "True").lower() == "true"
KEEP_HISTORY = os.getenv("KEEP_HISTORY", "True").lower() == "true"
SHORT_NOTIFICATIONS = os.getenv("SHORT_NOTIFICATIONS", "True").lower() == "true"

# Notification appearance
APP_NAME = os.getenv("APP_NAME", "Carl's Whisper")
APP_ID = os.getenv("APP_ID", "CarlsWhisper.VoiceAssistant.1.0")
