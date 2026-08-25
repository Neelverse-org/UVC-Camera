# Neelverse UVC Camera

Open-source, camera-only USB Video Class identity and validation tooling for
Linux USB-gadget capable embedded appliances.

## USB identity

Private in-house testing:

- VID: `0x1209`
- PID: `0x0001`
- Manufacturer: `Neelverse Studios Private Limited`
- Product: `Neelverse UVC Camera`

`1209:0001` is the pid.codes shared testing identity. It is not unique and
MUST NOT be redistributed, sold, or manufactured.

Requested production identity (not valid until allocated):

- VID: `0x1209`
- PID: `0x4E56`

## Safety properties

The tool refuses to alter a bound gadget and refuses any gadget containing a
non-UVC function. It modifies only VID, PID, device revision, manufacturer,
product, and serial descriptor files. It does not create a gadget or configure
video formats; use your platform's reviewed UVC setup for those functions.

## Test

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_kit.py --allow-placeholders
```

## Dry-run

On a prepared but unbound UVC-only configfs gadget:

```bash
python3 neelverse_uvc_identity.py   --identity identity/private-test.json   --gadget /sys/kernel/config/usb_gadget/kvmd
```

Review the plan, then apply only in a private test environment:

```bash
python3 neelverse_uvc_identity.py   --identity identity/private-test.json   --gadget /sys/kernel/config/usb_gadget/kvmd   --apply
```

Never set `allocation_confirmed` to true until the pid.codes PR is merged.
See `PID_CODES_GUIDE.md` for the complete registration procedure.

## Scope

This repository does not include proprietary activation/licensing systems,
Bluetooth bond data, credentials, customer data, or vendor-owned source code.
See `HARDWARE.md` for the platform disclosure.

## Licence

MIT, copyright Neelverse Studios Private Limited.
