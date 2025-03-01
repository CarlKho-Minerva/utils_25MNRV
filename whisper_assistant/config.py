import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
HOLD_DURATION = 1.0  # seconds to hold key before recording
RECORDING_SAMPLE_RATE = 44100  # Hz
AUDIO_TEMP_FILE = "temp_recording.wav"
KEY_TO_MONITOR = "shift_r"  # Right shift key

# API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = "whisper-1"  # OpenAI Whisper model to use

# User preferences
# AUTO_PASTE: If True, will attempt to paste at cursor position
# If False, will only copy to clipboard for manual pasting
AUTO_PASTE = os.getenv("AUTO_PASTE", "True").lower() == "true"

# SHOW_VISUAL_FEEDBACK: If True, shows visual notifications during recording
SHOW_VISUAL_FEEDBACK = os.getenv("SHOW_VISUAL_FEEDBACK", "True").lower() == "true"

# KEEP_HISTORY: If True, will keep transcription in clipboard even after pasting
KEEP_HISTORY = os.getenv("KEEP_HISTORY", "True").lower() == "true"

# SHORT_NOTIFICATIONS: If True, notifications disappear quickly
SHORT_NOTIFICATIONS = os.getenv("SHORT_NOTIFICATIONS", "True").lower() == "true"
