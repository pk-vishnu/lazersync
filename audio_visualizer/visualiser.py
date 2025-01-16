import numpy as np
import pyaudio
import matplotlib.pyplot as plt

# Keyboard Matrix Layout
keyboard_matrix = [
    [21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, -1],  # Row 1
    [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 7],  # Row 2
    [49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 6],  # Row 3
    [50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, -1, 5],  # Row 4
    [75, 74, 73, 72, 71, 70, 69, 68, 67, 66, 65, 64, -1, 63, -1],  # Row 5
    [76, 77, 78, -1, -1, -1, 79, -1, -1, -1, 0, 1, 2, 3, 4],   # Row 6
]

# Create a mapping of matrix positions to coordinates for plotting
rows, cols = len(keyboard_matrix), len(keyboard_matrix[0])
led_positions = []
for r in range(rows):
    for c in range(cols):
        if keyboard_matrix[r][c] != -1:  # Ignore empty slots
            led_positions.append((c, rows - 1 - r))  # Flip y-axis for correct orientation

# Setup Matplotlib plot
fig, ax = plt.subplots()
ax.set_xlim(-1, cols)
ax.set_ylim(-1, rows)
ax.set_aspect('equal')
ax.axis('off')
plt.title("Lazersync")

# Initialize LED scatter plot
led_scatter = ax.scatter(
    [pos[0] for pos in led_positions],  # x-coordinates
    [pos[1] for pos in led_positions],  # y-coordinates
    c='black',  # All LEDs start off
    s=100,      # LED size
)

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

# Frequency data computation
def compute_fft(audio_data):
    fft_data = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1 / RATE)
    return freqs, np.abs(fft_data)


def get_band_amplitudes(freqs, fft_data, bands):
    amplitudes = [
        np.sum(fft_data[(freqs >= band[0]) & (freqs < band[1])])  # Sum FFT values within each band
        for band in bands
    ]
    return amplitudes
    
def normalize_amplitudes(amplitudes, max_rows=6):
    # Avoid division by zero by ensuring the maximum amplitude is never zero
    max_amplitude = max(amplitudes) if max(amplitudes) > 0 else 1e-6
    
    # Normalize amplitudes and clip them to fit within the row limit
    normalized = [
        min(int((amp / max_amplitude) * max_rows), max_rows) for amp in amplitudes
    ]
    
    # Ensure at least the first row lights up if all amplitudes are zero
    if all(amp == 0 for amp in normalized):
        normalized = [1] * len(normalized)
    
    return normalized


def update_leds(normalized_amplitudes):
    led_colors = ['black'] * len(led_positions)  # Default all LEDs to off

    # Define column groups for the 6 frequency bands
    col_groups = [
        range(0, 3),   # Band 1: Bass (columns 0, 1, 2)
        range(3, 5),   # Band 2: Bass (columns 3, 4)
        range(5, 8),   # Band 3: Mid (columns 5, 6, 7)
        range(8, 10),  # Band 4: Mid (columns 8, 9)
        range(10, 12), # Band 5: Treble (columns 10, 11)
        range(12, 15)  # Band 6: Treble (columns 12, 13, 14)
    ]

    # Iterate through the frequency bands and update the LEDs
    for band_idx, rows_lit in enumerate(normalized_amplitudes):
        for col in col_groups[band_idx]:  # Iterate through columns in this frequency band
            # Get valid rows for this column (skip -1 in keyboard_matrix)
            valid_rows = [r for r in range(rows) if keyboard_matrix[r][col] != -1]
            valid_rows.sort()  # Ensure rows are sorted from bottom to top

            # Light up rows based on amplitude
            for i, row in enumerate(valid_rows[:rows_lit]):  # Limit to `rows_lit`
                flipped_row = row  # No need to flip anymore
                if (col, flipped_row) in led_positions:
                    led_index = led_positions.index((col, flipped_row))
                    led_colors[led_index] = 'red'  # Turn on the LED
    
    # Update the LED scatter plot with new colors
    led_scatter.set_color(led_colors)


# Real-time visualization loop
try:
    while True:
        # Read audio chunk and handle small values (e.g., noise)
        audio_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        audio_data = np.where(np.abs(audio_data) < 1000, 0, audio_data)  # Remove small noise
        
        # Compute FFT to get frequency amplitudes
        freqs, fft_data = compute_fft(audio_data)
        
        # Get band amplitudes and normalize them
        amplitudes = get_band_amplitudes(freqs, fft_data, bands)
        normalized_amplitudes = normalize_amplitudes(amplitudes)
        
        # Update the LED visualization with the normalized amplitudes
        update_leds(normalized_amplitudes)
        plt.pause(0.01)

except KeyboardInterrupt:
    print("Exiting Lazersync....")
    stream.stop_stream()
    stream.close()
    p.terminate()