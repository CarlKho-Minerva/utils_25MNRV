import os
import sys
import threading
import time
import webbrowser
import pyperclip
import pystray
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from PIL import Image, ImageDraw
from pynput import keyboard
from keyboard_listener import KeyboardMonitor
from whisper_client import WhisperClient
from register_app_id import register_app_id
from config import (
    KEY_TO_MONITOR, HOLD_DURATION, APP_NAME, APP_VERSION,
    update_config, check_for_updates, WHISPER_MODEL, WHISPER_MODELS,
    LANGUAGE, LANGUAGES
)

class WhisperTrayApp:
    """System tray application for Whisper Assistant"""
    
    def __init__(self):
        # Register app ID with Windows to fix notification source
        register_app_id(APP_NAME)
        
        self.keyboard_monitor = None
        self.icon = None
        self.running = False
        self.active_key = KEY_TO_MONITOR
        self.hold_duration = HOLD_DURATION
        self.whisper_client = WhisperClient()
    
    def create_image(self):
        """Create a simple icon for the tray"""
        # Check if we have the saved icon file first
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carls_whisper.ico")
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        
        # Otherwise create a dynamic one
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
            pystray.MenuItem('Instructions', self.show_instructions),
            pystray.MenuItem('Copy Last Transcription', self.copy_last),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f'Change Hotkey (Current: {self.active_key})', self.change_hotkey),
            pystray.MenuItem(f'Hold Duration: {self.hold_duration:.1f}s', self.change_hold_duration),
            pystray.MenuItem('Select Model', self.select_model_submenu()),
            pystray.MenuItem('Language Settings', self.select_language_submenu()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Run on Startup', self.toggle_startup),
            pystray.MenuItem('Check for Updates', self.check_updates),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit', self.exit_app)
        ]
        return menu_items
    
    def select_model_submenu(self):
        """Create submenu for model selection"""
        # Create submenu items for each model
        submenu_items = []
        
        for model_id, model_info in WHISPER_MODELS.items():
            # Check mark for current selection
            checked = (model_id == WHISPER_MODEL)
            label = f"{model_id} - {model_info['description']}"
            
            # Create a menu item for this model
            item = pystray.MenuItem(
                label, 
                lambda _, m=model_id: self.change_model(m),
                checked=lambda item, m=model_id: m == WHISPER_MODEL
            )
            submenu_items.append(item)
        
        return pystray.Menu(*submenu_items)
    
    def select_language_submenu(self):
        """Create submenu for language selection"""
        # Create submenu items for each language
        submenu_items = []
        
        for lang_code, lang_name in LANGUAGES.items():
            # Check mark for current selection
            checked = (lang_code == LANGUAGE)
            
            # Create a menu item for this language
            item = pystray.MenuItem(
                lang_name, 
                lambda _, l=lang_code: self.change_language(l),
                checked=lambda item, l=lang_code: l == LANGUAGE
            )
            submenu_items.append(item)
        
        return pystray.Menu(*submenu_items)
    
    def change_model(self, model_id):
        """Change the Whisper model to use"""
        if model_id != WHISPER_MODEL:
            update_config('WHISPER_MODEL', model_id)
            self.show_notification(f"Model changed to: {model_id}")
            
            # Update menu
            self.icon.update_menu()
    
    def change_language(self, lang_code):
        """Change the language setting"""
        if lang_code != LANGUAGE:
            update_config('LANGUAGE', lang_code)
            lang_name = LANGUAGES.get(lang_code, lang_code)
            self.show_notification(f"Language changed to: {lang_name}")
            
            # Update menu
            self.icon.update_menu()
    
    def check_updates(self, icon=None, item=None):
        """Check for updates to the application"""
        self.show_notification("Checking for updates...")
        
        # Run check in background thread
        threading.Thread(target=self._perform_update_check, daemon=True).start()
    
    def _perform_update_check(self):
        """Perform the actual update check"""
        update_info = check_for_updates()
        
        if update_info['available']:
            # Show dialog with update info
            root = tk.Tk()
            root.withdraw()
            
            result = messagebox.askyesno(
                "Update Available", 
                f"A new version ({update_info['version']}) is available!\n\n"
                f"Current version: {APP_VERSION}\n\n"
                f"Would you like to open the download page?"
            )
            
            if result:
                webbrowser.open(update_info['url'])
                
            root.destroy()
        else:
            self.show_notification(f"You're using the latest version ({APP_VERSION})")
    
    def show_instructions(self, icon, item):
        """Show usage instructions"""
        message = f"Hold {self.active_key} key for {self.hold_duration} seconds to start recording.\n"
        message += "Release the key when you're done speaking.\n"
        message += "The transcribed text will be pasted automatically."
        
        # Create a simple dialog
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        dialog = tk.Toplevel(root)
        dialog.title(f"{APP_NAME} Instructions")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = ttk.Label(frame, text=message, wraplength=360, justify="left")
        label.pack(pady=10)
        
        ok_button = ttk.Button(frame, text="OK", command=dialog.destroy)
        ok_button.pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        dialog.transient(root)
        dialog.wait_window(dialog)
        root.destroy()
    
    def copy_last(self, icon, item):
        """Copy the last transcription to clipboard"""
        if hasattr(self, 'keyboard_monitor') and self.keyboard_monitor:
            if hasattr(self.keyboard_monitor, 'recent_transcriptions') and self.keyboard_monitor.recent_transcriptions:
                last_text = self.keyboard_monitor.recent_transcriptions[-1]
                pyperclip.copy(last_text)
                self.show_notification(f"Copied: {last_text[:30]}..." if len(last_text) > 30 else last_text)
    
    def change_hotkey(self, icon, item):
        """Change the hotkey used for recording"""
        root = tk.Tk()
        root.withdraw()
        
        dialog = tk.Toplevel(root)
        dialog.title("Change Hotkey")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = ttk.Label(frame, text="Press any key to set as the new hotkey...", wraplength=260)
        label.pack(pady=10)
        
        key_label = ttk.Label(frame, text="Current: " + self.active_key, font=("Arial", 12, "bold"))
        key_label.pack(pady=10)
        
        cancel_button = ttk.Button(frame, text="Cancel", command=dialog.destroy)
        cancel_button.pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        def on_key_press(key):
            try:
                key_name = key.name if hasattr(key, 'name') else key.char
                key_label.config(text=f"Selected: {key_name}")
                self.active_key = key_name
                update_config('KEY_TO_MONITOR', key_name)
                
                # Restart keyboard monitor with new key
                if self.keyboard_monitor:
                    self.keyboard_monitor.stop_listening()
                    self.keyboard_monitor = KeyboardMonitor(key_monitor=key_name)
                    self.keyboard_monitor.start_listening()
                
                # Update menu
                self.icon.update_menu()
                
                # Close dialog after short delay
                dialog.after(1000, dialog.destroy)
                return False  # Stop listener
            except AttributeError:
                pass
            except Exception as e:
                print(f"Error setting hotkey: {str(e)}")
                dialog.destroy()
            
        listener = keyboard.Listener(on_press=on_key_press)
        listener.start()
        
        dialog.transient(root)
        dialog.wait_window(dialog)
        if listener.is_alive():
            listener.stop()
        root.destroy()
    
    def change_hold_duration(self, icon, item):
        """Change how long to hold the key before recording starts"""
        root = tk.Tk()
        root.withdraw()
        
        new_duration = simpledialog.askfloat(
            "Hold Duration", 
            "Enter new hold duration in seconds:",
            minvalue=0.1, 
            maxvalue=5.0,
            initialvalue=self.hold_duration
        )
        
        if new_duration is not None:
            self.hold_duration = float(new_duration)
            update_config('HOLD_DURATION', str(self.hold_duration))
            
            # Restart keyboard monitor with new duration
            if self.keyboard_monitor:
                self.keyboard_monitor.stop_listening()
                self.keyboard_monitor = KeyboardMonitor()
                self.keyboard_monitor.start_listening()
            
            # Update menu
            self.icon.update_menu()
            
        root.destroy()
    
    def toggle_startup(self, icon, item):
        """Toggle whether the app runs on startup"""
        startup_folder = os.path.join(
            os.getenv("APPDATA"), 
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
        )
        startup_path = os.path.join(startup_folder, "Carl's Whisper.lnk")
        
        if os.path.exists(startup_path):
            # Remove from startup
            try:
                os.remove(startup_path)
                self.show_notification("Removed from startup")
            except Exception as e:
                self.show_notification(f"Error: {str(e)}")
        else:
            # Add to startup - use installer function
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(script_dir)
            
            try:
                from installer import add_to_startup
                result = add_to_startup()
                if result:
                    self.show_notification("Added to startup")
                else:
                    self.show_notification("Failed to add to startup")
            except Exception as e:
                self.show_notification(f"Error: {str(e)}")
    
    def show_notification(self, message):
        """Show a notification balloon"""
        try:
            self.icon.notify(message)
        except:
            print(message)
    
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
        
        # Check for updates on startup if enabled
        if check_for_updates()['available']:
            self._perform_update_check()
        
        # Start keyboard monitor
        self.keyboard_monitor = KeyboardMonitor(key_monitor=self.active_key)
        self.keyboard_monitor.start_listening()
        
        # Create and run system tray icon
        image = self.create_image()
        
        self.icon = pystray.Icon(APP_NAME, image, APP_NAME)
        self.icon.menu = pystray.Menu(*self.setup_menu())
        self.icon.run()

if __name__ == "__main__":
    app = WhisperTrayApp()
    app.run()
