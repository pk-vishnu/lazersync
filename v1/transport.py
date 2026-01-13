from device import HIDDevice

class Keyboard:
    def __init__(self):
        self.dev = HIDDevice()

    def send(self, frame):
        self.dev.send_frame(frame)

    def close(self):
        self.dev.cleanup()
