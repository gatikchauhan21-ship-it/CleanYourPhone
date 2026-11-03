"""Battery & Screen-On-Time (SOT) Maximizer for CleanYourPhone.

Optimizes Android power profiles by eliminating phantom background tasks,
enabling cached app freezing, curtailing radio scan frequency, and forcing
instantaneous Deep Doze within 60 seconds of screen off.
"""

from typing import Optional
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge
from src.backup_engine import BackupEngine

init(autoreset=True)


class BatteryTuner:
    """Configures kernel and framework power parameters over ADB."""

    def __init__(self, bridge: Optional[ADBBridge] = None):
        """Initialize BatteryTuner with ADBBridge and backup engine."""
        self.bridge = bridge or ADBBridge()
        self.backup_engine = BackupEngine(bridge=self.bridge)

    def tune_all(self) -> bool:
        """Execute full battery optimization pipeline.

        Applies:
        1. Limit phantom processes: max_phantom_processes 1
        2. Freeze cached background processes: cached_apps_freezer enabled
        3. Aggressive Doze timers: light_after_inactive_to=15000,deep=60000
        4. Disable constant WiFi background scanning: wifi_scan_always_enabled 0
        5. Disable constant BLE background scanning: ble_scan_always_enabled 0
        """
        # Strict Rule 1: Backup First
        self.backup_engine.create_full_backup()

        print(f"\n{Fore.CYAN}Applying power optimizations...{Style.RESET_ALL}")
        success = True

        # 1. Phantom processes
        c, _, _ = self.bridge.shell("device_config put activity_manager max_phantom_processes 1")
        if c == 0:
            print(f"  {Fore.GREEN}+ Limiting phantom background processes{Style.RESET_ALL}")

        # 2. Cached apps freezer
        c, _, _ = self.bridge.shell("settings put global cached_apps_freezer enabled")
        if c == 0:
            print(f"  {Fore.GREEN}+ Freezing inactive cached apps{Style.RESET_ALL}")

        # 3. Aggressive Doze parameters
        doze_params = "light_after_inactive_to=15000,deep=60000"
        c, _, err = self.bridge.shell(f"settings put global device_idle_constants {doze_params}")
        if c == 0:
            print(f"  {Fore.GREEN}+ Tuning deep sleep timers (active after 60s idle){Style.RESET_ALL}")
        else:
            success = False

        # 4. Disable constant Wi-Fi scanning
        c, _, _ = self.bridge.shell("settings put global wifi_scan_always_enabled 0")
        if c == 0:
            print(f"  {Fore.GREEN}+ Disabling background Wi-Fi scanning loops{Style.RESET_ALL}")

        # 5. Disable constant BLE scanning
        c, _, _ = self.bridge.shell("settings put global ble_scan_always_enabled 0")
        if c == 0:
            print(f"  {Fore.GREEN}+ Disabling background Bluetooth beacon polling{Style.RESET_ALL}")

        # 6. Disable Mobile Data Always Active when connected to Wi-Fi
        c, _, _ = self.bridge.shell("settings put global mobile_data_always_on 0")
        if c == 0:
            print(f"  {Fore.GREEN}+ Putting mobile radio to sleep while on Wi-Fi{Style.RESET_ALL}")

        if success:
            print(f"{Fore.GREEN}Battery and standby tuning complete.{Style.RESET_ALL}")
        return success
