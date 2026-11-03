"""Unit tests for BackupEngine."""

import os
import tempfile
import unittest
from unittest.mock import patch
from src.adb_bridge import ADBBridge
from src.backup_engine import BackupEngine


class TestBackupEngine(unittest.TestCase):
    """Test suite ensuring BackupEngine enforces strict non-destructive safety."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.bridge = ADBBridge(serial="TEST_SERIAL_123")
        self.engine = BackupEngine(bridge=self.bridge, base_dir=self.temp_dir)

    def tearDown(self):
        for fname in os.listdir(self.temp_dir):
            try:
                os.remove(os.path.join(self.temp_dir, fname))
            except Exception:
                pass
        try:
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    @patch.object(ADBBridge, "shell")
    def test_capture_current_state(self, mock_shell):
        def shell_side_effect(cmd, **kwargs):
            if "window_animation_scale" in cmd:
                return 0, "1.25", ""
            if "device_idle_constants" in cmd:
                return 0, "light_after_inactive_to=30000", ""
            if "private_dns_mode" in cmd:
                return 0, "opportunistic", ""
            return 0, "1.0", ""

        mock_shell.side_effect = shell_side_effect
        state = self.engine.capture_current_state()

        self.assertEqual(state["window_animation_scale"], "1.25")
        self.assertEqual(state["device_idle_constants"], "light_after_inactive_to=30000")
        self.assertEqual(state["private_dns_mode"], "opportunistic")

    @patch.object(BackupEngine, "capture_current_state")
    @patch.object(BackupEngine, "load_all_target_packages")
    def test_create_full_backup_generates_bat_and_sh(self, mock_pkgs, mock_state):
        mock_state.return_value = {
            "window_animation_scale": "1.0",
            "transition_animation_scale": "1.0",
            "animator_duration_scale": "1.0",
            "device_idle_constants": "null",
            "private_dns_mode": "off",
            "private_dns_specifier": "null",
            "min_refresh_rate": "null",
            "wifi_scan_always_enabled": "1",
            "ble_scan_always_enabled": "1",
            "background_blur_supported": "0",
            "disable_window_blurs": "1",
        }
        mock_pkgs.return_value = ["com.samsung.android.bixby.wakeup", "com.miui.analytics"]

        success = self.engine.create_full_backup()
        self.assertTrue(success)

        # Verify .bat exists and contains inverse commands
        self.assertTrue(os.path.exists(self.engine.bat_path))
        with open(self.engine.bat_path, "r", encoding="utf-8") as f:
            bat_text = f.read()

        self.assertIn("pm enable com.samsung.android.bixby.wakeup", bat_text)
        self.assertIn("pm enable com.miui.analytics", bat_text)
        self.assertIn("settings put global window_animation_scale 1.0", bat_text)

        # Verify .sh exists
        self.assertTrue(os.path.exists(self.engine.sh_path))
        with open(self.engine.sh_path, "r", encoding="utf-8") as f:
            sh_text = f.read()
        self.assertIn("pm enable com.samsung.android.bixby.wakeup", sh_text)


if __name__ == "__main__":
    unittest.main()
