import threading
import time
import signal
import sys
import ctypes
from keyboard_listener import KeyboardMonitor
from config import SHOW_VISUAL_FEEDBACK, AUTO_PASTE
from register_app_id import register_app_id

def handle_exit(signum, frame):
    """Handle exit signals gracefully"""
    print("\nShutting down...")
    sys.exit(0)

def main():
    # Set up signal handlers for graceful exit
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Register app ID for better notifications
    register_app_id()
    
    print("Starting Whisper Voice Assistant")
    print("Hold right shift for 1 second to start recording")
    print("Release right shift to stop recording and transcribe")
    print("Press Esc to exit")
    
    # Display settings
    print(f"Auto-paste is {'ENABLED' if AUTO_PASTE else 'DISABLED'} - " + 
          ("text will be pasted automatically" if AUTO_PASTE else "use Ctrl+V to paste"))
    
    if SHOW_VISUAL_FEEDBACK:
        print("Visual feedback is ENABLED - you'll see system notifications")
    else:
        print("Visual feedback is DISABLED - enable in .env with SHOW_VISUAL_FEEDBACK=True")
    
    controller = KeyboardMonitor()
    controller.start_listening()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        try:
            controller.stop_listening()
        except:
            pass  # Suppress errors during shutdown
    
if __name__ == "__main__":
    main()
