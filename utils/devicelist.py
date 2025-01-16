import pyaudio

p = pyaudio.PyAudio()

print("Available audio devices:")
for i in range(p.get_device_count()):
    device_info = p.get_device_info_by_index(i)
    print(f"ID: {i}, Name: {device_info['name']}, Input Channels: {device_info['maxInputChannels']}, Output Channels: {device_info['maxOutputChannels']}")

p.terminate()
