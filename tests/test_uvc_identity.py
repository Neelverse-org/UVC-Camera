from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.uvc_identity import Identity, apply_write_plan, build_write_plan, load_identity


class IdentityTests(unittest.TestCase):
    def test_private_test_identity_is_1209_0001(self) -> None:
        identity = Identity.private_test()
        self.assertEqual(identity.vid, 0x1209)
        self.assertEqual(identity.pid, 0x0001)
        self.assertTrue(identity.test_only)
        self.assertEqual(identity.manufacturer, "Neelverse Studios Private Limited")
        self.assertEqual(identity.product, "Neelverse UVC Camera")

    def test_requested_pid_requires_confirmed_allocation(self) -> None:
        with self.assertRaisesRegex(ValueError, "allocation has not been confirmed"):
            Identity(
                vid=0x1209,
                pid=0x4E56,
                manufacturer="Neelverse Studios Private Limited",
                product="Neelverse UVC Camera",
                serial="NVS-UVC-000001",
                test_only=False,
                allocation_confirmed=False,
            ).validate()

    def test_requested_pid_is_valid_after_confirmed_allocation(self) -> None:
        identity = Identity(
            vid=0x1209,
            pid=0x4E56,
            manufacturer="Neelverse Studios Private Limited",
            product="Neelverse UVC Camera",
            serial="NVS-UVC-000001",
            test_only=False,
            allocation_confirmed=True,
        )
        identity.validate()

    def test_serial_must_be_unique_style_ascii(self) -> None:
        identity = Identity.private_test()
        identity.serial = "short"
        with self.assertRaisesRegex(ValueError, "serial"):
            identity.validate()

    def test_load_identity_rejects_extra_fields(self) -> None:
        data = {
            "vid": "0x1209",
            "pid": "0x0001",
            "manufacturer": "Neelverse Studios Private Limited",
            "product": "Neelverse UVC Camera",
            "serial": "NVS-UVC-000001",
            "test_only": True,
            "allocation_confirmed": False,
            "hid": True,
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp, "identity.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported fields"):
                load_identity(path)


class ConfigfsPlanTests(unittest.TestCase):
    def make_gadget(self, root: Path) -> Path:
        gadget = root / "g1"
        (gadget / "strings" / "0x409").mkdir(parents=True)
        (gadget / "functions" / "uvc.usb0").mkdir(parents=True)
        for relative, value in {
            "UDC": "",
            "idVendor": "0x1d6b",
            "idProduct": "0x0104",
            "bcdDevice": "0x0100",
            "strings/0x409/manufacturer": "old",
            "strings/0x409/product": "old",
            "strings/0x409/serialnumber": "old",
        }.items():
            (gadget / relative).write_text(value, encoding="ascii")
        return gadget

    def test_write_plan_contains_only_identity_descriptors(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            gadget = self.make_gadget(Path(temp))
            plan = build_write_plan(gadget, Identity.private_test())
            self.assertEqual(
                set(plan),
                {
                    gadget / "idVendor",
                    gadget / "idProduct",
                    gadget / "bcdDevice",
                    gadget / "strings/0x409/manufacturer",
                    gadget / "strings/0x409/product",
                    gadget / "strings/0x409/serialnumber",
                },
            )
            self.assertEqual(plan[gadget / "idVendor"], "0x1209")
            self.assertEqual(plan[gadget / "idProduct"], "0x0001")

    def test_bound_gadget_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            gadget = self.make_gadget(Path(temp))
            (gadget / "UDC").write_text("fe980000.usb", encoding="ascii")
            with self.assertRaisesRegex(RuntimeError, "must be unbound"):
                build_write_plan(gadget, Identity.private_test())

    def test_non_uvc_functions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            gadget = self.make_gadget(Path(temp))
            (gadget / "functions" / "hid.usb0").mkdir()
            with self.assertRaisesRegex(RuntimeError, "non-UVC USB functions"):
                build_write_plan(gadget, Identity.private_test())

    def test_apply_writes_only_planned_descriptor_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            gadget = self.make_gadget(Path(temp))
            sentinel = gadget / "do-not-touch"
            sentinel.write_text("preserve", encoding="ascii")
            plan = build_write_plan(gadget, Identity.private_test())
            apply_write_plan(plan)
            for path, expected in plan.items():
                self.assertEqual(path.read_text(encoding="ascii"), expected)
            self.assertEqual(sentinel.read_text(encoding="ascii"), "preserve")


if __name__ == "__main__":
    unittest.main()
