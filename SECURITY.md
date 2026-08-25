# Security model

The descriptor utility is fail-closed:

- dry-run is the default;
- descriptor writes require an explicit `--apply` flag;
- the gadget must be unbound before descriptor changes;
- at least one UVC function must exist;
- any HID, mass-storage, Ethernet, serial or other non-UVC function aborts;
- `1209:0001` is accepted only as a private-test identity;
- `1209:4E56` cannot be applied until `allocation_confirmed` is changed to
  `true` after the pid.codes allocation is actually merged;
- serial numbers must be unique-style printable ASCII values.

Never copy a third party's VID/PID. Never ship the shared testing PID.
Report security defects privately to the repository owner before publication.
