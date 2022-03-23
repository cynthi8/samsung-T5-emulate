import socket
import struct
from abc import ABC, abstractmethod


class BaseStucture:
    def __init__(self, **kwargs):
        self.init_from_dict(**kwargs)
        for field in self._fields_:
            if len(field) > 2:
                if not hasattr(self, field[0]):
                    setattr(self, field[0], field[2])

    def init_from_dict(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def size(self):
        return struct.calcsize(self.format())

    def format(self):
        pack_format = '>'
        for field in self._fields_:
            if isinstance(field[1], BaseStucture):
                pack_format += str(field[1].size()) + 's'
            elif '<' in field[1]:
                pack_format += field[1][1:]
            else:
                pack_format += field[1]
        return pack_format

    def pack(self):
        values = []
        for field in self._fields_:
            if isinstance(field[1], BaseStucture):
                values.append(getattr(self, field[0], 0).pack())
            else:
                values.append(getattr(self, field[0], 0))
        return struct.pack(self.format(), *values)

    def unpack(self, buf):
        values = struct.unpack(self.format(), buf)
        keys_vals = {}
        for i, val in enumerate(values):
            if '<' in self._fields_[i][1][0]:
                val = struct.unpack('<' + self._fields_[i][1][1], struct.pack('>' + self._fields_[i][1][1], val))[0]
            keys_vals[self._fields_[i][0]] = val

        self.init_from_dict(**keys_vals)


class USBIPHeader(BaseStucture):
    _fields_ = [
        ('version', 'H', 0x0111),  # USB/IP version 1.1.1
        ('command', 'H'),
        ('status', 'I')
    ]


class USBInterface(BaseStucture):
    _fields_ = [
        ('bInterfaceClass', 'B'),
        ('bInterfaceSubClass', 'B'),
        ('bInterfaceProtocol', 'B'),
        ('align', 'B', 0)
    ]


class OP_REP_DevList(BaseStucture):
    _fields_ = [
        ('base', USBIPHeader()),
        ('nExportedDevice', 'I'),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B'),
        ('interfaces', USBInterface())
    ]


class OP_REP_Import(BaseStucture):
    _fields_ = [
        ('base', USBIPHeader()),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B')
    ]


class USBIP_RET_Submit(BaseStucture):
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),
        ('status', 'I'),
        ('actual_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('error_count', 'I'),
        ('setup', 'Q')
    ]

    def pack(self):
        packed_data = BaseStucture.pack(self)
        packed_data += self.data
        return packed_data


class USBIP_CMD_Submit(BaseStucture):
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),  # endpoint
        ('transfer_flags', 'I'),
        ('transfer_buffer_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('interval', 'I'),
        ('setup', '8s')
    ]


class StandardDeviceRequest(BaseStucture):
    _fields_ = [
        ('bmRequestType', 'B'),
        ('bRequest', 'B'),
        ('wValue', 'H'),
        ('wIndex', 'H'),
        ('wLength', '<H')
    ]


class DeviceDescriptor(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 18),
        ('bDescriptorType', 'B', 1),
        ('bcdUSB', 'H', 0x1001),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bMaxPacketSize0', 'B'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('iManufacturer', 'B', 0),
        ('iProduct', 'B', 0),
        ('iSerialNumber', 'B', 0),
        ('bNumConfigurations', 'B')
    ]


class DeviceConfiguration(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 2),
        ('wTotalLength', 'H'),
        ('bNumInterfaces', 'B'),
        ('bConfigurationValue', 'B', 1),
        ('iConfiguration', 'B', 0),
        ('bmAttributes', 'B', 0x80),
        ('bMaxPower', 'B')
    ]


class InterfaceDescriptor(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 4),
        ('bInterfaceNumber', 'B', 0),
        ('bAlternateSetting', 'B', 0),
        ('bNumEndpoints', 'B', 1),
        ('bInterfaceClass', 'B', 3),
        ('bInterfaceSubClass', 'B', 1),
        ('bInterfaceProtocol', 'B', 2),
        ('iInterface', 'B', 0)
    ]


class EndPoint(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 7),
        ('bDescriptorType', 'B', 0x5),
        ('bEndpointAddress', 'B', 0x81),
        ('bmAttributes', 'B', 0x3),
        ('wMaxPacketSize', 'H', 0x8000),
        ('bInterval', 'B', 0x0A)
    ]


class USBRequest():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class USBDevice(ABC):
    '''
    Abstract Base Class
    '''

    @property
    @abstractmethod
    def configurations(self): pass

    @property
    @abstractmethod
    def device_descriptor(self): pass

    def __init__(self):
        self.generate_raw_configuration()

    def generate_raw_configuration(self):
        all_configurations = bytearray()
        for configuration in self.configurations:
            all_configurations.extend(configuration.pack())
            for interface in configuration.interfaces:
                all_configurations.extend(interface.pack())
                if hasattr(interface, 'class_descriptor'):
                    all_configurations.extend(interface.class_descriptor.pack())
                for endpoint in interface.endpoints:
                    all_configurations.extend(endpoint.pack())
        self.all_configurations = all_configurations

    def send_usb_ret(self, usb_req, usb_res, usb_len, status=0):
        self.connection.sendall(USBIP_RET_Submit(command=0x3,
                                                 seqnum=usb_req.seqnum,
                                                 ep=0,
                                                 status=status,
                                                 actual_length=usb_len,
                                                 start_frame=0x0,
                                                 number_of_packets=0x0,
                                                 interval=0x0,
                                                 data=usb_res).pack())

    def handle_get_descriptor(self, control_req, usb_req):
        handled = False
        print(f"handle_get_descriptor {control_req.wValue:n}")
        if control_req.wValue == 0x1:  # Device
            handled = True
            ret = self.device_descriptor.pack()
            self.send_usb_ret(usb_req, ret, len(ret))
        elif control_req.wValue == 0x2:  # configuration
            handled = True
            ret = self.all_configurations[:control_req.wLength]
            self.send_usb_ret(usb_req, ret, len(ret))
        elif control_req.wValue == 0xA:  # config status ???
            handled = True
            self.send_usb_ret(usb_req, b'', 0, 1)

        return handled

    def handle_set_configuration(self, control_req, usb_req):
        # Only supports 1 configuration
        print(f"handle_set_configuration {control_req.wValue:n}")
        self.send_usb_ret(usb_req, b'', 0, 0)
        return True

    def handle_usb_control(self, usb_req):
        control_req = StandardDeviceRequest()
        control_req.unpack(usb_req.setup)
        handled = False
        print(f"  UC Request Type {control_req.bmRequestType}")
        print(f"  UC Request {control_req.bRequest}")
        print(f"  UC Value  {control_req.wValue}")
        print(f"  UC Index  {control_req.wIndex}")
        print(f"  UC Length {control_req.wLength}")
        if control_req.bmRequestType == 0x80:  # Host Request
            if control_req.bRequest == 0x06:  # Get Descriptor
                handled = self.handle_get_descriptor(control_req, usb_req)
            if control_req.bRequest == 0x00:  # Get STATUS
                self.send_usb_ret(usb_req, "\x01\x00", 2)
                handled = True

        if control_req.bmRequestType == 0x00:  # Host Request
            if control_req.bRequest == 0x09:  # Set Configuration
                handled = self.handle_set_configuration(control_req, usb_req)

        if not handled:
            self.handle_unknown_control(control_req, usb_req)

    def handle_usb_request(self, usb_req):
        if usb_req.ep == 0:
            self.handle_usb_control(usb_req)
        else:
            self.handle_data(usb_req)

    @abstractmethod
    def handle_data(self, usb_req):
        pass

    @abstractmethod
    def handle_unknown_control(self, usb_req):
        pass


class USBContainer:
    usb_devices = []

    def add_usb_device(self, usb_device):
        self.usb_devices.append(usb_device)

    def handle_attach(self):
        usb_dev = self.usb_devices[0]
        device_descriptor = usb_dev.device_descriptor
        return OP_REP_Import(base=USBIPHeader(command=3, status=0),
                             usbPath='/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1'.encode('ascii'),
                             busID='1-1'.encode('ascii'),
                             busnum=1,
                             devnum=2,
                             speed=2,
                             idVendor=device_descriptor.idVendor,
                             idProduct=device_descriptor.idProduct,
                             bcdDevice=device_descriptor.bcdDevice,
                             bDeviceClass=device_descriptor.bDeviceClass,
                             bDeviceSubClass=device_descriptor.bDeviceSubClass,
                             bDeviceProtocol=device_descriptor.bDeviceProtocol,
                             bConfigurationValue=usb_dev.configurations[0].bConfigurationValue,
                             bNumConfigurations=device_descriptor.bNumConfigurations,
                             bNumInterfaces=usb_dev.configurations[0].bNumInterfaces)

    def handle_device_list(self):
        usb_dev = self.usb_devices[0]
        device_descriptor = usb_dev.device_descriptor
        return OP_REP_DevList(base=USBIPHeader(command=5, status=0),
                              nExportedDevice=1,
                              usbPath='/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1'.encode('ascii'),
                              busID='1-1'.encode('ascii'),
                              busnum=1,
                              devnum=2,
                              speed=2,
                              idVendor=device_descriptor.idVendor,
                              idProduct=device_descriptor.idProduct,
                              bcdDevice=device_descriptor.bcdDevice,
                              bDeviceClass=device_descriptor.bDeviceClass,
                              bDeviceSubClass=device_descriptor.bDeviceSubClass,
                              bDeviceProtocol=device_descriptor.bDeviceProtocol,
                              bConfigurationValue=usb_dev.configurations[0].bConfigurationValue,
                              bNumConfigurations=device_descriptor.bNumConfigurations,
                              bNumInterfaces=usb_dev.configurations[0].bNumInterfaces,
                              interfaces=USBInterface(bInterfaceClass=usb_dev.configurations[0].interfaces[0].bInterfaceClass,
                                                      bInterfaceSubClass=usb_dev.configurations[0].interfaces[0].bInterfaceSubClass,
                                                      bInterfaceProtocol=usb_dev.configurations[0].interfaces[0].bInterfaceProtocol))

    def run(self, ip='0.0.0.0', port=3240):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen()
        attached = False
        req = USBIPHeader()
        while 1:
            conn, addr = s.accept()
            print('Connection address:', addr)
            while 1:
                if not attached:
                    data = conn.recv(8)
                    if not data:
                        break
                    req.unpack(data)
                    print('Header Packet')
                    print('command:', hex(req.command))
                    if req.command == 0x8005:  # OP_REQ_DEVLIST
                        print('list of devices')
                        conn.sendall(self.handle_device_list().pack())
                    elif req.command == 0x8003:  # OP_REQ_IMPORT
                        print('attach device')
                        conn.recv(32)  # receive bus id
                        conn.sendall(self.handle_attach().pack())
                        attached = True
                else:
                    print('----------------')
                    print('handles requests')
                    cmd = USBIP_CMD_Submit()
                    data = conn.recv(cmd.size())
                    cmd.unpack(data)
                    print(f"usbip cmd {cmd.command:x}")
                    print(f"usbip seqnum {cmd.seqnum:x}")
                    print(f"usbip devid {cmd.devid:x}")
                    print(f"usbip direction {cmd.direction:x}")
                    print(f"usbip ep {cmd.ep:x}")
                    print(f"usbip flags {cmd.transfer_flags:x}")
                    print(f"usbip number of packets {cmd.number_of_packets:x}")
                    print(f"usbip interval {cmd.interval:x}")
                    print("usbip setup", ''.join(["\\x{0:02x}".format(val) for val in cmd.setup]))
                    print(f"usbip buffer length {cmd.transfer_buffer_length:x}")
                    usb_req = USBRequest(seqnum=cmd.seqnum,
                                         devid=cmd.devid,
                                         direction=cmd.direction,
                                         ep=cmd.ep,
                                         flags=cmd.transfer_flags,
                                         numberOfPackets=cmd.number_of_packets,
                                         interval=cmd.interval,
                                         setup=cmd.setup,
                                         data=data)
                    self.usb_devices[0].connection = conn
                    self.usb_devices[0].handle_usb_request(usb_req)
            print('Close connection\n')
            conn.close()
