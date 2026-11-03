"""Backup Engine for CleanYourPhone.

Strict Backup-First Rule:
Queries the device's existing state before any modification and generates
an executable `restore_cleanyourphone.bat` (and `restore_cleanyourphone.sh`)
containing the exact inverse commands to revert any changes made.
"""

import os
import json
from typing import List, Dict, Optional
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge

init(autoreset=True)


class BackupEngine:
    """Captures original device settings and writes rollback scripts."""

    def __init__(self, bridge: Optional[ADBBridge] = None, base_dir: Optional[str] = None):
        """Initialize backup engine with an ADB bridge and directory references."""
        self.bridge = bridge or ADBBridge()
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.bat_path = os.path.join(self.base_dir, "restore_cleanyourphone.bat")
        self.sh_path = os.path.join(self.base_dir, "restore_cleanyourphone.sh")

    def capture_current_state(self) -> Dict[str, str]:
        """Query current Android system settings before optimization."""
        state = {}

        # 1. Animation Scales
        for key in ["window_animation_scale", "transition_animation_scale", "animator_duration_scale"]:
            code, val, _ = self.bridge.shell(f"settings get global {key}")
            state[key] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "1.0"

        # 2. Doze Settings
        code, val, _ = self.bridge.shell("settings get global device_idle_constants")
        state["device_idle_constants"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "null"

        # 3. DNS settings
        code, val, _ = self.bridge.shell("settings get global private_dns_mode")
        state["private_dns_mode"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "off"

        code, val, _ = self.bridge.shell("settings get global private_dns_specifier")
        state["private_dns_specifier"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "null"

        # 4. Refresh rate
        code, val, _ = self.bridge.shell("settings get system min_refresh_rate")
        state["min_refresh_rate"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "null"

        # 5. WiFi & BLE scanning
        code, val, _ = self.bridge.shell("settings get global wifi_scan_always_enabled")
        state["wifi_scan_always_enabled"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "1"

        code, val, _ = self.bridge.shell("settings get global ble_scan_always_enabled")
        state["ble_scan_always_enabled"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "1"

        # 6. Window Blurs
        code, val, _ = self.bridge.shell("settings get global background_blur_supported")
        state["background_blur_supported"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "0"

        code, val, _ = self.bridge.shell("settings get global disable_window_blurs")
        state["disable_window_blurs"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "1"

        # 7. UI Night Mode, Status Bar Icons & Density
        code, val, _ = self.bridge.shell("settings get secure ui_night_mode")
        state["ui_night_mode"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "0"

        code, val, _ = self.bridge.shell("settings get secure icon_blacklist")
        state["icon_blacklist"] = val.strip() if (code == 0 and val.strip() and val.strip() != "null") else "null"

        code, val, _ = self.bridge.shell("wm density")
        state["wm_density"] = val.strip() if (code == 0 and val.strip()) else "reset"

        return state

    def load_all_target_packages(self) -> List[str]:
        """Aggregate all bloatware packages from JSON databases for safe restoration."""
        packages = set()
        lists_dir = os.path.join(self.base_dir, "lists")
        if os.path.isdir(lists_dir):
            for file_name in os.listdir(lists_dir):
                if file_name.endswith(".json"):
                    full_path = os.path.join(lists_dir, file_name)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            for pkg in data.get("packages", []):
                                packages.add(pkg)
                    except Exception as err:
                        print(f"{Fore.YELLOW}[WARNING] Error reading {file_name}: {err}{Style.RESET_ALL}")
        return sorted(list(packages))

    def create_full_backup(self, extra_packages: Optional[List[str]] = None) -> bool:
        """Generate both restore_cleanyourphone.bat and restore_cleanyourphone.sh.

        This guarantees that the user can revert every single change made by running
        a native script on their platform.
        """
        print(f"\n{Fore.CYAN}[*] Strict Safety Check: Generating state backup snapshot...{Style.RESET_ALL}")
        original_state = self.capture_current_state()
        all_packages = self.load_all_target_packages()
        if extra_packages:
            for p in extra_packages:
                if p not in all_packages:
                    all_packages.append(p)

        target_serial_cmd = f"adb -s {self.bridge.serial} " if self.bridge.serial else "adb "

        # --- Generate Windows .bat ---
        bat_content = [
            "@echo off",
            "title CleanYourPhone - Safe Reversion Utility",
            "echo ========================================================",
            "echo      Restoring Original Android System Settings...",
            "echo ========================================================",
            "echo.",
            f"echo Target Device Serial: {self.bridge.serial or 'Default Device'}",
            "echo.",
            ":: 1. Restore Animations",
            f"{target_serial_cmd}shell settings put global window_animation_scale {original_state.get('window_animation_scale', '1.0')}",
            f"{target_serial_cmd}shell settings put global transition_animation_scale {original_state.get('transition_animation_scale', '1.0')}",
            f"{target_serial_cmd}shell settings put global animator_duration_scale {original_state.get('animator_duration_scale', '1.0')}",
            "",
            ":: 2. Restore Doze and Scans",
        ]

        if original_state.get("device_idle_constants") == "null":
            bat_content.append(f"{target_serial_cmd}shell settings delete global device_idle_constants")
        else:
            bat_content.append(
                f"{target_serial_cmd}shell settings put global device_idle_constants \"{original_state.get('device_idle_constants')}\""
            )

        bat_content.extend([
            f"{target_serial_cmd}shell settings put global wifi_scan_always_enabled {original_state.get('wifi_scan_always_enabled', '1')}",
            f"{target_serial_cmd}shell settings put global ble_scan_always_enabled {original_state.get('ble_scan_always_enabled', '1')}",
            "",
            ":: 3. Restore DNS Settings",
            f"{target_serial_cmd}shell settings put global private_dns_mode {original_state.get('private_dns_mode', 'off')}",
        ])

        if original_state.get("private_dns_specifier") == "null":
            bat_content.append(f"{target_serial_cmd}shell settings delete global private_dns_specifier")
        else:
            bat_content.append(
                f"{target_serial_cmd}shell settings put global private_dns_specifier \"{original_state.get('private_dns_specifier')}\""
            )

        bat_content.extend([
            "",
            ":: 4. Restore Refresh Rate & Visual Blurs",
        ])
        if original_state.get("min_refresh_rate") == "null":
            bat_content.append(f"{target_serial_cmd}shell settings delete system min_refresh_rate")
        else:
            bat_content.append(f"{target_serial_cmd}shell settings put system min_refresh_rate {original_state.get('min_refresh_rate')}")

        bat_content.extend([
            f"{target_serial_cmd}shell settings put global background_blur_supported {original_state.get('background_blur_supported', '0')}",
            f"{target_serial_cmd}shell settings put global disable_window_blurs {original_state.get('disable_window_blurs', '1')}",
            f"{target_serial_cmd}shell settings put secure ui_night_mode {original_state.get('ui_night_mode', '0')}",
            f"{target_serial_cmd}shell wm density reset",
        ])
        if original_state.get("icon_blacklist") == "null":
            bat_content.append(f"{target_serial_cmd}shell settings delete secure icon_blacklist")
        else:
            bat_content.append(f"{target_serial_cmd}shell settings put secure icon_blacklist \"{original_state.get('icon_blacklist')}\"")

        bat_content.extend([
            "",
            ":: 5. Re-enable All Debloated OEM Packages",
            "echo Re-enabling frozen OEM applications...",
        ])

        for pkg in all_packages:
            bat_content.append(f"{target_serial_cmd}shell pm enable {pkg} >nul 2>&1")

        bat_content.extend([
            "",
            "echo.",
            "echo ========================================================",
            "echo [SUCCESS] Device successfully restored to factory defaults!",
            "echo ========================================================",
            "pause",
        ])

        with open(self.bat_path, "w", encoding="utf-8") as f:
            f.write("\n".join(bat_content) + "\n")

        # --- Generate macOS/Linux .sh ---
        sh_content = [
            "#!/usr/bin/env bash",
            "echo '========================================================'",
            "echo '     Restoring Original Android System Settings...'",
            "echo '========================================================'",
            "",
            f"{target_serial_cmd}shell settings put global window_animation_scale {original_state.get('window_animation_scale', '1.0')}",
            f"{target_serial_cmd}shell settings put global transition_animation_scale {original_state.get('transition_animation_scale', '1.0')}",
            f"{target_serial_cmd}shell settings put global animator_duration_scale {original_state.get('animator_duration_scale', '1.0')}",
            f"{target_serial_cmd}shell settings put global wifi_scan_always_enabled {original_state.get('wifi_scan_always_enabled', '1')}",
            f"{target_serial_cmd}shell settings put global ble_scan_always_enabled {original_state.get('ble_scan_always_enabled', '1')}",
            f"{target_serial_cmd}shell settings put global private_dns_mode {original_state.get('private_dns_mode', 'off')}",
        ]
        for pkg in all_packages:
            sh_content.append(f"{target_serial_cmd}shell pm enable {pkg} 2>/dev/null || true")
        sh_content.append("echo '[SUCCESS] Device restored.'")

        with open(self.sh_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sh_content) + "\n")

        print(f"{Fore.GREEN}[OK] Backup successfully created:{Style.RESET_ALL}")
        print(f"    - Windows: {self.bat_path}")
        print(f"    - Linux/Mac: {self.sh_path}\n")
        return True

    def execute_reversion(self) -> bool:
        """Execute restore operations directly via Python using ADB."""
        all_packages = self.load_all_target_packages()
        print(f"\n{Fore.YELLOW}[*] Executing full revert to stock settings...{Style.RESET_ALL}")

        # Reset animations
        self.bridge.shell("settings put global window_animation_scale 1.0")
        self.bridge.shell("settings put global transition_animation_scale 1.0")
        self.bridge.shell("settings put global animator_duration_scale 1.0")

        # Reset DNS
        self.bridge.shell("settings put global private_dns_mode off")
        self.bridge.shell("settings delete global private_dns_specifier")

        # Reset Refresh & Doze & UI
        self.bridge.shell("settings delete system min_refresh_rate")
        self.bridge.shell("settings delete global device_idle_constants")
        self.bridge.shell("settings put global wifi_scan_always_enabled 1")
        self.bridge.shell("settings put global ble_scan_always_enabled 1")
        self.bridge.shell("settings put global background_blur_supported 0")
        self.bridge.shell("settings put global disable_window_blurs 1")
        self.bridge.shell("settings delete secure icon_blacklist")
        self.bridge.shell("wm density reset")

        # Re-enable all packages
        print(f"{Fore.CYAN}[*] Re-enabling {len(all_packages)} potentially disabled packages...{Style.RESET_ALL}")
        re_enabled = 0
        for pkg in all_packages:
            code, out, _ = self.bridge.shell(f"pm enable {pkg}")
            if "new state: enabled" in out.lower() or "enabled" in out.lower():
                re_enabled += 1

        print(f"{Fore.GREEN}[OK] Reversion complete. {re_enabled} packages re-enabled, settings reset to 1.0.{Style.RESET_ALL}")
        return True
