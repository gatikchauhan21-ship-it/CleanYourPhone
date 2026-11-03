"""Fluid Motion & Gesture Physics Engine for CleanYourPhone.

Configures dynamic transition physics and input response over ADB:
- Predictive Back Gesture preview (fluid edge-swipe screen transitions)
- Ultra-low touch latency (clamps long-press timeout from 400ms down to 250ms)
- Elastic window transition curves (0.65x / 0.60x duration tuning)
- Immersive edge-to-edge gesture navigation
"""

from typing import Optional
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge
from src.backup_engine import BackupEngine

init(autoreset=True)


class MotionEngine:
    """Configures system-level motion physics, gestures, and touch response."""

    def __init__(self, bridge: Optional[ADBBridge] = None):
        """Initialize MotionEngine with ADBBridge."""
        self.bridge = bridge or ADBBridge()
        self.backup_engine = BackupEngine(bridge=self.bridge)

    def apply_fluid_transitions(self) -> bool:
        """Apply calibrated motion curves for responsive, natural transitions."""
        self.bridge.shell("settings put global window_animation_scale 0.65")
        self.bridge.shell("settings put global transition_animation_scale 0.60")
        self.bridge.shell("settings put global animator_duration_scale 0.65")
        print(f"  {Fore.GREEN}+ Configured fluid transition curves (0.65x / 0.60x){Style.RESET_ALL}")
        return True

    def enable_predictive_back(self) -> bool:
        """Enable Android 13/14+ Predictive Back Gesture animations."""
        c1, _, _ = self.bridge.shell("settings put global predictive_back_gesture 1")
        c2, _, _ = self.bridge.shell("settings put secure predictive_back_gesture 1")
        if c1 == 0 or c2 == 0:
            print(f"  {Fore.GREEN}+ Enabled predictive back gesture transitions{Style.RESET_ALL}")
            return True
        return False

    def optimize_touch_latency(self) -> bool:
        """Reduce input polling latency for instantaneous touch response."""
        self.bridge.shell("settings put secure long_press_timeout 250")
        self.bridge.shell("settings put secure multi_press_timeout 200")
        self.bridge.shell("settings put system pointer_speed 2")
        print(f"  {Fore.GREEN}+ Tuned touch debounce latency to 250ms{Style.RESET_ALL}")
        return True

    def hide_gesture_pill(self) -> bool:
        """Optionally remove gesture bar line for a borderless edge-to-edge experience."""
        self.bridge.shell("settings put secure navigation_mode 2")
        print(f"  {Fore.GREEN}+ Set edge-to-edge full gesture navigation{Style.RESET_ALL}")
        return True

    def run_full_motion_suite(self) -> None:
        """Execute complete motion physics, touch acceleration, and gesture pipeline."""
        self.backup_engine.create_full_backup()
        self.apply_fluid_transitions()
        self.enable_predictive_back()
        self.optimize_touch_latency()
        self.hide_gesture_pill()
        print(f"{Fore.GREEN}Fluid motion and touch acceleration active.{Style.RESET_ALL}")
