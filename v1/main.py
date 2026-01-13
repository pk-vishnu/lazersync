import numpy as np
import time
from device import HIDDevice

MAGIC = 0xA5
VERSION = 1
TYPE_AUDIO   = 0x01
TYPE_CONTROL = 0x02
BAND_COUNT = 6

PARAM_SPEED       = 1
PARAM_DECAY       = 2
PARAM_BASE_WIDTH  = 3
PARAM_MID_GAIN    = 4
PARAM_SPARKLE     = 5


def clamp(x, lo=0, hi=255):
    return max(lo, min(hi, int(x)))


def pack_audio_frame(bands):
    payload = bytearray(3 + BAND_COUNT)
    payload[0] = MAGIC
    payload[1] = VERSION
    payload[2] = TYPE_AUDIO
    for i in range(BAND_COUNT):
        payload[3 + i] = clamp(bands[i])
    return bytes([0x00]) + payload


def pack_control(param, value, scale):
    v = int(value * scale)
    return bytes([0x00, MAGIC, VERSION, TYPE_CONTROL, param, v & 0xFF, (v >> 8) & 0xFF])


def fake_audio_bands(t):
    bass = int((1 + np.sin(t * 2)) * 127)
    mids = int((1 + np.sin(t * 1.3)) * 80)
    highs = int((1 + np.sin(t * 3.7)) * 50)

    return [
        bass,
        bass // 2,
        mids,
        mids // 2,
        highs,
        highs // 2,
    ]


def main():
    device = HIDDevice()
    start = time.time()

    try:
        while True:
            t = time.time() - start

            # ---- Send audio ----
            bands = fake_audio_bands(t)
            audio_frame = pack_audio_frame(bands)
            device.send_frame(audio_frame)

            # ---- Live parameter modulation ----
            speed = 1.0 + np.sin(t * 0.5) * 2.0
            decay = 0.95 + np.sin(t * 0.3) * 0.03

            device.send_frame(pack_control(PARAM_SPEED, speed, 100))
            device.send_frame(pack_control(PARAM_DECAY, decay, 1000))

            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        device.cleanup()


main()
