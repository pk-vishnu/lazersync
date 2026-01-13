import numpy as np
import pyaudio
from scipy.signal import savgol_filter
from collections import deque
from scipy.signal import convolve

# Audio Parameters
CHUNK = 700
RATE = 48000
device_id = 27

# Frequency band ranges
bands = [
    (20, 150),   # Deep bass
    (150, 500),  # Bass
    (500, 1000), # Lower mids
    (1000, 3000),# Upper mids
    (3000, 6000),# Treble 1
    (6000, 12000) # Treble 2
]

# Audio Stream Setup
'''
use Voicemeeter as middleware (Voicemeeter INPUT)
Route Audio to Voicemeeter Input/or AUX input and then -> OUTPUT B1 or B2
Pyaudio stream audio input_device_index should be B1/B2 
'''
p = pyaudio.PyAudio()
stream = p.open(input_device_index=12, format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

def whittaker_henderson_smooth(buffer, lambda_=1e-2):
    """Applies Whittaker-Henderson smoothing using a convolution kernel."""    
    # We will use a simple smoothing filter with weights (you can adjust this kernel size)
    kernel = np.array([1,-2,1])  # A basic second derivative kernel for smoothing
    
    # Convolve with the kernel and apply lambda regularization to the result
    smoothed = convolve(buffer, kernel, mode='same', method='direct')
    
    # Apply lambda for regularization
    smoothed = buffer - lambda_ * smoothed
    
    return smoothed

# Class to manage smoothing and normalization
class AmplitudeNormalizer:
    def __init__(self, max_rows=6, buffer_size=5, alpha=0.5, window_size=5, poly_order=2):
        self.max_rows = max_rows
        self.buffer_size = buffer_size
        self.alpha = alpha
        self.window_size = window_size
        self.poly_order = poly_order

        # Initialize buffers for each frequency band
        self.buffers = [deque(maxlen=buffer_size) for _ in range(len(bands))]

    def normalize_amplitudes(self, amplitudes, audio_data):
        """Normalizes audio amplitudes and smoothens using buffers."""
        # Handle NaN values
        amplitudes = [amp if not np.isnan(amp) else 0 for amp in amplitudes]
        audio_data = np.where(np.isnan(audio_data), 0, audio_data)

        # Calculate maximum amplitude in the audio data
        max_audio_amplitude = np.max(np.abs(audio_data))
        max_audio_amplitude = max_audio_amplitude if max_audio_amplitude > 0 else 1e-6  # Avoid divide by zero
        volume_factor = (max_audio_amplitude / (2**15)) * self.max_rows

        # Normalize amplitudes
        max_amplitude = max(amplitudes) if max(amplitudes) > 0 else 1e-6
        normalized = [min(int((amp / max_amplitude) * volume_factor), self.max_rows) for amp in amplitudes]

        # If all amplitudes are zero, set normalized values to 1
        if all(amp == 0 for amp in normalized):
            normalized = [1] * len(normalized)

        # Update buffers and apply smoothing
        smoothed = []
        for i, value in enumerate(normalized):
            self.buffers[i].append(value)  # Update buffer for the band

            # # Apply smoothing using Savitzky-Golay or SMA
            # if len(self.buffers[i]) >= self.window_size:
            #     smoothed_value = savgol_filter(list(self.buffers[i]), self.window_size, self.poly_order)[-1]
            # else:
            #     smoothed_value = np.mean(self.buffers[i])  # Fallback to SMA if buffer is too small
            # smoothed.append(int(smoothed_value))
            
            # Apply Whittaker-Henderson smoothing using the buffer
            '''
            TODO: Remove whittaker, use Exponential Moving Average instead. OR try to apply this to the actual raw FFT amplitude
            and not the normalized level buffer 
            '''
            if len(self.buffers[i]) >= self.window_size:
                smoothed_value = whittaker_henderson_smooth(list(self.buffers[i]))[-1]
            else:
                smoothed_value = np.mean(self.buffers[i])

            smoothed.append(int(smoothed_value))

        return smoothed

    def smooth_transitions(self, new_values, previous_values):
        """Applies exponential smoothing for transitions."""
        return [
            self.alpha * new + (1 - self.alpha) * prev
            for new, prev in zip(new_values, previous_values)
        ]

# Compute FFT
def compute_fft(audio_data):
    """Computes FFT and returns the frequencies and their amplitudes."""
    fft_data = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1 / RATE)
    return freqs, np.abs(fft_data)

# Get Band Amplitudes
def get_band_amplitudes(freqs, fft_data, bands):
    """Calculates the sum of FFT values for each frequency band."""
    return [
        np.sum(fft_data[(freqs >= band[0]) & (freqs < band[1])]) for band in bands
    ]

# Fade Out Function
def fade_out(previous_values, new_values, decay_rate=0.1):
    """
    Gradually fade out LEDs by applying a decay to previous values.
    """
    faded_values = [
        int(prev * decay_rate) if new < prev else new  # Decay only when the value drops
        for prev, new in zip(previous_values, new_values)
    ]
    return faded_values
