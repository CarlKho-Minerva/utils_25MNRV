import time
import threading
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController, Key
from audio_recorder import AudioRecorder
from whisper_client import WhisperClient
from visual_feedback import RecordingFeedback
from config import HOLD_DURATION, KEY_TO_MONITOR, SHOW_VISUAL_FEEDBACK, AUTO_PASTE, KEEP_HISTORY

class KeyboardMonitor:
    def __init__(self):
        self.recorder = AudioRecorder()
        self.whisper = WhisperClient()
        self.key_press_time = 0
        self.is_recording = False
        self.listener = None
        self.keyboard_controller = KeyboardController()  # For auto-pasting
        
        # Initialize visual feedback if enabled
        self.feedback = RecordingFeedback() if SHOW_VISUAL_FEEDBACK else None
        
        # Store the last transcription
        self.last_transcription = ""
        
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
        if self.feedback:
            try:
                self.feedback.close()
            except:
                pass  # Suppress errors during cleanup
            
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
                    
                    # Show processing feedback safely
                    if self.feedback:
                        try:
                            self.feedback.show_processing()
                        except:
                            print("Processing audio...")
                            
                    audio_file = self.recorder.stop_recording()
                    
                    if audio_file:
                        # Process in a separate thread to avoid blocking
                        threading.Thread(
                            target=self._process_transcription,
                            args=(audio_file,),
                            daemon=True
                        ).start()
                        
            elif key == keyboard.Key.esc:
                # Stop listener with Escape key
                return False
        except AttributeError:
            pass
            
    def _process_transcription(self, audio_file):
        """Process transcription in a separate thread"""
        try:
            # Transcribe audio - no processing notification to speed things up
            transcription = self.whisper.transcribe_audio(audio_file)
            
            if transcription:
                # Store the transcription
                self.last_transcription = transcription
                
                # Copy to clipboard silently
                self.whisper.paste_text(transcription)
                
                if AUTO_PASTE:
                    # Immediately paste without delay
                    # Use direct keyboard typing to avoid clipboard history
                    self.keyboard_controller.type(transcription)
                    
                # Only show notification after all actions are complete
                if self.feedback:
                    try:
                        self.feedback.show_ready(transcription)
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"Error processing transcription: {str(e)}")
            
    def _check_hold_duration(self):
        """Check if the key has been held for the required duration"""
        if self.key_press_time == 0:
            return
            
        current_time = time.time()
        if current_time - self.key_press_time >= HOLD_DURATION:
            # Key held long enough, start recording
            if not self.is_recording:
                self.is_recording = True
                
                # Show recording feedback safely
                if self.feedback:
                    try:
                        self.feedback.show_recording()
                    except:
                        print("Recording started...")
                
                self.recorder.start_recording()
        else:
            # Check again after a short delay
            timer = threading.Timer(0.1, self._check_hold_duration)
            timer.daemon = True
            timer.start()
