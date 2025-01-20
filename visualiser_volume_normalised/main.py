import numpy as np
import matplotlib.pyplot as plt
from audio import *
from visualisation import *
from device import initialize_device

# Initialize HID device
device = initialize_device()

# Setup Matplotlib plot
fig, ax = plt.subplots()
ax.set_xlim(-1, len(keyboard_matrix[0]))
ax.set_ylim(-1, len(keyboard_matrix))
ax.set_aspect('equal')
ax.axis('off')

# Initialize LED scatter plot
led_scatter = ax.scatter(
    [pos[0] for pos in led_positions],
    [pos[1] for pos in led_positions],
    c='black', s=100,
)

previous_normalized = [0]*len(bands)

# Real-time visualization loop
try:
    while True:
        # Read audio chunk and handle small values (e.g., noise)
        audio_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        audio_data = np.where(np.abs(audio_data) < 1000, 0, audio_data)  # Remove small noise

        # Compute FFT to get frequency amplitudes
        freqs, fft_data = compute_fft(audio_data)

        # Get band amplitudes and normalize them based on volume
        amplitudes = get_band_amplitudes(freqs, fft_data, bands)
        current_normalized = normalize_amplitudes(amplitudes, audio_data, previous_normalized)

        # Smooth transitions
        smoothed_normalized = fade_out(previous_normalized, current_normalized, decay_rate=0.8)
        report = bytes([0] + [int(x) for x in smoothed_normalized])
        device.write(report)
        previous_normalized = smoothed_normalized

        # Update the LED visualization with the normalized amplitudes
        led_scatter = update_leds(led_scatter, [int(x) for x in smoothed_normalized], col_groups, led_positions, len(keyboard_matrix))
        plt.pause(0.01)
        
except KeyboardInterrupt:
    print("Exiting...")
    device.close()
    p.terminate()
