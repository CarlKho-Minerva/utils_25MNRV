import threading
import os
from plyer import notification

class RecordingFeedback:
    def __init__(self):
        self.status = "idle"
        self.last_text = ""
        
    def show_recording(self):
        """Show recording feedback using system notification"""
        self.status = "recording"
        try:
            notification.notify(
                title="Recording",
                message="🎤 Hold shift until done speaking",
                app_name="Carl's Whisper",  # This sets the app name in the notification source
                app_icon=None,              # Use default system icon instead of custom
                timeout=1
            )
        except Exception as e:
            print(f"Recording started...")
        
    def show_processing(self):
        """Processing notification - skipped to improve speed"""
        self.status = "processing"
        # Skip notification for processing to improve speed
        print("Processing audio...")
        
    def show_ready(self, text):
        """Show ready feedback with transcribed text"""
        self.status = "ready"
        self.last_text = text
        
        # Create a shorter preview of the text
        preview = text[:30] + "..." if len(text) > 30 else text
        
        try:
            notification.notify(
                title="Transcribed",
                message=f"✅ {preview}",
                app_name="Carl's Whisper",  # This sets the app name in the notification source
                app_icon=None,              # Use default system icon instead of custom
                timeout=1
            )
        except Exception as e:
            print(f"Ready: {preview}")
        
    def close(self):
        """Clean up resources"""
        pass  # No resources to clean up
