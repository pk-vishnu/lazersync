import numpy as np
import pyaudio

# Audio Parameters
CHUNK = 1024
RATE = 48000
device_id = 27

# Frequency band ranges
bands = [
    (20, 500),  # Bass 1
    (500, 2000), # Bass 2
    (2000, 4000),# Mid 1
    (4000, 7000), # Mid 2
    (7000, 9000), # Treble 1
    (9000, 12000) # Treble 2
]

# Audio Stream Setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)


def compute_fft(audio_data):
    """Computes FFT and returns the frequencies and their amplitudes."""
    fft_data = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1 / RATE)
    return freqs, np.abs(fft_data)


def normalize_amplitudes(amplitudes, audio_data, previous_normalized, max_rows=6, alpha=0.5):
    """Normalizes audio amplitudes based on the maximum value."""
    amplitudes = [amp if not np.isnan(amp) else 0 for amp in amplitudes]
    audio_data = np.where(np.isnan(audio_data), 0, audio_data)

    max_audio_amplitude = np.max(np.abs(audio_data))
    max_audio_amplitude = max_audio_amplitude if max_audio_amplitude > 0 else 1e-6
    volume_factor = (max_audio_amplitude / (2**15)) * max_rows

    max_amplitude = max(amplitudes) if max(amplitudes) > 0 else 1e-6
    normalized = [min(int((amp / max_amplitude) * volume_factor), max_rows) for amp in amplitudes]

    if all(amp == 0 for amp in normalized):
        normalized = [1] * len(normalized)

    if previous_normalized is not None:
        normalized = smooth_transitions(normalized, previous_normalized, alpha)

    return normalized


def smooth_transitions(new_values, previous_values, alpha=0.5):
    """Smoothens the transitions using an exponential moving average."""
    return [alpha * new + (1 - alpha) * prev for new, prev in zip(new_values, previous_values)]


def get_band_amplitudes(freqs, fft_data, bands):
    """Calculates the sum of FFT values for each frequency band."""
    return [
        np.sum(fft_data[(freqs >= band[0]) & (freqs < band[1])]) for band in bands
    ]

def fade_out(previous_values, new_values, decay_rate=0.8):
    """
    Gradually fade out LEDs by applying a decay to previous values.
    """
    faded_values = [
        int(prev * decay_rate) if new < prev else new  # Decay only when the value drops
        for prev, new in zip(previous_values, new_values)
    ]
    return faded_values