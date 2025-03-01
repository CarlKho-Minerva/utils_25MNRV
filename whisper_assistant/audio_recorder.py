import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import threading
from config import RECORDING_SAMPLE_RATE, AUDIO_TEMP_FILE

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.record_thread = None

    def start_recording(self):
        """Start recording audio in a separate thread"""
        self.recording = True
        self.audio_data = []
        self.record_thread = threading.Thread(target=self._record)
        self.record_thread.start()
        print("Recording started...")

    def stop_recording(self):
        """Stop the audio recording and save to a file"""
        if self.recording:
            self.recording = False
            if self.record_thread:
                self.record_thread.join()
            
            if len(self.audio_data) > 0:
                audio_array = np.concatenate(self.audio_data, axis=0)
                wav.write(AUDIO_TEMP_FILE, RECORDING_SAMPLE_RATE, audio_array)
                print(f"Recording saved to {AUDIO_TEMP_FILE}")
                return AUDIO_TEMP_FILE
            else:
                print("No audio recorded")
                return None
        return None

    def _record(self):
        """Record audio data from the microphone"""
        with sd.InputStream(samplerate=RECORDING_SAMPLE_RATE, channels=1) as stream:
            while self.recording:
                data, overflowed = stream.read(RECORDING_SAMPLE_RATE)
                if not overflowed:
                    self.audio_data.append(data)
