import os
import subprocess
import tempfile
from plyer import notification
from config import APP_NAME

class RecordingFeedback:
    def __init__(self):
        self.status = "idle"
        self.last_text = ""
        self._create_notification_icon()
        
    def _create_notification_icon(self):
        """Create a temporary icon file for notifications if needed"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carls_whisper.ico")
            if not os.path.exists(icon_path):
                # No icon file exists, use a default one
                self.icon_path = None
            else:
                self.icon_path = icon_path
        except:
            self.icon_path = None
    
    def show_notification_windows(self, title, message):
        """Show Windows-specific toast notification with proper app branding"""
        try:
            # Use PowerShell to create proper Windows toast notification
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $APP_ID = "CarlsWhisper.VoiceAssistant.1.0"
            
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
            "@
            
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
            """
            
            # Execute the PowerShell script
            subprocess.run(["powershell", "-Command", ps_script], 
                           capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            print(f"Windows notification failed: {str(e)}")
            return False
    
    def show_recording(self):
        """Show recording feedback using system notification"""
        self.status = "recording"
        message = "🎤 Release shift when done speaking"
        
        # Try Windows-specific notification first
        if not self.show_notification_windows("Recording", message):
            # Fall back to plyer if Windows-specific method fails
            try:
                notification.notify(
                    title="Recording",
                    message=message,
                    app_name=APP_NAME,
                    app_icon=self.icon_path,
                    timeout=1
                )
            except Exception as e:
                print("Recording started...")
        
    def show_processing(self):
        """Processing notification - skipped to improve speed"""
        self.status = "processing"
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
            
        # Try Windows-specific notification first
        if not self.show_notification_windows("Transcribed", message):
            # Fall back to plyer if Windows-specific method fails
            try:
                notification.notify(
                    title="Transcribed",
                    message=message,
                    app_name=APP_NAME,
                    app_icon=self.icon_path,
                    timeout=1
                )
            except Exception as e:
                print(f"Transcribed: {preview}")
        
    def close(self):
        """Clean up resources"""
        pass
