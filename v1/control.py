MAGIC = 0xA5
VERSION = 1
TYPE_CONTROL = 0x02

PARAM_SPEED       = 1
PARAM_DECAY       = 2
PARAM_BASE_WIDTH  = 3
PARAM_MID_GAIN    = 4
PARAM_SPARKLE     = 5


def send_param(device, param, value, scale):
    v = int(value * scale)
    lo = v & 0xFF
    hi = (v >> 8) & 0xFF

    frame = bytes([
        0x00,        
        MAGIC,
        VERSION,
        TYPE_CONTROL,
        param,
        lo,
        hi
    ])

    device.send_frame(frame)


def set_speed(device, speed):
    send_param(device, PARAM_SPEED, speed, 100)


def set_decay(device, decay):
    send_param(device, PARAM_DECAY, decay, 1000)


def set_base_width(device, width):
    send_param(device, PARAM_BASE_WIDTH, width, 100)


def set_mid_gain(device, gain):
    send_param(device, PARAM_MID_GAIN, gain, 100)


def set_sparkle(device, sparkle):
    send_param(device, PARAM_SPARKLE, sparkle, 100)
