# Samsung T5 SSD emulation (Virtual USB device)

Emulate the Samsung T5 SSD USB transactions sent during unlock.

## Setup

#### Check that usbip is installed

```
usbip
sudo apt install linux-tools-5.13.0-37-generic
```

#### Load the Virtual Host Controller Interface module

```
sudo modprobe vhci-hcd
```

#### Start the USB emulation and list or attach to the emulated device

```
python hid-mouse.py
sudo usbip list -r 127.0.0.1
sudo usbip attach -r 127.0.0.1 -b '1-1'
```

## Potential Errors

#### To fix usbip: error: failed to open /usr/share/hwdata//usb.ids, run these commands.

_This enables usbip to decode Manufactor and Product IDs_

```
mkdir /usr/share/hwdata
ln -sf /var/lib/usbutils/usb.ids /usr/share/hwdata/
```
