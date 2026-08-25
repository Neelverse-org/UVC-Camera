from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_kit import validate


class KitValidationTests(unittest.TestCase):
    def test_current_kit_passes_with_placeholder_exception(self) -> None:
        root = Path(__file__).resolve().parents[1]
        errors = validate(root, allow_placeholders=True)
        self.assertEqual(errors, [])

    def test_final_submission_has_no_placeholder_url(self) -> None:
        root = Path(__file__).resolve().parents[1]
        errors = validate(root, allow_placeholders=False)
        self.assertEqual(errors, [])

    def test_used_pid_is_detected_from_registry_checkout(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            registry = Path(temp)
            (registry / "1209" / "4E56").mkdir(parents=True)
            errors = validate(root, allow_placeholders=True, registry=registry)
        self.assertTrue(any("already exists" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
