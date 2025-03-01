import threading
import time
from keyboard_listener import KeyboardController

def main():
    print("Starting Whisper Voice Assistant")
    print("Hold right shift for 1 second to start recording")
    print("Release right shift to stop recording and transcribe")
    print("Press Esc to exit")
    
    controller = KeyboardController()
    controller.start_listening()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        controller.stop_listening()
    
if __name__ == "__main__":
    main()
