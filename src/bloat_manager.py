"""Bloatware Manager and Ad-Blocking Engine for CleanYourPhone.

Identifies OEM brand, parses targeted bloatware package lists, executes
safe user-level package disabling (`pm disable-user --user 0`), and configures
system-wide encrypted AdGuard DNS for native ad-blocking.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge
from src.backup_engine import BackupEngine

init(autoreset=True)


class BloatManager:
    """Handles OEM bloatware identification, package disabling, and DNS ad-blocking."""

    OEM_FILE_MAP = {
        "samsung": "bloat_samsung.json",
        "xiaomi": "bloat_xiaomi.json",
        "redmi": "bloat_xiaomi.json",
        "poco": "bloat_xiaomi.json",
        "realme": "bloat_realme.json",
        "oppo": "bloat_realme.json",
        "vivo": "bloat_vivo.json",
        "iqoo": "bloat_vivo.json",
        "oneplus": "bloat_oneplus.json",
        "google": "bloat_google.json",
    }

    def __init__(self, bridge: Optional[ADBBridge] = None, lists_dir: Optional[str] = None):
        """Initialize BloatManager with ADBBridge and directory references."""
        self.bridge = bridge or ADBBridge()
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.lists_dir = lists_dir or os.path.join(base, "lists")
        self.backup_engine = BackupEngine(bridge=self.bridge)

    def detect_oem_file(self) -> Tuple[str, str]:
        """Detect phone brand via ADB and return (normalized_brand, json_filename)."""
        brand = self.bridge.get_brand().lower().strip()
        print(f"{Fore.CYAN}[*] Detected device brand: '{brand}'{Style.RESET_ALL}")

        matched_file = None
        for key, fname in self.OEM_FILE_MAP.items():
            if key in brand:
                matched_file = fname
                break

        if not matched_file:
            print(f"{Fore.YELLOW}[!] No specific brand match for '{brand}'. Defaulting to Google standard list.{Style.RESET_ALL}")
            matched_file = "bloat_google.json"

        return brand, matched_file

    def load_packages(self, json_filename: str) -> List[str]:
        """Read and parse package array from JSON database."""
        path = os.path.join(self.lists_dir, json_filename)
        if not os.path.isfile(path):
            print(f"{Fore.RED}[!] Database file not found: {path}{Style.RESET_ALL}")
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("packages", [])
        except Exception as e:
            print(f"{Fore.RED}[!] Error reading {json_filename}: {e}{Style.RESET_ALL}")
            return []

    def get_installed_packages(self) -> List[str]:
        """Fetch list of all installed packages on the connected device."""
        code, out, _ = self.bridge.shell("pm list packages")
        if code != 0:
            return []
        return [line.replace("package:", "").strip() for line in out.splitlines() if line.strip()]

    def disable_bloatware(self, custom_packages: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Disable target OEM bloatware packages using `pm disable-user --user 0`.

        Ensures a fresh backup is generated prior to disabling packages.
        """
        # Strict Rule 1: Backup First
        self.backup_engine.create_full_backup()

        brand, json_file = self.detect_oem_file()
        target_pkgs = custom_packages if custom_packages else self.load_packages(json_file)

        if not target_pkgs:
            print(f"{Fore.YELLOW}[!] No packages to disable.{Style.RESET_ALL}")
            return {"disabled": [], "skipped": [], "failed": []}

        print(f"\n{Fore.CYAN}[*] Auditing installed packages against {json_file}...{Style.RESET_ALL}")
        installed = set(self.get_installed_packages())

        results = {"disabled": [], "skipped": [], "failed": []}

        for pkg in target_pkgs:
            if pkg not in installed:
                print(f"  {Fore.LIGHTBLACK_EX}[-] Package not present: {pkg}{Style.RESET_ALL}")
                results["skipped"].append(pkg)
                continue

            # Execute safe disable
            code, out, err = self.bridge.shell(f"pm disable-user --user 0 {pkg}")
            output = f"{out} {err}".lower()
            if code == 0 and ("disabled" in output or "new state" in output):
                print(f"  {Fore.GREEN}[OK] Disabled: {pkg}{Style.RESET_ALL}")
                results["disabled"].append(pkg)
            else:
                print(f"  {Fore.YELLOW}[!] Failed/Protected: {pkg} -> {out or err}{Style.RESET_ALL}")
                results["failed"].append(pkg)

        print(f"\n{Fore.GREEN}[+] Debloat Summary: {len(results['disabled'])} disabled, "
              f"{len(results['skipped'])} not installed, {len(results['failed'])} protected.{Style.RESET_ALL}")
        return results

    def inject_adblock_dns(self) -> bool:
        """Configure system-wide AdGuard private DNS via ADB settings."""
        print(f"\n{Fore.CYAN}Configuring system-wide private DNS...{Style.RESET_ALL}")
        c1, _, err1 = self.bridge.shell("settings put global private_dns_mode hostname")
        c2, _, err2 = self.bridge.shell("settings put global private_dns_specifier dns.adguard.com")

        if c1 == 0 and c2 == 0:
            print(f"  {Fore.GREEN}+ Enabled AdGuard encrypted DNS (blocks ad tracking & banners){Style.RESET_ALL}")
            return True
        else:
            print(f"  {Fore.YELLOW}! DNS configuration notice: {err1 or err2}{Style.RESET_ALL}")
            return False

    def run_full_debloat_pipeline(self) -> None:
        """Run complete debloat and ad-blocking sequence."""
        self.disable_bloatware()
        self.inject_adblock_dns()
