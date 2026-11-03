"""Automatic Device & Hardware Detection Module for CleanYourPhone.

Queries comprehensive device properties via ADB getprop and dumpsys
to accurately identify brand, model, SoC, display specs, and battery health.
"""

import sys
from typing import Dict, Any, Optional
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge

init(autoreset=True)


class DeviceDetector:
    """Detects and categorizes connected Android hardware and OS specifications."""

    def __init__(self, bridge: Optional[ADBBridge] = None):
        """Initialize detector with existing or newly created ADBBridge."""
        self.bridge = bridge or ADBBridge()

    def get_prop(self, key: str, default: str = "") -> str:
        """Helper to read an Android system property."""
        code, out, _ = self.bridge.shell(f"getprop {key}")
        if code == 0 and out:
            return out.strip()
        return default

    def detect_all(self) -> Dict[str, Any]:
        """Fetch all hardware, brand, and OS characteristics."""
        brand = self.get_prop("ro.product.brand", "Unknown").capitalize()
        manufacturer = self.get_prop("ro.product.manufacturer", "Unknown").capitalize()
        model = self.get_prop("ro.product.model", "Unknown Model")
        device_codename = self.get_prop("ro.product.device", "Unknown")

        # Marketing names (often stored in brand-specific getprop entries)
        marketing_name = (
            self.get_prop("ro.config.marketing_name")
            or self.get_prop("ro.product.marketname")
            or self.get_prop("ro.product.odm.model")
            or model
        )

        android_version = self.get_prop("ro.build.version.release", "Unknown")
        sdk_version = self.get_prop("ro.build.version.sdk", "Unknown")
        security_patch = self.get_prop("ro.build.version.security_patch", "Unknown")
        soc_chip = self.get_prop("ro.soc.model") or self.get_prop("ro.board.platform", "Unknown SoC")
        cpu_abi = self.get_prop("ro.product.cpu.abi", "arm64-v8a")
        serial = self.bridge.get_serialno()

        # Screen resolution & refresh rate
        resolution = self._get_screen_resolution()
        refresh_rate = self._get_refresh_rate()

        # Battery metrics
        battery_level, battery_health = self._get_battery_status()

        # OEM Classification for bloatware mapping
        oem_family = self.classify_oem(brand, manufacturer)

        return {
            "brand": brand,
            "manufacturer": manufacturer,
            "model": model,
            "marketing_name": marketing_name,
            "device_codename": device_codename,
            "android_version": android_version,
            "sdk_version": sdk_version,
            "security_patch": security_patch,
            "soc_chip": soc_chip,
            "cpu_abi": cpu_abi,
            "serial": serial,
            "resolution": resolution,
            "refresh_rate": refresh_rate,
            "battery_level": battery_level,
            "battery_health": battery_health,
            "oem_family": oem_family,
        }

    def classify_oem(self, brand: str, manufacturer: str) -> str:
        """Classify device into supported OEM database profile."""
        combined = f"{brand} {manufacturer}".lower()
        if "samsung" in combined:
            return "samsung"
        if any(x in combined for x in ["xiaomi", "redmi", "poco"]):
            return "xiaomi"
        if any(x in combined for x in ["realme", "oppo"]):
            return "realme"
        if any(x in combined for x in ["vivo", "iqoo"]):
            return "vivo"
        if "oneplus" in combined:
            return "oneplus"
        if "google" in combined:
            return "google"
        return "generic"

    def _get_screen_resolution(self) -> str:
        """Read active window manager display size."""
        code, out, _ = self.bridge.shell("wm size")
        if code == 0 and "Physical size:" in out:
            return out.split("Physical size:")[-1].strip()
        return "Unknown"

    def _get_refresh_rate(self) -> str:
        """Read current display refresh rate if available."""
        code, out, _ = self.bridge.shell("dumpsys display | grep -E 'mBaseDisplayInfo|refreshRate|fps'")
        if code == 0 and out:
            for part in out.split(","):
                if "fps" in part.lower() or "refreshrate" in part.lower():
                    return part.strip()
        return "60Hz (Default)"

    def _get_battery_status(self) -> (str, str):
        """Parse battery level and health via dumpsys battery."""
        code, out, _ = self.bridge.shell("dumpsys battery")
        level, health = "Unknown", "Good"
        if code == 0 and out:
            for line in out.splitlines():
                line = line.strip()
                if line.startswith("level:"):
                    level = f"{line.split(':', 1)[1].strip()}%"
                elif line.startswith("health:"):
                    raw_h = line.split(":", 1)[1].strip()
                    health_map = {"2": "Good", "3": "Overheat", "4": "Dead", "5": "Over voltage"}
                    health = health_map.get(raw_h, "Good")
        return level, health

    def print_summary(self, info: Optional[Dict[str, Any]] = None) -> None:
        """Print a colorful, formatted terminal card showing detected device specs."""
        if not info:
            info = self.detect_all()

        print(f"\n{Fore.GREEN}+--------------------------------------------------------+{Style.RESET_ALL}")
        print(f"{Fore.GREEN}|           [DEVICE] DETECTED ANDROID HARDWARE PROFILE   |{Style.RESET_ALL}")
        print(f"{Fore.GREEN}+--------------------------------------------------------+{Style.RESET_ALL}")
        print(f"|  {Fore.CYAN}Model Name:{Style.RESET_ALL}        {info['marketing_name']} ({info['model']})")
        print(f"|  {Fore.CYAN}Manufacturer:{Style.RESET_ALL}      {info['manufacturer']} [{info['brand']}]")
        print(f"|  {Fore.CYAN}Codename / SoC:{Style.RESET_ALL}    {info['device_codename']} / {info['soc_chip']} ({info['cpu_abi']})")
        print(f"|  {Fore.CYAN}Android OS:{Style.RESET_ALL}        Android {info['android_version']} (API {info['sdk_version']})")
        print(f"|  {Fore.CYAN}Security Patch:{Style.RESET_ALL}    {info['security_patch']}")
        print(f"|  {Fore.CYAN}Display Specs:{Style.RESET_ALL}     {info['resolution']} @ {info['refresh_rate']}")
        print(f"|  {Fore.CYAN}Battery:{Style.RESET_ALL}           {info['battery_level']} (Health: {info['battery_health']})")
        print(f"|  {Fore.CYAN}Serial / ID:{Style.RESET_ALL}       {info['serial']}")
        print(f"|  {Fore.CYAN}OEM Bloat Profile:{Style.RESET_ALL} {Fore.YELLOW}{info['oem_family'].upper()}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}+--------------------------------------------------------+{Style.RESET_ALL}\n")


if __name__ == "__main__":
    detector = DeviceDetector()
    devices = detector.bridge.get_devices()
    if not devices:
        print(f"{Fore.RED}[!] No Android devices detected via ADB.{Style.RESET_ALL}")
        print("Please enable USB/Wireless Debugging and ensure your phone is connected.")
        sys.exit(1)
    detector.print_summary()
