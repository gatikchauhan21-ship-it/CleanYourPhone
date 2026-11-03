"""Unit tests for Motion Engine and Lock Screen Engine."""

import unittest
from unittest.mock import patch
from src.adb_bridge import ADBBridge
from src.motion_engine import MotionEngine
from src.lockscreen_engine import LockScreenEngine
from src.optimizations import Optimizations


class TestFlagshipFeatures(unittest.TestCase):
    """Test suite ensuring motion physics and lockscreen media work as intended."""

    def setUp(self):
        self.bridge = ADBBridge(serial="TEST_SERIAL_PHONE")
        self.motion = MotionEngine(bridge=self.bridge)
        self.lockscreen = LockScreenEngine(bridge=self.bridge)
        self.opts = Optimizations(bridge=self.bridge)

    @patch.object(ADBBridge, "shell")
    def test_fluid_transitions(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        res = self.motion.apply_fluid_transitions()
        self.assertTrue(res)
        mock_shell.assert_any_call("settings put global window_animation_scale 0.65")
        mock_shell.assert_any_call("settings put global transition_animation_scale 0.60")

    @patch.object(ADBBridge, "shell")
    def test_touch_latency_optimization(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        res = self.motion.optimize_touch_latency()
        self.assertTrue(res)
        mock_shell.assert_any_call("settings put secure long_press_timeout 250")

    @patch.object(ADBBridge, "shell")
    def test_predictive_back(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        res = self.motion.enable_predictive_back()
        self.assertTrue(res)

    @patch.object(ADBBridge, "shell")
    def test_lockscreen_music_visualizer(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        res = self.lockscreen.enable_elegant_music_visualizer()
        self.assertTrue(res)
        mock_shell.assert_any_call("settings put secure media_controls_lock_screen 1")
        mock_shell.assert_any_call("settings put secure lockscreen_media_metadata 1")

    @patch.object(ADBBridge, "shell")
    def test_modular_refresh_rate_profiles(self, mock_shell):
        mock_shell.return_value = (0, "", "")
        # 90Hz
        self.opts.set_refresh_rate_profile("90")
        mock_shell.assert_any_call("settings put system min_refresh_rate 90.0")

        # 120Hz
        self.opts.set_refresh_rate_profile("120")
        mock_shell.assert_any_call("settings put system min_refresh_rate 120.0")

        # Auto
        self.opts.set_refresh_rate_profile("auto")
        mock_shell.assert_any_call("settings delete system min_refresh_rate")


if __name__ == "__main__":
    unittest.main()
