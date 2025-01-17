import ctypes
ctypes.CDLL('../utils/hidapi.dll')
import hid


# Device Info
VENDOR_ID = 0x342D
PRODUCT_ID = 0xE484
USAGE_PAGE = 0xFF60
USAGE_ID = 0x61


def initialize_device():
    """Initializes the HID device."""
    devices = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    if len(devices) == 0:
        print("Device not connected!")
        exit()

    for device in devices:
        if device['vendor_id'] == VENDOR_ID and device['product_id'] == PRODUCT_ID and device['usage_page'] == USAGE_PAGE and device['usage'] == USAGE_ID:
            device_info = device

    device_path = device_info['path']
    device = hid.Device(VENDOR_ID, PRODUCT_ID, path=device_path)
    return device
