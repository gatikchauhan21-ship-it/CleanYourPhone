"""Unit tests for DeviceDetector."""

import unittest
from unittest.mock import patch
from src.adb_bridge import ADBBridge
from src.device_detector import DeviceDetector


class TestDeviceDetector(unittest.TestCase):
    """Test suite for device property discovery and OEM brand categorization."""

    def setUp(self):
        self.bridge = ADBBridge(serial="TEST_SERIAL_PHONE")
        self.detector = DeviceDetector(bridge=self.bridge)

    @patch.object(ADBBridge, "shell")
    def test_detect_all_properties(self, mock_shell):
        def mock_shell_side_effect(cmd, **kwargs):
            if "ro.product.brand" in cmd:
                return 0, "samsung", ""
            if "ro.product.manufacturer" in cmd:
                return 0, "samsung", ""
            if "ro.product.model" in cmd:
                return 0, "SM-A546B", ""
            if "ro.product.device" in cmd:
                return 0, "a54x", ""
            if "ro.build.version.release" in cmd:
                return 0, "14", ""
            if "ro.build.version.sdk" in cmd:
                return 0, "34", ""
            if "ro.build.version.security_patch" in cmd:
                return 0, "2026-05-01", ""
            if "wm size" in cmd:
                return 0, "Physical size: 1080x2340", ""
            if "dumpsys display" in cmd:
                return 0, "refreshRate=120.0, fps=120", ""
            if "dumpsys battery" in cmd:
                return 0, "level: 85\nhealth: 2\n", ""
            return 0, "", ""

        mock_shell.side_effect = mock_shell_side_effect
        info = self.detector.detect_all()

        self.assertEqual(info["brand"], "Samsung")
        self.assertEqual(info["model"], "SM-A546B")
        self.assertEqual(info["android_version"], "14")
        self.assertEqual(info["battery_level"], "85%")
        self.assertEqual(info["battery_health"], "Good")
        self.assertEqual(info["oem_family"], "samsung")

    def test_classify_oem(self):
        self.assertEqual(self.detector.classify_oem("Samsung", "samsung"), "samsung")
        self.assertEqual(self.detector.classify_oem("Xiaomi", "xiaomi"), "xiaomi")
        self.assertEqual(self.detector.classify_oem("Redmi", "Xiaomi"), "xiaomi")
        self.assertEqual(self.detector.classify_oem("Realme", "realme"), "realme")
        self.assertEqual(self.detector.classify_oem("OnePlus", "oneplus"), "oneplus")
        self.assertEqual(self.detector.classify_oem("Vivo", "vivo"), "vivo")
        self.assertEqual(self.detector.classify_oem("Google", "google"), "google")


if __name__ == "__main__":
    unittest.main()
