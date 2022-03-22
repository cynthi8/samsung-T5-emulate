import time
import random
import datetime
from USBIP import BaseStucture, USBDevice, InterfaceDescriptor, DeviceConfigurations, EndPoint, USBContainer


# data event counter
count = 0

# Emulating USB keyboard

# HID Configuration


class HIDClass(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 0x21),  # HID
        ('bcdHID', 'H'),
        ('bCountryCode', 'B'),
        ('bNumDescriptors', 'B'),
        ('bDescriptprType2', 'B'),
        ('wDescriptionLength', 'H'),
    ]


hid_class = HIDClass(bcdHID=0x0100,  # keyboard
                     bCountryCode=0x0,
                     bNumDescriptors=0x1,
                     bDescriptprType2=0x22,  # Report
                     wDescriptionLength=0x3F00)  # Little endian


interface_d = InterfaceDescriptor(bAlternateSetting=0,
                                  bNumEndpoints=1,
                                  bInterfaceClass=3,  # class HID
                                  bInterfaceSubClass=1,
                                  bInterfaceProtocol=1,  # keyboard
                                  iInterface=0)

end_point = EndPoint(bEndpointAddress=0x81,
                     bmAttributes=0x3,
                     wMaxPacketSize=0x0800,  # Little endian
                     bInterval=0xFF)  # interval to report


configuration = DeviceConfigurations(wTotalLength=0x2200,
                                     bNumInterfaces=0x1,
                                     bConfigurationValue=0x1,
                                     iConfiguration=0x0,  # No string
                                     bmAttributes=0x80,  # valid self powered
                                     bMaxPower=50)  # 100 mah current

interface_d.descriptions = [hid_class]  # Supports only one description
interface_d.endpoints = [end_point]  # Supports only one endpoint
configuration.interfaces = [interface_d]   # Supports only one interface


class USBHID(USBDevice):
    vendorID = 0x0627
    productID = 0x01
    bcdDevice = 0x0
    bcdUSB = 0x0
    bNumConfigurations = 0x1
    bNumInterfaces = 0x1
    bConfigurationValue = 0x1
    configurations = []
    bDeviceClass = 0x0
    bDeviceSubClass = 0x0
    bDeviceProtocol = 0x0
    configurations = [configuration]  # Supports only one configuration

    def __init__(self):
        USBDevice.__init__(self)
        self.start_time = datetime.datetime.now()

    def generate_keyboard_report(self):

        arr = [0x05, 0x01,
               0x09, 0x06,  # Usage Page (Generic Desktop),
               0xA1, 0x01,  # Usage (Keyboard),
               0x05, 0x07,  # Collection (Application),
               0x19, 0xE0,  # Usage Page (Key Codes);
               0x29, 0xE7,  # Usage Minimum (224),
               0x15, 0x00,  # Usage Maximum (231),
               0x25, 0x01,  # Logical Minimum (0),
               0x75, 0x01,  # Logical Maximum (1),
               0x95, 0x08,  # Report Size (1),
               0x81, 0x02,  # Report Count (8),
               0x95, 0x01,  # Input (Data, Variable, Absolute),
               0x75, 0x08,  # Report Count (1),
               0x81, 0x01,  # Report Size (8),
               0x95, 0x05,  # Input (Constant),
               0x75, 0x01,  # Report Count (5),
               0x05, 0x08,  # Report Size (1),
               0x19, 0x01,  # Usage Page (Page# for LEDs),
               0x29, 0x05,  # Usage Minimum (1),
               0x91, 0x02,  # Usage Maximum (5),
               0x95, 0x01,  # Output (Data, Variable, Absolute),
               0x75, 0x03,  # Report Count (1),
               0x91, 0x01,  # Report Size (3),
               0x95, 0x06,  # Output (Constant),
               0x75, 0x08,  # Report Count (6),
               0x15, 0x00,  # Report Size (8),
               0x25, 0x65,  # Logical Minimum (0),
               0x05, 0x07,  # Logical Maximum(101),
               0x19, 0x00,  # Usage Page (Key Codes),
               0x29, 0x65,  # Usage Minimum (0),
               0x81, 0x00,  # Usage Maximum (101), #Input (Data, Array),
               0xC0]  # End Collection
        return_val = ''
        for val in arr:
            return_val += chr(val)
        return return_val

    def comp(self, val):
        if val >= 0:
            return val
        else:
            return 256 + val

    def handle_data(self, usb_req):
        # Sending random keyboard data
        # Send data only for 5 seconds
        # if (datetime.datetime.now() - self.start_time).seconds < 10:
        print "handle data"
        global count
        if count < 100:
            if (count % 2) == 0:
                return_val = "\x00\x00" + str(chr(random.randint(4, 29))) + "\x00\x00\x00\x00\x00"
            else:
                return_val = "\x00\x00\x00\x00\x00\x00\x00\x00"
            self.send_usb_req(usb_req, return_val, len(return_val))
        time.sleep(0.05)
        count = count + 1

    def handle_unknown_control(self, control_req, usb_req):
        if control_req.bmRequestType == 0x81:
            if control_req.bRequest == 0x6:  # Get Descriptor
                if control_req.wValue == 0x22:  # send initial report
                    print 'send initial report'
                    ret = self.generate_keyboard_report()
                    self.send_usb_req(usb_req, ret, len(ret))

        if control_req.bmRequestType == 0x21:  # Host Request
            if control_req.bRequest == 0x0a:  # set idle
                print 'Idle'
                # Idle
                self.send_usb_req(usb_req, '', 0, 0)
                pass
            if control_req.bRequest == 0x09:  # set report
                print 'set report'
                data = usb_container.usb_devices[0].connection.recv(control_req.wLength)
                # use data ?
                self.send_usb_req(usb_req, '', 0, 0)
                pass


usb_Dev = USBHID()
usb_container = USBContainer()
usb_container.add_usb_device(usb_Dev)  # Supports only one device!
usb_container.run()

# Run in cmd: usbip.exe -a 127.0.0.1 "1-1"
