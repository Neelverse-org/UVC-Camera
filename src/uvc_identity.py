from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

_ALLOWED_FIELDS = {
    "vid",
    "pid",
    "manufacturer",
    "product",
    "serial",
    "test_only",
    "allocation_confirmed",
    "bcd_device",
}


@dataclass
class Identity:
    vid: int
    pid: int
    manufacturer: str
    product: str
    serial: str
    test_only: bool
    allocation_confirmed: bool
    bcd_device: int = 0x0100

    @classmethod
    def private_test(cls) -> "Identity":
        return cls(
            vid=0x1209,
            pid=0x0001,
            manufacturer="Neelverse Studios Private Limited",
            product="Neelverse UVC Camera",
            serial="NVS-UVC-000001",
            test_only=True,
            allocation_confirmed=False,
        )

    def validate(self) -> None:
        for label, value in (("VID", self.vid), ("PID", self.pid), ("bcdDevice", self.bcd_device)):
            if not 0 <= value <= 0xFFFF:
                raise ValueError(f"{label} must fit in 16 bits")
        for label, value in (("manufacturer", self.manufacturer), ("product", self.product)):
            if not value or not value.isascii() or len(value) > 126:
                raise ValueError(f"{label} must be non-empty ASCII and at most 126 characters")
        if not self.serial.isascii() or len(self.serial) < 12 or len(self.serial) > 64:
            raise ValueError("serial must be unique-style ASCII, 12-64 characters")
        if self.test_only:
            if (self.vid, self.pid) != (0x1209, 0x0001):
                raise ValueError("test-only identity must use pid.codes 1209:0001")
            if self.allocation_confirmed:
                raise ValueError("test-only identity cannot claim allocation confirmation")
        elif not self.allocation_confirmed:
            raise ValueError("production PID allocation has not been confirmed")


def _parse_u16(value: object, label: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError as ex:
            raise ValueError(f"invalid {label}: {value!r}") from ex
    raise ValueError(f"invalid {label} type")


def load_identity(path: Path) -> Identity:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("identity file must contain a JSON object")
    extra = set(raw) - _ALLOWED_FIELDS
    if extra:
        raise ValueError(f"unsupported fields: {', '.join(sorted(extra))}")
    required = _ALLOWED_FIELDS - {"bcd_device"}
    missing = required - set(raw)
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    identity = Identity(
        vid=_parse_u16(raw["vid"], "VID"),
        pid=_parse_u16(raw["pid"], "PID"),
        manufacturer=str(raw["manufacturer"]),
        product=str(raw["product"]),
        serial=str(raw["serial"]),
        test_only=bool(raw["test_only"]),
        allocation_confirmed=bool(raw["allocation_confirmed"]),
        bcd_device=_parse_u16(raw.get("bcd_device", 0x0100), "bcdDevice"),
    )
    identity.validate()
    return identity


def build_write_plan(gadget: Path, identity: Identity) -> dict[Path, str]:
    identity.validate()
    udc = gadget / "UDC"
    if not udc.is_file():
        raise RuntimeError(f"not a configfs USB gadget: {gadget}")
    if udc.read_text(encoding="ascii").strip():
        raise RuntimeError("USB gadget must be unbound before descriptor changes")
    functions = gadget / "functions"
    function_names = {entry.name for entry in functions.iterdir() if entry.is_dir()}
    unexpected = sorted(name for name in function_names if not name.startswith("uvc."))
    if unexpected:
        raise RuntimeError(f"non-UVC USB functions present: {', '.join(unexpected)}")
    if not any(name.startswith("uvc.") for name in function_names):
        raise RuntimeError("no UVC function is configured")
    strings = gadget / "strings" / "0x409"
    return {
        gadget / "idVendor": f"0x{identity.vid:04x}",
        gadget / "idProduct": f"0x{identity.pid:04x}",
        gadget / "bcdDevice": f"0x{identity.bcd_device:04x}",
        strings / "manufacturer": identity.manufacturer,
        strings / "product": identity.product,
        strings / "serialnumber": identity.serial,
    }


def apply_write_plan(plan: dict[Path, str]) -> None:
    for path, value in plan.items():
        path.write_text(value, encoding="ascii")
