"""ADB Bridge Module for CleanYourPhone.

Handles discovery, wireless pairing (`adb pair`), connection (`adb connect`),
and low-level command dispatch via the Android Debug Bridge.
"""

import shutil
import subprocess
import time
from typing import List, Optional, Tuple
from colorama import Fore, Style, init

init(autoreset=True)


class ADBBridge:
    """Manages ADB communications and device lifecycle."""

    def __init__(self, serial: Optional[str] = None):
        """Initialize ADBBridge with an optional target device serial."""
        self.serial = serial
        self._check_adb_binary()

    def _check_adb_binary(self) -> bool:
        """Verify that the adb executable exists in PATH."""
        if not shutil.which("adb"):
            print(f"{Fore.YELLOW}[WARNING] 'adb' executable not found in PATH.{Style.RESET_ALL}")
            print("Please install Android SDK Platform-Tools and ensure 'adb' is added to PATH.")
            return False
        return True

    def build_command(self, args: List[str]) -> List[str]:
        """Construct the ADB command array, injecting the target serial if set."""
        cmd = ["adb"]
        if self.serial:
            cmd.extend(["-s", self.serial])
        cmd.extend(args)
        return cmd

    def run(self, args: List[str], timeout: Optional[int] = 30) -> Tuple[int, str, str]:
        """Execute an arbitrary ADB command and return (returncode, stdout, stderr)."""
        full_cmd = self.build_command(args)
        try:
            process = subprocess.run(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return process.returncode, process.stdout.strip(), process.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds."
        except Exception as exc:
            return -1, "", str(exc)

    def shell(self, shell_cmd: str, timeout: Optional[int] = 30) -> Tuple[int, str, str]:
        """Execute a shell command inside the connected Android device."""
        return self.run(["shell", shell_cmd], timeout=timeout)

    def get_devices(self) -> List[Tuple[str, str]]:
        """Query and parse connected devices from `adb devices`."""
        code, out, _ = self.run(["devices"])
        if code != 0:
            return []

        devices = []
        for line in out.splitlines()[1:]:
            parts = line.strip().split()
            if len(parts) >= 2:
                devices.append((parts[0], parts[1]))
        return devices

    def pair(self, host_port: str, pairing_code: str) -> bool:
        """Pair with an Android 11+ device using Wireless Debugging pairing code.

        Example:
            host_port: '192.168.1.50:37123'
            pairing_code: '482910'
        """
        print(f"{Fore.CYAN}[*] Attempting Wireless ADB pairing to {host_port}...{Style.RESET_ALL}")
        code, out, err = self.run(["pair", host_port, pairing_code], timeout=20)
        output = f"{out}\n{err}".strip()
        if code == 0 and "successfully paired" in output.lower():
            print(f"{Fore.GREEN}[+] Pair successful: {output}{Style.RESET_ALL}")
            return True
        print(f"{Fore.RED}[!] Pairing failed: {output}{Style.RESET_ALL}")
        return False

    def connect(self, host_port: str) -> bool:
        """Connect to an Android device over Wireless ADB (`adb connect <host>:<port>`)."""
        print(f"{Fore.CYAN}[*] Connecting to {host_port}...{Style.RESET_ALL}")
        code, out, err = self.run(["connect", host_port], timeout=15)
        output = f"{out}\n{err}".strip()
        if code == 0 and "connected to" in output.lower():
            print(f"{Fore.GREEN}[+] Connected to {host_port}!{Style.RESET_ALL}")
            return True
        print(f"{Fore.YELLOW}[!] Connect response: {output}{Style.RESET_ALL}")
        return "connected" in output.lower()

    def get_brand(self) -> str:
        """Fetch device brand via `adb shell getprop ro.product.brand`."""
        code, out, _ = self.shell("getprop ro.product.brand")
        if code == 0 and out:
            return out.strip().lower()
        return "unknown"

    def get_model(self) -> str:
        """Fetch device model via `adb shell getprop ro.product.model`."""
        code, out, _ = self.shell("getprop ro.product.model")
        if code == 0 and out:
            return out.strip()
        return "Unknown Model"

    def get_serialno(self) -> str:
        """Fetch unique hardware serial or connection identifier."""
        code, out, _ = self.run(["get-serialno"])
        if code == 0 and out:
            return out.strip()
        return self.serial or "UNKNOWN_SERIAL"

    def wait_for_device(self, timeout_sec: int = 15) -> bool:
        """Wait until at least one device is recognized and authorized."""
        start = time.time()
        while time.time() - start < timeout_sec:
            devs = self.get_devices()
            authorized = [d for d in devs if d[1] == "device"]
            if authorized:
                if not self.serial:
                    self.serial = authorized[0][0]
                return True
            time.sleep(1)
        return False
