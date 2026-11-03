"""Unit tests for ThemeEngine and modular options."""

import unittest
from unittest.mock import patch
from src.adb_bridge import ADBBridge
from src.theme_engine import ThemeEngine
from src.optimizations import Optimizations


class TestThemeAndModularOptions(unittest.TestCase):
    """Test suite for theme restorations and modular hardware options."""

    def setUp(self):
        self.bridge = ADBBridge(serial="TEST_SERIAL_PHONE")
        self.theme = ThemeEngine(bridge=self.bridge)
        self.opts = Optimizations(bridge=self.bridge)

    @patch.object(ADBBridge, "shell")
    def test_apply_pitch_black_oled_theme(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        res = self.theme.apply_pitch_black_oled_theme()
        self.assertTrue(res)
        mock_shell.assert_any_call("cmd uimode night yes")
        mock_shell.assert_any_call("settings put secure ui_night_mode 2")

    @patch.object(ADBBridge, "shell")
    def test_clean_status_bar_clutter(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        res = self.theme.clean_status_bar_clutter()
        self.assertTrue(res)

    @patch.object(ADBBridge, "shell")
    def test_glass_ui_blurs_toggle(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        # Enable
        self.opts.set_glass_ui_blurs(enable=True)
        mock_shell.assert_any_call("settings put global background_blur_supported 1")
        mock_shell.assert_any_call("settings put global disable_window_blurs 0")

        # Disable
        self.opts.set_glass_ui_blurs(enable=False)
        mock_shell.assert_any_call("settings put global background_blur_supported 0")
        mock_shell.assert_any_call("settings put global disable_window_blurs 1")

    @patch.object(ADBBridge, "shell")
    def test_modular_animations(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        self.opts.apply_liquid_animations(scale="0.65")
        mock_shell.assert_any_call("settings put global window_animation_scale 0.65")

        self.opts.reset_animations_to_stock()
        mock_shell.assert_any_call("settings put global window_animation_scale 1.0")

    def test_resource_specifications(self):
        specs = self.opts.get_resource_specifications()
        self.assertIn("oem_debloat", specs)
        self.assertIn("glass_ui", specs)
        self.assertIn("fluid_motion", specs)
        self.assertIn("restored_theme", specs)
        self.assertIn("ram_impact", specs["glass_ui"])


if __name__ == "__main__":
    unittest.main()
