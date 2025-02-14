import ctypes
import os
import hid
import sys
import platform

# Device Info
VENDOR_ID = 0x342D
PRODUCT_ID = 0xE484
USAGE_PAGE = 0xFF60
USAGE_ID = 0x61

class HIDDevice:
    def __init__(self):
        self.device = self.initialize_device()

    def load_hidapi_library(self):
        """Load the HIDAPI library based on the operating system."""
        try:
            if platform.system() == "Windows":
                # Load hidapi.dll on Windows
                ctypes.CDLL("hidapi.dll")
            elif platform.system() == "Darwin":  # macOS
                # Load libhidapi.dylib on macOS
                ctypes.CDLL("libhidapi.dylib")
            else:
                raise Exception("Unsupported operating system")
        except Exception as e:
            print(f"Failed to load HIDAPI library: {e}")
            sys.exit(1)

    def initialize_device(self):
        """Initializes the HID device and returns the device handle."""
        # Load the HIDAPI library
        self.load_hidapi_library()

        # Enumerate devices
        devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        if not devices:
            print("Device not connected!")
            sys.exit(1)

        # Find the specific device
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

        # Open the device
        device_path = device_info['path']
        try:
            device = hid.Device(VENDOR_ID, PRODUCT_ID, path=device_path)
        except Exception as e:
            print(f"Failed to open the device: {e}")
            sys.exit(1)
        
        return device

    def send_data(self, data):
        """Send data to the HID device."""
        report = bytes([0] + [int(x) for x in data])
        self.device.write(report)

    def cleanup(self):
        """Close the HID device."""
        self.device.close()

# Only run this test if the module is executed directly.
if __name__ == '__main__':
    device = HIDDevice()
    print("HID device initialized successfully!")
    try:
        data = device.device.read(64, timeout=500)
        print("Data read from device:", data)
    except Exception as e:
        print("Error reading from device:", e)