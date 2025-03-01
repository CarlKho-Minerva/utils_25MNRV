import time
import threading
from pynput import keyboard
from audio_recorder import AudioRecorder
from whisper_client import WhisperClient
from config import HOLD_DURATION, KEY_TO_MONITOR

class KeyboardController:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.whisper = WhisperClient()
        self.key_press_time = 0
        self.is_recording = False
        self.listener = None
        
    def start_listening(self):
        """Start listening for keyboard events"""
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.listener.start()
        print(f"Listening for {KEY_TO_MONITOR} key hold ({HOLD_DURATION} seconds)...")
        
    def stop_listening(self):
        """Stop the keyboard listener"""
        if self.listener:
            self.listener.stop()
            
    def on_press(self, key):
        """Handle key press events"""
        try:
            # Check if the right shift key is pressed
            if key == keyboard.Key.shift_r and not self.is_recording:
                if self.key_press_time == 0:  # Initial press
                    self.key_press_time = time.time()
                    # Start a timer to check for hold duration
                    self._check_hold_duration()
        except AttributeError:
            pass
            
    def on_release(self, key):
        """Handle key release events"""
        try:
            if key == keyboard.Key.shift_r:
                self.key_press_time = 0
                
                # If recording, stop and process
                if self.is_recording:
                    self.is_recording = False
                    audio_file = self.recorder.stop_recording()
                    
                    if audio_file:
                        # Transcribe and paste
                        transcription = self.whisper.transcribe_audio(audio_file)
                        self.whisper.paste_text(transcription)
                        
            elif key == keyboard.Key.esc:
                # Stop listener with Escape key
                return False
        except AttributeError:
            pass
            
    def _check_hold_duration(self):
        """Check if the key has been held for the required duration"""
        if self.key_press_time == 0:
            return
            
        current_time = time.time()
        if current_time - self.key_press_time >= HOLD_DURATION:
            # Key held long enough, start recording
            if not self.is_recording:
                self.is_recording = True
                self.recorder.start_recording()
        else:
            # Check again after a short delay
            timer = threading.Timer(0.1, self._check_hold_duration)
            timer.daemon = True
            timer.start()
