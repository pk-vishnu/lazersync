import time
import numpy as np
import matplotlib.pyplot as plt
from audio import AudioProcessor
from led import LEDControl
from device import HIDDevice

# Initialize devices and audio
device = HIDDevice()
audio_processor = AudioProcessor()
led_control = LEDControl()

previous_normalized = [0] * 6  # Number of bands
decay_rate = 0.8

# Real-time processing loop
try:
    while True:
        audio_data = audio_processor.read_audio_data()
        freqs, fft_data = audio_processor.compute_fft(audio_data)
        amplitudes = audio_processor.get_band_amplitudes(freqs, fft_data)

        # Normalize amplitudes and smooth transitions
        current_normalized = audio_processor.normalize_amplitudes(amplitudes, previous_normalized)
        smoothed_normalized = audio_processor.fade_out(previous_normalized, current_normalized, decay_rate)

        # Send data to HID device
        device.send_data(smoothed_normalized)
        
        previous_normalized = smoothed_normalized

        # Update LED visualization
        led_control.update_leds(smoothed_normalized)
        led_control.plot()

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Exiting Lazersync....")
    device.cleanup()
    led_control.cleanup()
