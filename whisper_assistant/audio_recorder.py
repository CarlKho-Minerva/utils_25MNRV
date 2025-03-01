import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import threading
import os
from config import RECORDING_SAMPLE_RATE, AUDIO_TEMP_FILE, MAX_RECORDING_LENGTH

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.record_thread = None
        self.chunk_size = 4096  # Smaller chunk size for better memory usage

    def start_recording(self):
        """Start recording audio in a separate thread"""
        self.recording = True
        self.audio_data = []  # Clear previous data
        self.record_thread = threading.Thread(target=self._record)
        self.record_thread.daemon = True
        self.record_thread.start()
        
    def stop_recording(self):
        """Stop the audio recording and save to a file"""
        if self.recording:
            self.recording = False
            if self.record_thread:
                self.record_thread.join(timeout=1.0)  # Add timeout to prevent hanging
            
            # Clean up any previous temp file
            if os.path.exists(AUDIO_TEMP_FILE):
                try:
                    os.remove(AUDIO_TEMP_FILE)
                except:
                    pass
            
            if len(self.audio_data) > 0:
                audio_array = np.concatenate(self.audio_data, axis=0)
                
                # Remove silence at beginning and end to improve transcription
                audio_array = self._trim_silence(audio_array)
                
                wav.write(AUDIO_TEMP_FILE, RECORDING_SAMPLE_RATE, audio_array)
                return AUDIO_TEMP_FILE
            else:
                return None
        return None
    
    def _trim_silence(self, audio_array, threshold=0.02):
        """Trim silence from beginning and end of audio"""
        # Convert to float for easier amplitude analysis
        if audio_array.dtype != np.float32:
            audio_float = audio_array.astype(np.float32) / 32768.0
        else:
            audio_float = audio_array
            
        # Calculate amplitude
        amplitude = np.abs(audio_float)
        
        # Find where audio exceeds threshold
        mask = amplitude > threshold
        
        # Find the first and last significant audio
        if np.any(mask):
            start = np.argmax(mask)
            end = len(mask) - np.argmax(mask[::-1])
            
            # Add small buffers at start and end
            start = max(0, start - int(RECORDING_SAMPLE_RATE * 0.1))
            end = min(len(audio_array), end + int(RECORDING_SAMPLE_RATE * 0.1))
            
            return audio_array[start:end]
        
        return audio_array

    def _record(self):
        """Record audio data from the microphone"""
        try:
            with sd.InputStream(
                samplerate=RECORDING_SAMPLE_RATE, 
                channels=1,
                blocksize=self.chunk_size
            ) as stream:
                max_chunks = int(MAX_RECORDING_LENGTH * RECORDING_SAMPLE_RATE / self.chunk_size)
                chunk_count = 0
                
                while self.recording and chunk_count < max_chunks:
                    data, overflowed = stream.read(self.chunk_size)
                    if not overflowed:
                        self.audio_data.append(data)
                        chunk_count += 1
                
                # If max length reached, auto-stop
                if chunk_count >= max_chunks and self.recording:
                    self.recording = False
        except Exception as e:
            print(f"Error during recording: {e}")
            self.recording = False
