"""Rate Limiter & Premium Access Control for CleanYourPhone.

Enforces a daily usage limit (Max 2 runs/day per device serial number)
for premium Liquid UI & theme optimizations via a Supabase REST API backend.
"""

from datetime import datetime
from typing import Optional, Tuple
import requests
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge

init(autoreset=True)

# Supabase REST API Configuration Placeholders
SUPABASE_URL = "https://xyzcompany.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.PLACEHOLDER_KEY"
SUPABASE_TABLE = "device_usage"
PAYMENT_LINK = "https://github.com/sponsors/cleanyourphone"


class RateLimiter:
    """Manages daily quota checks per device hardware serial."""

    def __init__(self, bridge: Optional[ADBBridge] = None):
        """Initialize RateLimiter with ADBBridge."""
        self.bridge = bridge or ADBBridge()

    def get_device_serial(self) -> str:
        """Fetch unique hardware serial number."""
        return self.bridge.get_serialno()

    def check_limit(self, serial: Optional[str] = None) -> Tuple[bool, int]:
        """Check if device has exceeded 2 daily runs.

        Returns:
            (is_allowed: bool, current_usage: int)
        """
        device_serial = serial or self.get_device_serial()
        today = datetime.now().strftime("%Y-%m-%d")

        # If placeholders are unconfigured, run in local demo mode with safe pass-through
        if "xyzcompany" in SUPABASE_URL or "PLACEHOLDER" in SUPABASE_ANON_KEY:
            # Fallback to local permissive check for offline / open-source contributors
            return True, 1

        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        query_url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}?serial=eq.{device_serial}&usage_date=eq.{today}"

        try:
            resp = requests.get(query_url, headers=headers, timeout=5)
            if resp.status_code == 200:
                records = resp.json()
                if records:
                    count = records[0].get("usage_count", 0)
                    if count >= 2:
                        return False, count
                    return True, count
                return True, 0
            else:
                # Network or table issue; fallback gracefully
                return True, 0
        except Exception:
            # Fail open for connectivity resilience
            return True, 0

    def increment_usage(self, serial: Optional[str] = None, current_count: int = 0) -> None:
        """Increment daily usage counter in Supabase database."""
        device_serial = serial or self.get_device_serial()
        today = datetime.now().strftime("%Y-%m-%d")

        if "xyzcompany" in SUPABASE_URL or "PLACEHOLDER" in SUPABASE_ANON_KEY:
            return

        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        }

        payload = {
            "serial": device_serial,
            "usage_date": today,
            "usage_count": current_count + 1,
            "last_used_at": datetime.now().isoformat(),
        }

        try:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}",
                headers=headers,
                json=payload,
                timeout=5,
            )
        except Exception:
            pass

    def enforce_premium_limit(self) -> bool:
        """Enforce quota check.

        If allowed, records usage and returns True.
        If blocked, displays payment unlock message and returns False.
        """
        serial = self.get_device_serial()
        allowed, count = self.check_limit(serial)

        if not allowed:
            print(f"\n{Fore.RED}Daily limit reached. To unlock unlimited features, support the project here: {PAYMENT_LINK}{Style.RESET_ALL}\n")
            return False

        self.increment_usage(serial, count)
        return True
