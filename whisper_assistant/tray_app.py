import os
import sys
import threading
import time
import pyperclip
import pystray
from PIL import Image, ImageDraw
from pynput import keyboard
from keyboard_listener import KeyboardMonitor
from config import KEY_TO_MONITOR, HOLD_DURATION

class WhisperTrayApp:
    """System tray application for Whisper Assistant"""
    
    def __init__(self):
        self.keyboard_monitor = None
        self.icon = None
        self.running = False
        self.recent_transcriptions = []
    
    def create_image(self):
        """Create a simple icon for the tray"""
        width = 64
        height = 64
        color1 = (66, 133, 244)  # Blue
        color2 = (234, 67, 53)   # Red
        
        image = Image.new('RGB', (width, height), color=(0, 0, 0, 0))
        dc = ImageDraw.Draw(image)
        
        # Draw a microphone-like shape
        dc.rectangle((20, 16, 44, 40), fill=color1)
        dc.ellipse((16, 8, 48, 24), fill=color1)
        dc.rectangle((28, 40, 36, 56), fill=color2)
        dc.ellipse((24, 48, 40, 64), fill=color2)
        
        return image
    
    def setup_menu(self):
        """Create system tray menu"""
        menu_items = [
            pystray.MenuItem('Show Instructions', self.show_instructions),
            pystray.MenuItem('Copy Last Transcription', self.copy_last),
            pystray.MenuItem('', None),  # Separator
            pystray.MenuItem('Exit', self.exit_app)
        ]
        return menu_items
    
    def show_instructions(self, icon, item):
        """Show usage instructions"""
        message = f"Hold {KEY_TO_MONITOR} key for {HOLD_DURATION} seconds to start recording.\n"
        message += "Release the key when you're done speaking.\n"
        message += "The transcribed text will be pasted automatically."
        
        # Show in terminal for now - in real app would show a GUI dialog
        print("\n" + "-"*50)
        print("INSTRUCTIONS:")
        print(message)
        print("-"*50 + "\n")
    
    def copy_last(self, icon, item):
        """Copy the last transcription to clipboard"""
        if hasattr(self, 'keyboard_monitor') and self.keyboard_monitor:
            if hasattr(self.keyboard_monitor, 'recent_transcriptions') and self.keyboard_monitor.recent_transcriptions:
                last_text = self.keyboard_monitor.recent_transcriptions[-1]
                pyperclip.copy(last_text)
                print(f"Copied to clipboard: {last_text[:30]}...")
    
    def exit_app(self, icon, item):
        """Exit the application"""
        if hasattr(self, 'keyboard_monitor') and self.keyboard_monitor:
            self.keyboard_monitor.stop_listening()
        self.running = False
        icon.stop()
        os._exit(0)  # Force exit in case threads are still running
    
    def run(self):
        """Run the application"""
        self.running = True
        
        # Start keyboard monitor
        self.keyboard_monitor = KeyboardMonitor()
        self.keyboard_monitor.start_listening()
        
        # Create and run system tray icon
        image = self.create_image()
        menu = self.setup_menu()
        
        self.icon = pystray.Icon("whisper_assistant", image, "Carl's Whisper", menu)
        self.icon.run()

if __name__ == "__main__":
    app = WhisperTrayApp()
    app.run()
