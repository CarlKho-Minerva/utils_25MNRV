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
# DON'T store the API key directly in code. Use environment variables instead.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHISPER_MODEL = "whisper-1"  # OpenAI Whisper model to use
