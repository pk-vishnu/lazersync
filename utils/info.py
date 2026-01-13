import pyaudio
p = pyaudio.PyAudio()

info = p.get_device_info_by_index(32)
print(info)