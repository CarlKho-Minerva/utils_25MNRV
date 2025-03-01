import os
from plyer import notification
from config import APP_NAME

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
                message="🎤 Release shift when done speaking",
                app_name=APP_NAME,  # Use configured app name
                app_icon=None,
                timeout=1
            )
        except Exception as e:
            print(f"Recording started...")
        
    def show_processing(self):
        """Processing notification - skipped to improve speed"""
        self.status = "processing"
        # Skip notification for processing to improve speed
        print("Processing audio...")
        
    def show_ready(self, text, length=0):
        """Show ready feedback with transcribed text"""
        self.status = "ready"
        self.last_text = text
        
        # Create a shorter preview
        preview = text[:30] + "..." if len(text) > 30 else text
        
        # Add character count for longer texts
        message = f"✅ {preview}"
        if length > 50:
            message += f" ({length} chars)"
            
        try:
            notification.notify(
                title="Transcribed",
                message=message,
                app_name=APP_NAME,  # Use configured app name
                app_icon=None,
                timeout=1
            )
        except Exception as e:
            print(f"Transcribed: {preview}")
        
    def close(self):
        """Clean up resources"""
        pass
