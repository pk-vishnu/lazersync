import ctypes
import platform
import sys

try:
    if platform.system() == "Windows":
        ctypes.CDLL('utils\hidapi.dll')
    elif platform.system() == "Darwin":
        ctypes.CDLL("libhidapi.dylib")  # Update the path to your installation if hidapi 
except OSError as e:  # Handle missing or incorrect DLL path
    print(f"Error loading HIDAPI library: {e}")
    sys.exit(1)  # Exit if the HIDAPI library fails to load

import hid

# Device info (Royal Kludge RK-R75)
# might have to make this read from a config file later

VENDOR_ID = 0x342D
PRODUCT_ID = 0xE484
USAGE_PAGE = 0xFF60
USAGE_ID = 0x61

class HIDDevice:
    def __init__(self):
        self.device = self.initialize_device()

    def initialize_device(self):
        devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        if not devices:
            print("Device not connected!")
            sys.exit(1)

        device_info = None
        for dev in devices:
            if (dev['vendor_id'] == VENDOR_ID and 
                dev['product_id'] == PRODUCT_ID and 
                dev['usage_page'] == USAGE_PAGE and 
                dev['usage'] == USAGE_ID):
                device_info = dev
                break

        if device_info is None:
            print("Specific device not found!")
            sys.exit(1)

        device_path = device_info['path']
        try:
            device = hid.Device(VENDOR_ID, PRODUCT_ID, path=device_path)
        except Exception as e:
            print(f"Failed to open the device: {e}")
            sys.exit(1)
        
        return device

    def send_frame(self, frame: bytes):
        if not isinstance(frame, (bytes, bytearray)):
            raise TypeError("frame must be bytes")
        self.device.write(frame)

    def cleanup(self):
        self.device.close()
