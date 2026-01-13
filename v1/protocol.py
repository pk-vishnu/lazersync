MAGIC = 0xA5
VERSION = 1

TYPE_AUDIO   = 0x01
TYPE_CONTROL = 0x02

PARAM_SPEED       = 1
PARAM_DECAY       = 2
PARAM_BASE_WIDTH  = 3
PARAM_MID_GAIN    = 4
PARAM_SPARKLE     = 5

def clamp(x, lo=0, hi=255):
    return max(lo, min(hi, int(x)))

def pack_audio(bands):
    payload = bytearray(3 + 6)
    payload[0] = MAGIC
    payload[1] = VERSION
    payload[2] = TYPE_AUDIO

    for i in range(6):
        payload[3 + i] = clamp(bands[i])

    return bytes([0x00]) + payload

def pack_control(param, value, scale):
    v = int(value * scale)
    return bytes([0x00, MAGIC, VERSION, TYPE_CONTROL, param, v & 0xFF, (v >> 8) & 0xFF])
