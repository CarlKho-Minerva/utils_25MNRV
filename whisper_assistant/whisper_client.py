import os
import pyperclip
from openai import OpenAI
from config import OPENAI_API_KEY, WHISPER_MODEL

class WhisperClient:
    def __init__(self):
        # Initialize the client only once to improve connection reuse
        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        except TypeError as e:
            if 'got an unexpected keyword argument' in str(e):
                import httpx
                http_client = httpx.Client()
                self.client = OpenAI(
                    api_key=OPENAI_API_KEY,
                    http_client=http_client
                )
            else:
                raise
        
        # Cache latest results to reduce API calls for identical audio
        self.cache = {}
        self.cache_max_size = 5
            
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file using OpenAI's Whisper API
        """
        try:
            if not os.path.exists(audio_file_path):
                print(f"Audio file not found: {audio_file_path}")
                return None
                
            # Get file size and modification time for cache key
            stat = os.stat(audio_file_path)
            cache_key = f"{audio_file_path}:{stat.st_size}:{stat.st_mtime}"
            
            # Check if we have this in cache
            if cache_key in self.cache:
                return self.cache[cache_key]
                
            print("Transcribing audio...")
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file
                )
            
            if response and hasattr(response, "text"):
                transcription = response.text
                
                # Cache the result
                self.cache[cache_key] = transcription
                if len(self.cache) > self.cache_max_size:
                    # Remove oldest item
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                
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
            try:
                pyperclip.copy(text)
                return True
            except Exception as e:
                print(f"Error copying to clipboard: {str(e)}")
                return False
        return False
