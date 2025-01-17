import numpy as np
import pyaudio
import matplotlib.pyplot as plt
import ctypes
ctypes.CDLL('../utils/hidapi.dll')
import hid
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

#Device info
VENDOR_ID = 0x342D
PRODUCT_ID = 0xE484
USAGE_PAGE = 0xFF60
USAGE_ID = 0x61
devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
print(devices)
if len(devices) == 0:
    print("Device not connected!")
    exit()
for device in devices:
    if device['vendor_id'] == VENDOR_ID and device['product_id'] == PRODUCT_ID and device['usage_page'] == USAGE_PAGE and device['usage'] == USAGE_ID:
        device_info = device

device_path = device_info['path']
device = hid.Device(VENDOR_ID, PRODUCT_ID, path=device_path)

# Setup Matplotlib plot
fig, ax = plt.subplots()
ax.set_xlim(-1, cols)
ax.set_ylim(-1, rows)
ax.set_aspect('equal')
ax.axis('off')

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

def compute_fft(audio_data):
    # Perform FFT and get frequency components
    fft_data = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1 / RATE)
    return freqs, np.abs(fft_data)


def normalize_amplitudes(amplitudes, audio_data, max_rows=6, previous_normalized=None, alpha=0.5):
    # Handle NaN values
    amplitudes = [amp if not np.isnan(amp) else 0 for amp in amplitudes]
    audio_data = np.where(np.isnan(audio_data), 0, audio_data)

    # Calculate the maximum amplitude in the current raw audio data
    max_audio_amplitude = np.max(np.abs(audio_data))
    max_audio_amplitude = max_audio_amplitude if max_audio_amplitude > 0 else 1e-6

    # Normalize the audio data's maximum amplitude to fit between 0 and max_rows
    volume_factor = (max_audio_amplitude / (2**15)) * max_rows  # Assuming 16-bit audio

    # Avoid division by zero
    max_amplitude = max(amplitudes) if max(amplitudes) > 0 else 1e-6

    # Normalize each frequency band's amplitude based on the audio volume
    normalized = [
        min(int((amp / max_amplitude) * volume_factor), max_rows) for amp in amplitudes
    ]

    # Ensure at least the first row lights up if all amplitudes are zero
    if all(amp == 0 for amp in normalized):
        normalized = [1] * len(normalized)

    # Smooth transitions using EMA
    if previous_normalized is not None:
        normalized = smooth_transitions(normalized, previous_normalized, alpha)

    return normalized


def smooth_transitions(new_values, previous_values, alpha=0.5):
    # Apply exponential moving average (EMA)
    smoothed = [
        alpha * new + (1 - alpha) * prev for new, prev in zip(new_values, previous_values)
    ]
    return smoothed


def interpolate_frames(current_frame, next_frame, steps=5):
    # Generate intermediate frames between current and next
    interpolated_frames = []
    for t in np.linspace(0, 1, steps):
        interpolated_frame = [
            int(current * (1 - t) + next * t) for current, next in zip(current_frame, next_frame)
        ]
        interpolated_frames.append(interpolated_frame)
    return interpolated_frames


def get_band_amplitudes(freqs, fft_data, bands):
    # Use list comprehension and vectorized numpy operations
    amplitudes = [
        np.sum(fft_data[(freqs >= band[0]) & (freqs < band[1])])  # Sum FFT values within each band
        for band in bands
    ]
    return amplitudes



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
        
        # Handle NaN values in FFT data
        fft_data = np.nan_to_num(fft_data)  # Replace NaNs in FFT data with 0
        
        # Get band amplitudes and normalize them based on volume
        amplitudes = get_band_amplitudes(freqs, fft_data, bands)
        
        # Handle NaN values in amplitudes
        amplitudes = [amp if not np.isnan(amp) else 0 for amp in amplitudes]  # Replace NaNs with 0
        
        normalized_amplitudes = normalize_amplitudes(amplitudes, audio_data)
        report = bytes([0] + normalized_amplitudes)
        print("Sending to QMK: ", report)
        device.write(report)
        # Update the LED visualization with the normalized amplitudes
        update_leds(normalized_amplitudes)
        plt.pause(0.01)

except KeyboardInterrupt:
    print("Exiting Lazersync...")
    stream.stop_stream()
    stream.close()
    device.close()
    p.terminate()
