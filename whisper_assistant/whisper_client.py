import os
import pyperclip
from openai import OpenAI
from config import OPENAI_API_KEY, WHISPER_MODEL

class WhisperClient:
    def __init__(self):
        try:
            # Try the standard initialization
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        except TypeError as e:
            if 'got an unexpected keyword argument' in str(e):
                # Handle older HTTPX versions that don't support proxies
                import httpx
                http_client = httpx.Client()
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    http_client=http_client
                )
            else:
                raise
        
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file using OpenAI's Whisper API
        """
        try:
            if not os.path.exists(audio_file_path):
                print(f"Audio file not found: {audio_file_path}")
                return None
                
            print("Transcribing audio...")
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file
                )
            
            if response and hasattr(response, "text"):
                transcription = response.text
                print(f"Transcription: {transcription}")
                return transcription
            else:
                print("No transcription received")
                return None
                
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            return None
            
    def paste_text(self, text):
        """
        Copy text to clipboard so it can be pasted - avoid triggering clipboard history
        """
        if text:
            # Use pyperclip quietly
            try:
                pyperclip.copy(text)
                # Don't print message to avoid UI clutter
                return True
            except Exception as e:
                print(f"Error copying to clipboard: {str(e)}")
                return False
        return False
