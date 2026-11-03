"""Unit tests for ADBBridge."""

import unittest
from unittest.mock import patch, MagicMock
from src.adb_bridge import ADBBridge


class TestADBBridge(unittest.TestCase):
    """Test cases for ADB command building and execution wrapper."""

    def test_build_command_without_serial(self):
        bridge = ADBBridge()
        cmd = bridge.build_command(["devices"])
        self.assertEqual(cmd, ["adb", "devices"])

    def test_build_command_with_serial(self):
        bridge = ADBBridge(serial="192.168.1.50:5555")
        cmd = bridge.build_command(["shell", "getprop", "ro.product.brand"])
        self.assertEqual(cmd, ["adb", "-s", "192.168.1.50:5555", "shell", "getprop", "ro.product.brand"])

    @patch("subprocess.run")
    def test_run_success(self, mock_subproc):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "samsung\n"
        mock_result.stderr = ""
        mock_subproc.return_value = mock_result

        bridge = ADBBridge()
        code, out, err = bridge.run(["shell", "getprop", "ro.product.brand"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "samsung")
        self.assertEqual(err, "")

    @patch.object(ADBBridge, "run")
    def test_get_devices_parsing(self, mock_run):
        mock_run.return_value = (0, "List of devices attached\nemulator-5554\tdevice\n192.168.1.20:5555\tunauthorized\n", "")
        bridge = ADBBridge()
        devices = bridge.get_devices()
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0], ("emulator-5554", "device"))
        self.assertEqual(devices[1], ("192.168.1.20:5555", "unauthorized"))

    @patch.object(ADBBridge, "run")
    def test_pair_success(self, mock_run):
        mock_run.return_value = (0, "Successfully paired to 192.168.1.50:37123 [guid: ...]", "")
        bridge = ADBBridge()
        self.assertTrue(bridge.pair("192.168.1.50:37123", "123456"))

    @patch.object(ADBBridge, "run")
    def test_pair_failure(self, mock_run):
        mock_run.return_value = (1, "", "Failed: Unable to start pairing client.")
        bridge = ADBBridge()
        self.assertFalse(bridge.pair("192.168.1.50:37123", "000000"))


if __name__ == "__main__":
    unittest.main()
