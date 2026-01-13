import time
import numpy as np
from audio import FakeAudio
from protocol import pack_audio, pack_control, PARAM_SPEED, PARAM_DECAY
from transport import Keyboard

audio = FakeAudio()
kb = Keyboard()

start = time.time()

try:
    while True:
        bands = audio.get_bands()
        kb.send(pack_audio(bands))

        t = time.time() - start
        speed = 1.0 + np.sin(t * 0.5) * 2.0
        decay = 0.95 + np.sin(t * 0.3) * 0.03

        kb.send(pack_control(PARAM_SPEED, speed, 100))
        kb.send(pack_control(PARAM_DECAY, decay, 1000))

        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    kb.close()
