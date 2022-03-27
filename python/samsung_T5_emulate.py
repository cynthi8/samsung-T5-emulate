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
serial_number_string = "1234567B859B"  # This was my T5 serial number, yours will be different
manufacturer_string = "Samsung"
product_string = "Portable SSD T5"

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

samsung_T5_interface = [samsung_T5_interface_descriptor_BOT, samsung_T5_interface_descriptor_UAS]  # List of interface alternatives
samsung_T5_device_configuration.interfaces = [samsung_T5_interface]


class SamsungT5(USBDevice):
    configurations = [samsung_T5_device_configuration]
    device_descriptor = samsung_T5_device_descriptor
    supported_langagues = [0x0409]  # Only supports English (United States)
    device_strings = [None, serial_number_string, manufacturer_string, product_string]

    def __init__(self):
        super().__init__()
        self.data_recieved = []

    def handle_data(self, usb_req):
        if usb_req.direction == 0: # USBIP_DIR_OUT
            self.data_recieved.append(usb_req.transfer_buffer)
            self.send_usb_ret(usb_req, b'', 0)
        elif usb_req.direction == 1: # USBIP_DIR_IN
            raise(NotImplementedError)
        

    def handle_device_specific_control(self, control_req, usb_req):
        handled = False
        if control_req.bmRequestType == 0x80:  # IN:STANDARD:DEVICE request
            if control_req.bRequest == 0x06:  # GET_DESCRIPTOR
                descriptor_index, descriptor_type = control_req.wValue.to_bytes(length=2, byteorder='big')
                if descriptor_type == 0x03:  # String Descriptor
                    if descriptor_index == 0:
                        # String Index 0 - List of supported languages
                        ret_data = bytearray()
                        for language in self.supported_langagues:
                            ret_data.extend(language.to_bytes(length=2, byteorder='big'))
                    else:
                        ret_data = self.device_strings[descriptor_index].encode('utf_8')
                    ret = bytearray([2 + len(ret_data), 0x03])
                    ret.extend(ret_data)
                    self.send_usb_ret(usb_req, ret, len(ret))
                    handled = True
        elif control_req.bmRequestType == 0b1_01_00001:  # IN:CLASS:INTERFACE request
            if control_req.bRequest == 0xFE:  # GET_MAX_LUN
                ret = bytearray([0])
                self.send_usb_ret(usb_req, ret, len(ret))
                handled = True
        if not handled:
            raise(NotImplementedError)


usb_dev = SamsungT5()
usb_container = USBContainer()
usb_container.add_usb_device(usb_dev)  # Supports only one device!
usb_container.run()
