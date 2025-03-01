import os
import pyperclip
from openai import OpenAI
from config import OPENAI_API_KEY, WHISPER_MODEL, LANGUAGE, LANGUAGES

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
        
        # Store detected language from last transcription
        self.last_detected_language = None
            
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
            cache_key = f"{audio_file_path}:{stat.st_size}:{stat.st_mtime}:{WHISPER_MODEL}:{LANGUAGE}"
            
            # Check if we have this in cache
            if cache_key in self.cache:
                return self.cache[cache_key]
                
            print(f"Transcribing audio using {WHISPER_MODEL}...")
            
            transcription_options = {
                "model": WHISPER_MODEL,
                "response_format": "verbose_json",  # Get additional metadata
            }
            
            # Add language specification if not on auto-detect
            if LANGUAGE != "auto":
                transcription_options["language"] = LANGUAGE
            
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    **transcription_options
                )
            
            # Extract transcription and metadata
            if hasattr(response, "text"):
                transcription = response.text
                
                # Try to get detected language if available
                try:
                    if hasattr(response, "language"):
                        self.last_detected_language = response.language
                        print(f"Detected language: {self.get_language_name(response.language)}")
                except:
                    pass
                
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
    
    def get_language_name(self, language_code):
        """Convert language code to human-readable name"""
        return LANGUAGES.get(language_code, language_code)
    
    def get_available_models(self):
        """Get list of available Whisper models"""
        try:
            models = self.client.models.list()
            whisper_models = []
            
            for model in models:
                if "whisper" in model.id.lower():
                    whisper_models.append(model.id)
            
            return whisper_models
        except:
            # If API call fails, return default models
            return ["whisper-1"]
            
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
