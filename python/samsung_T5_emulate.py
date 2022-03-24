from USBIP import BaseStructure, USBDevice, InterfaceDescriptor, DeviceDescriptor, DeviceConfiguration, EndpointDescriptor, USBContainer


samsung_T5_device_descriptor = DeviceDescriptor(bDeviceClass=0x0,
                                                bDeviceSubClass=0x0,
                                                bDeviceProtocol=0x0,
                                                bMaxPacketSize0=0x40,
                                                idVendor=0x04e8,  # Samsung Electronics
                                                idProduct=0x61f6,  # T5 SSD
                                                bcdDevice=0x0100,
                                                iManufacturer=2,
                                                iProduct=3,
                                                iSerialNumber=1,
                                                bNumConfigurations=1)

samsung_T5_device_configuration = DeviceConfiguration(wTotalLength=0x0055,
                                                      bNumInterfaces=0x1,
                                                      bConfigurationValue=1,
                                                      iConfiguration=0x0,  # No string
                                                      bmAttributes=0x80,  # Valid self-powered
                                                      bMaxPower=250)  # 500 mA current

# BOT - Bulk Only Transport
samsung_T5_interface_descriptor_BOT = InterfaceDescriptor(bAlternateSetting=0,
                                                          bNumEndpoints=2,
                                                          bInterfaceClass=0x08,  # Mass Storage
                                                          bInterfaceSubClass=0x06,  # SCSI transparent command set
                                                          bInterfaceProtocol=0x50,  # BOT
                                                          iInterface=0)
samsung_T5_interface_descriptor_BOT.endpoints = []
samsung_T5_interface_descriptor_BOT.endpoints.append(EndpointDescriptor(bEndpointAddress=0x81, bmAttributes=0x02, wMaxPacketSize=512, bInterval=0))
samsung_T5_interface_descriptor_BOT.endpoints.append(EndpointDescriptor(bEndpointAddress=0x02, bmAttributes=0x02, wMaxPacketSize=512, bInterval=0))

# UAS - USB Attached SCSI
samsung_T5_interface_descriptor_UAS = InterfaceDescriptor(bAlternateSetting=1,
                                                          bNumEndpoints=4,
                                                          bInterfaceClass=0x08,  # Mass Storage
                                                          bInterfaceSubClass=0x06,  # SCSI transparent command set
                                                          bInterfaceProtocol=0x62,  # UAS
                                                          iInterface=0)


class PipeUsageClassSpecificDescriptor(BaseStructure):
    '''
    I think this is the Pipe Usage Class Specific Descriptor, but I don't have access to 
    "USB Attached SCSI (UAS) T10/2095-D" which describes it. Wireshark also doesn't know.
    '''
    _fields_ = [
        ('bLength', 'B', 4),
        ('bDescriptorType', 'B', 0x24),  # Pipe Usage Class Specific Descriptor
        ('bValue', 'H'),
    ]


UAS_endpoint_0 = EndpointDescriptor(bEndpointAddress=0x81, bmAttributes=0x02, wMaxPacketSize=512, bInterval=0)
UAS_endpoint_0.class_descriptor = PipeUsageClassSpecificDescriptor(bValue=0x0003)
UAS_endpoint_1 = EndpointDescriptor(bEndpointAddress=0x02, bmAttributes=0x02, wMaxPacketSize=512, bInterval=0)
UAS_endpoint_1.class_descriptor = PipeUsageClassSpecificDescriptor(bValue=0x0004)
UAS_endpoint_2 = EndpointDescriptor(bEndpointAddress=0x83, bmAttributes=0x02, wMaxPacketSize=512, bInterval=0)
UAS_endpoint_2.class_descriptor = PipeUsageClassSpecificDescriptor(bValue=0x0002)
UAS_endpoint_3 = EndpointDescriptor(bEndpointAddress=0x04, bmAttributes=0x02, wMaxPacketSize=512, bInterval=0)
UAS_endpoint_3.class_descriptor = PipeUsageClassSpecificDescriptor(bValue=0x0001)
samsung_T5_interface_descriptor_UAS.endpoints = [UAS_endpoint_0, UAS_endpoint_1, UAS_endpoint_2, UAS_endpoint_3]

samsung_T5_interface = [samsung_T5_interface_descriptor_BOT, samsung_T5_interface_descriptor_UAS] # List of interface alternatives
samsung_T5_device_configuration.interfaces = [samsung_T5_interface]


class SamsungT5(USBDevice):
    configurations = [samsung_T5_device_configuration]  # Supports only one configuration
    device_descriptor = samsung_T5_device_descriptor

    def __init__(self):
        super().__init__()

    def handle_data(self, usb_req):
        raise(NotImplementedError)
        self.send_usb_ret(usb_req, ret, len(ret))

    def handle_device_specific_control(self, control_req, usb_req):
        raise(NotImplementedError)
        self.send_usb_ret(usb_req, ret, len(ret))

usb_dev = SamsungT5()
usb_container = USBContainer()
usb_container.add_usb_device(usb_dev)  # Supports only one device!
usb_container.run()