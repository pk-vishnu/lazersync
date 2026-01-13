import numpy as np
import pyaudio

# Define bands globally
bands = [
    (20, 150),   # Deep bass
    (150, 500),  # Bass
    (500, 1000), # Lower mids
    (1000, 3000),# Upper mids
    (3000, 6000),# Treble 1
    (6000, 12000) # Treble 2
]

# Audio Stream setup 
'''
use Voicemeeter as middleware (Voicemeeter INPUT)
Route Audio to Voicemeeter Input and then -> OUTPUT B1 or B2
Pyaudio stream audio input_device_index should be B1/B2 
'''
class AudioProcessor:
    def __init__(self, chunk_size=700, rate=48000):
        self.chunk_size = chunk_size
        self.rate = rate
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(input_device_index=12, format=pyaudio.paInt16, channels=1, rate=self.rate, input=True, frames_per_buffer=self.chunk_size)

    def read_audio_data(self):
        try:
            audio_data = np.frombuffer(self.stream.read(self.chunk_size, exception_on_overflow=False), dtype=np.int16)
            return np.where(np.abs(audio_data) < 1000, 0, audio_data)  # Remove small noise
        except OSError as e:
            print(f"Audio input overflow: {e}")
            return np.zeros(self.chunk_size, dtype=np.int16)  # Return zeros if overflow occurs

    def compute_fft(self, audio_data):
        fft_data = np.fft.rfft(audio_data)
        freqs = np.fft.rfftfreq(len(audio_data), 1 / self.rate)
        return freqs, np.abs(fft_data)

    def get_band_amplitudes(self, freqs, fft_data):
        return [
            np.sum(fft_data[(freqs >= band[0]) & (freqs < band[1])]) 
            for band in bands  # Use the global bands variable
        ]

    def normalize_amplitudes(self, amplitudes, previous_normalized, max_rows=6, alpha=0.5):
        max_amplitude = max(amplitudes) if max(amplitudes) > 0 else 1e-6
        normalized = [
            min(int((amp / max_amplitude) * max_rows), max_rows) for amp in amplitudes
        ]
        if all(amp == 0 for amp in normalized):
            normalized = [1] * len(normalized)
        return self.smooth_transitions(normalized, previous_normalized, alpha)

    def smooth_transitions(self, new_values, previous_values, alpha=0.2):
        return [
            int(alpha * new + (1 - alpha) * prev) for new, prev in zip(new_values, previous_values)
        ]
    
    def fade_out(self, previous_values, new_values, decay_rate=0.8):
        return [
            int(prev * decay_rate) if new < prev else new
            for prev, new in zip(previous_values, new_values)
        ]