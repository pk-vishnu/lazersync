import ctypes
ctypes.CDLL('../utils/hidapi.dll')
import hid

class HIDDevice:
    def __init__(self, vendor_id=0x342D, product_id=0xE484, usage_page=0xFF60, usage_id=0x61):
        self.device = self.init_device(vendor_id, product_id, usage_page, usage_id)

    def init_device(self, vendor_id, product_id, usage_page, usage_id):
        devices = hid.enumerate(vendor_id, product_id)
        if len(devices) == 0:
            print("Device not connected!")
            exit()
        for device in devices:
            if device['vendor_id'] == vendor_id and device['product_id'] == product_id and device['usage_page'] == usage_page and device['usage'] == usage_id:
                device_path = device['path']
                return hid.Device(vendor_id, product_id, path=device_path)
        print("Device not found!")
        exit()

    def send_data(self, data):
        report = bytes([0] + [int(x) for x in data])
        print("Sending to device:", report)
        self.device.write(report)

    def cleanup(self):
        self.device.close()
