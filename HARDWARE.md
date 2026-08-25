# Hardware disclosure

Neelverse UVC Camera is a software-defined USB Video Class gadget intended for
off-the-shelf Linux single-board computers or embedded appliances that expose
a USB device/peripheral controller and a standards-compliant UVC gadget
function.

This repository does not claim ownership of, or publish modified schematics
for, the underlying third-party compute module/appliance. No custom PCB is
required by the reference implementation. The open-source work covered here
is the USB identity safety layer, UVC-only gadget policy, descriptor tooling,
configuration examples, and validation tests.

A compatible deployment platform must provide:

- a Linux kernel with ConfigFS USB gadget and UVC function support;
- a USB device/peripheral-capable port physically connected to the host;
- a video producer compatible with the platform's UVC gadget implementation;
- sufficient bandwidth for the selected UVC mode.

The project deliberately rejects HID, mass-storage, USB Ethernet and serial
functions. Those interfaces are outside this project's camera-only scope.
