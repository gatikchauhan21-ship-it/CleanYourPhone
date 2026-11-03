"""Main CLI Interface for CleanYourPhone.

Provides interactive modular menus and scriptable command-line flags
for wireless pairing, device discovery, debloating, battery tuning,
fluid motion transitions, lock screen custom music visualizers,
modular refresh rate selection (60/90/120/Auto), Glass UI toggles,
and the 'Completely Restored' Flagship Theme suite.
"""

import argparse
from typing import Optional
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge
from src.device_detector import DeviceDetector
from src.backup_engine import BackupEngine
from src.bloat_manager import BloatManager
from src.battery_tuner import BatteryTuner
from src.hardware_tune import HardwareTuner
from src.optimizations import Optimizations
from src.theme_engine import ThemeEngine
from src.motion_engine import MotionEngine
from src.lockscreen_engine import LockScreenEngine
from src.rate_limiter import RateLimiter

init(autoreset=True)

ASCII_BANNER = rf"""{Fore.GREEN}
   ____ _                      __   __             ____  _                     
  / ___| | ___  __ _ _ __      \ \ / /__  _   _ _ _|  _ \| |__   ___  _ __   ___ 
 | |   | |/ _ \/ _` | '_ \ _____ \ V / _ \| | | | '__| |_) | '_ \ / _ \| '_ \ / _ \
 | |___| |  __/ (_| | | | |_____| | | (_) | |_| | |  |  __/| | | | (_) | | | |  __/
  \____|_|\___|\__,_|_| |_|       |_|\___/ \__,_|_|  |_|   |_| |_|\___/|_| |_|\___|{Style.RESET_ALL}
              {Fore.CYAN}Transform Budget Androids into Flagship Experiences{Style.RESET_ALL}
                    {Fore.YELLOW}Inspired by CleanYourTV • Non-Root & Safe{Style.RESET_ALL}
"""


def print_banner():
    """Print the CleanYourPhone ASCII banner."""
    print(ASCII_BANNER)


def print_menu():
    """Print the interactive modular options menu."""
    print(f"{Fore.CYAN}+-------------------------------------------------------------------------+{Style.RESET_ALL}")
    print(f"{Fore.CYAN}|                    FLAGSHIP TRANSFORMATION CONTROL SUITE                |{Style.RESET_ALL}")
    print(f"{Fore.CYAN}+-------------------------------------------------------------------------+{Style.RESET_ALL}")
    print(f"|  {Fore.GREEN}[1]{Style.RESET_ALL}  Auto-Detect Phone Model & Hardware Specs                         |")
    print(f"|  {Fore.GREEN}[2]{Style.RESET_ALL}  Wireless ADB Pairing & Connection Wizard                         |")
    print(f"|  {Fore.GREEN}[3]{Style.RESET_ALL}  {Fore.YELLOW}Inspect RAM & Hardware Overhead Matrix (What uses what RAM?){Style.RESET_ALL}    |")
    print(f"|  {Fore.GREEN}[4]{Style.RESET_ALL}  Safe OEM Debloat & System Ad-Block (Saves +350-750MB RAM)        |")
    print(f"|  {Fore.GREEN}[5]{Style.RESET_ALL}  Battery & Standby Maximizer (Deep Doze + Wi-Fi Sleep + Radio Cut)|")
    print(f"|  {Fore.GREEN}[6]{Style.RESET_ALL}  Fluid Motion & Touch Overclock (Predictive Back + 250ms)         |")
    print(f"|  {Fore.GREEN}[7]{Style.RESET_ALL}  Lock Screen Makeover (Glance Ad Purge + Live Music Waveform)     |")
    print(f"|  {Fore.GREEN}[8]{Style.RESET_ALL}  Modular Refresh Rate (Auto / 90Hz Sweet-Spot / 120Hz / 60Hz)     |")
    print(f"|  {Fore.GREEN}[9]{Style.RESET_ALL}  Glass UI Background Blurs (Modular: ON/OFF with budget warnings) |")
    print(f"|  {Fore.GREEN}[10]{Style.RESET_ALL} Completely Restored Flagship Theme (Pitch Black OLED + Slate)    |")
    print(f"|  {Fore.GREEN}[11]{Style.RESET_ALL} Hardware Tuning (NAND fstrim + Full AOT Speed Compile)          |")
    print(f"|  {Fore.GREEN}[12]{Style.RESET_ALL} [>>] 1-Click Ultimate Flagship Transformation (All-in-one)       |")
    print(f"|  {Fore.GREEN}[13]{Style.RESET_ALL} [<<] Revert All Changes (Execute restore_cleanyourphone)         |")
    print(f"|  {Fore.GREEN}[0]{Style.RESET_ALL}  Exit                                                             |")
    print(f"{Fore.CYAN}+-------------------------------------------------------------------------+{Style.RESET_ALL}")


def wizard_wireless(bridge: ADBBridge):
    """Interactive wizard for pairing and connecting Wireless ADB."""
    print(f"\n{Fore.CYAN}=== Wireless ADB Connection Wizard ==={Style.RESET_ALL}")
    print("1. Go to Settings > Developer Options > Wireless Debugging.")
    print("2. Tap 'Pair device with pairing code'.")
    print("3. Enter the IP address, Port, and 6-digit Code shown on screen.\n")

    host_port = input(f"{Fore.YELLOW}Enter Host:Port (e.g. 192.168.1.50:37123): {Style.RESET_ALL}").strip()
    code = input(f"{Fore.YELLOW}Enter 6-digit pairing code (or press Enter if already paired): {Style.RESET_ALL}").strip()

    if code:
        paired = bridge.pair(host_port, code)
        if not paired:
            print(f"{Fore.RED}[!] Pairing failed. Check Wi-Fi connection and re-try.{Style.RESET_ALL}")
            return

    connect_hp = input(f"{Fore.YELLOW}Enter Connect Host:Port (from Wireless Debugging main screen): {Style.RESET_ALL}").strip() or host_port
    bridge.connect(connect_hp)


def modular_refresh_rate_wizard(opts: Optimizations):
    """Modular menu allowing user to pick optimal refresh rate."""
    print(f"\n{Fore.CYAN}=== Modular Refresh Rate Controller ==={Style.RESET_ALL}")
    print("  [1] 90Hz Golden Sweet-Spot (Recommended for budget phones: Butter-smooth + Great Battery)")
    print("  [2] 120Hz Peak Smoothness (Maximum fluidity, slightly higher battery usage)")
    print("  [3] Dynamic Auto (OEM factory adaptive refresh rate)")
    print("  [4] 60Hz Eco-Saver (Maximum battery preservation)")
    c = input(f"{Fore.YELLOW}Choose refresh profile (1-4): {Style.RESET_ALL}").strip()
    if c == "1":
        opts.set_refresh_rate_profile("90")
    elif c == "2":
        opts.set_refresh_rate_profile("120")
    elif c == "3":
        opts.set_refresh_rate_profile("auto")
    elif c == "4":
        opts.set_refresh_rate_profile("60")


def modular_glass_ui_wizard(opts: Optimizations):
    """Modular menu allowing user to toggle Glass UI blurs."""
    print(f"\n{Fore.CYAN}=== Android Glass UI (Background Blur Shaders) Controller ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Technical Reality for Budget Phones:{Style.RESET_ALL}")
    print("  Glass UI requires continuous multi-pass GPU Gaussian calculations.")
    print("  On budget processors (e.g. Helio G99, Snapdragon 680, Unisoc), this consumes ~150MB VRAM")
    print("  and drops frame rates during notification shade pulls.")
    print("  Keeping blurs OFF yields maximum 120Hz/90Hz touch response.\n")
    print("  [1] Keep Glass UI Blurs OFF (Budget Performance Mode - Recommended)")
    print("  [2] Turn Glass UI Blurs ON (Luxury Aesthetics - Requires Capable GPU)")
    c = input(f"{Fore.YELLOW}Select mode (1 or 2): {Style.RESET_ALL}").strip()
    if c == "1":
        opts.set_glass_ui_blurs(enable=False)
    elif c == "2":
        opts.set_glass_ui_blurs(enable=True)


def run_full_transformation(bridge: ADBBridge):
    """Execute complete transformation with user choices for animations, refresh, and glass UI."""
    print(f"\n{Fore.MAGENTA}========================================================")
    print("      STARTING 1-CLICK ULTIMATE FLAGSHIP TRANSFORMATION")
    print(f"========================================================{Style.RESET_ALL}")

    # 1. Device Detection
    detector = DeviceDetector(bridge=bridge)
    detector.print_summary()

    # 2. Strict Backup First
    backup = BackupEngine(bridge=bridge)
    backup.create_full_backup()

    # 3. Rate Limiter check
    limiter = RateLimiter(bridge=bridge)
    allow_premium = limiter.enforce_premium_limit()

    # 4. Debloat & Ad-Block
    bloat = BloatManager(bridge=bridge)
    bloat.run_full_debloat_pipeline()

    # 5. Battery Tuner
    battery = BatteryTuner(bridge=bridge)
    battery.tune_all()

    # 6. Fluid Motion & Touch Overclock
    motion = MotionEngine(bridge=bridge)
    motion.run_full_motion_suite()

    # 7. Lock Screen Customization & Music Waveform
    lockscreen = LockScreenEngine(bridge=bridge)
    lockscreen.apply_full_lockscreen_makeover()

    # 8. Restored Flagship Theme
    theme = ThemeEngine(bridge=bridge)
    theme.apply_restored_flagship_preset()

    # 9. Liquid UI, Refresh Rate & Glass Options
    opts = Optimizations(bridge=bridge)
    if allow_premium:
        refresh_choice = input(f"\n{Fore.YELLOW}Select Refresh Rate: [1] 90Hz Sweet-Spot (Recommended), [2] 120Hz Peak, [3] Auto [1]: {Style.RESET_ALL}").strip()
        if refresh_choice == "2":
            opts.set_refresh_rate_profile("120")
        elif refresh_choice == "3":
            opts.set_refresh_rate_profile("auto")
        else:
            opts.set_refresh_rate_profile("90")

        want_glass = input(f"{Fore.YELLOW}Enable Glass UI Blurs? (Uses ~150MB VRAM. Recommended 'n' for budget phones) (y/n) [n]: {Style.RESET_ALL}").strip().lower() == "y"
        opts.set_glass_ui_blurs(enable=want_glass)
        opts.offload_surfaceflinger_gpu()
        opts.inject_micro_apk_torch()

    # 10. Hardware Tuning
    proceed_hw = input(f"\n{Fore.YELLOW}Run Ahead-Of-Time (AOT) app compilation now? Takes ~5 mins. (y/n) [y]: {Style.RESET_ALL}").strip().lower()
    if proceed_hw != "n":
        hardware = HardwareTuner(bridge=bridge)
        hardware.run_full_hardware_tune()

    print(f"\n{Fore.GREEN}========================================================")
    print("      [SUCCESS] ULTIMATE FLAGSHIP TRANSFORMATION COMPLETE! [SUCCESS]")
    print("      Your phone is now clean, responsive, ad-free, and musically styled.")
    print("      Rollback script saved to: restore_cleanyourphone.bat")
    print(f"========================================================{Style.RESET_ALL}\n")


def interactive_loop(bridge: ADBBridge):
    """Main interactive terminal loop."""
    print_banner()

    detector = DeviceDetector(bridge=bridge)
    backup = BackupEngine(bridge=bridge)
    bloat = BloatManager(bridge=bridge)
    battery = BatteryTuner(bridge=bridge)
    hardware = HardwareTuner(bridge=bridge)
    opts = Optimizations(bridge=bridge)
    theme = ThemeEngine(bridge=bridge)
    motion = MotionEngine(bridge=bridge)
    lockscreen = LockScreenEngine(bridge=bridge)
    limiter = RateLimiter(bridge=bridge)

    while True:
        print_menu()
        choice = input(f"{Fore.CYAN}Select an option (0-13): {Style.RESET_ALL}").strip()

        if choice == "0":
            print(f"\n{Fore.GREEN}Stay smooth! Exiting CleanYourPhone.{Style.RESET_ALL}")
            break
        elif choice == "1":
            detector.print_summary()
        elif choice == "2":
            wizard_wireless(bridge)
        elif choice == "3":
            opts.print_resource_overhead_matrix()
        elif choice == "4":
            bloat.run_full_debloat_pipeline()
        elif choice == "5":
            battery.tune_all()
        elif choice == "6":
            motion.run_full_motion_suite()
        elif choice == "7":
            lockscreen.apply_full_lockscreen_makeover()
        elif choice == "8":
            modular_refresh_rate_wizard(opts)
        elif choice == "9":
            modular_glass_ui_wizard(opts)
        elif choice == "10":
            theme.apply_restored_flagship_preset()
        elif choice == "11":
            hardware.run_full_hardware_tune()
        elif choice == "12":
            run_full_transformation(bridge)
        elif choice == "13":
            backup.execute_reversion()
        else:
            print(f"{Fore.RED}[!] Invalid choice. Please select from 0 to 13.{Style.RESET_ALL}")

        input(f"\n{Fore.LIGHTBLACK_EX}Press Enter to return to menu...{Style.RESET_ALL}")


def main():
    """Main entrypoint handling both CLI flags and interactive shell."""
    parser = argparse.ArgumentParser(
        description="CleanYourPhone - Zero-Root Flagship Android Optimizer via Wireless ADB"
    )
    parser.add_argument("-s", "--serial", help="Target ADB device serial or IP:Port", default=None)
    parser.add_argument("--detect", action="store_true", help="Auto-detect phone model and hardware specs")
    parser.add_argument("--specs", action="store_true", help="Display RAM and Hardware Overhead Analysis Matrix")
    parser.add_argument("--debloat", action="store_true", help="Run safe OEM debloat and AdGuard DNS injection")
    parser.add_argument("--battery", action="store_true", help="Apply Deep Doze and battery tuning")
    parser.add_argument("--motion", action="store_true", help="Apply fluid motion, predictive back, and touch overclock")
    parser.add_argument("--lockscreen", action="store_true", help="Apply lockscreen adware purge, music waveform, and iOS clock")
    parser.add_argument("--refresh", choices=["60", "90", "120", "auto"], help="Set modular display refresh rate profile")
    parser.add_argument("--glass-on", action="store_true", help="Enable Glass UI background blur shaders")
    parser.add_argument("--glass-off", action="store_true", help="Disable Glass UI blurs for budget performance")
    parser.add_argument("--theme", action="store_true", help="Apply Completely Restored Flagship Theme (OLED Black + Slate)")
    parser.add_argument("--hardware", action="store_true", help="Run fstrim and full AOT compilation")
    parser.add_argument("--all", action="store_true", help="Run complete 1-click flagship transformation")
    parser.add_argument("--revert", action="store_true", help="Revert device back to stock factory settings")

    args = parser.parse_args()
    bridge = ADBBridge(serial=args.serial)

    has_flags = any([
        args.detect, args.specs, args.debloat, args.battery,
        args.motion, args.lockscreen, args.refresh,
        args.glass_on, args.glass_off, args.theme,
        args.hardware, args.all, args.revert
    ])

    if not has_flags:
        interactive_loop(bridge)
        return

    opts = Optimizations(bridge)

    if args.detect:
        DeviceDetector(bridge).print_summary()
    if args.specs:
        opts.print_resource_overhead_matrix()
    if args.revert:
        BackupEngine(bridge).execute_reversion()
    if args.debloat:
        BloatManager(bridge).run_full_debloat_pipeline()
    if args.battery:
        BatteryTuner(bridge).tune_all()
    if args.motion:
        MotionEngine(bridge).run_full_motion_suite()
    if args.lockscreen:
        LockScreenEngine(bridge).apply_full_lockscreen_makeover()
    if args.refresh:
        opts.set_refresh_rate_profile(args.refresh)
    if args.glass_on:
        opts.set_glass_ui_blurs(enable=True)
    if args.glass_off:
        opts.set_glass_ui_blurs(enable=False)
    if args.theme:
        ThemeEngine(bridge).apply_restored_flagship_preset()
    if args.hardware:
        HardwareTuner(bridge).run_full_hardware_tune()
    if args.all:
        run_full_transformation(bridge)


if __name__ == "__main__":
    main()
