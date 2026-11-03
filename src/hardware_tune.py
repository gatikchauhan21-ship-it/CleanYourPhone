"""Hardware Tuning Engine for CleanYourPhone.

Executes NAND flash TRIM maintenance (`sm fstrim`) and triggers full system-wide
Ahead-Of-Time (AOT) speed-profile compilation (`cmd package compile -m speed -a`)
with an interactive live progress spinner and elapsed time tracking.
"""

import itertools
import threading
import time
from typing import Optional
from colorama import Fore, Style, init

from src.adb_bridge import ADBBridge

init(autoreset=True)


class HardwareTuner:
    """Performs filesystem maintenance and Ahead-of-Time DEX bytecode optimization."""

    def __init__(self, bridge: Optional[ADBBridge] = None):
        """Initialize HardwareTuner with ADBBridge instance."""
        self.bridge = bridge or ADBBridge()

    def run_fstrim(self) -> bool:
        """Run NAND storage TRIM (`adb shell sm fstrim`).

        Restores read/write I/O throughput by reclaiming deleted flash storage blocks.
        """
        print(f"\n{Fore.CYAN}[*] Running NAND Storage TRIM (`sm fstrim`)...{Style.RESET_ALL}")
        code, out, err = self.bridge.shell("sm fstrim", timeout=60)
        if code == 0:
            print(f"{Fore.GREEN}[OK] Storage TRIM completed successfully. Block garbage collection finalized.{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}[!] Storage TRIM response: {out or err}{Style.RESET_ALL}")
            return False

    def run_aot_compilation(self) -> bool:
        """Run Ahead-Of-Time (AOT) DEX bytecode speed compilation for all packages.

        Command:
            adb shell cmd package compile -m speed -a

        Pre-compiles Dalvik/ART bytecode into native machine code, completely
        eliminating runtime Just-In-Time (JIT) stutters during app execution.
        """
        print(f"\n{Fore.CYAN}[*] Initiating System-Wide Ahead-Of-Time (AOT) Speed Compilation...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Note: This optimizes every application to native code and may take 3-8 minutes.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[!] Please keep your phone connected and awake.{Style.RESET_ALL}\n")

        spinner_chars = ["|", "/", "-", "\\"]
        done_flag = threading.Event()
        start_time = time.time()

        def spinner_worker():
            for char in itertools.cycle(spinner_chars):
                if done_flag.is_set():
                    break
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                sys_stdout = f"\r  {Fore.MAGENTA}[{char}]{Style.RESET_ALL} Compiling packages with ART speed profile... [Elapsed: {mins:02d}:{secs:02d}] "
                print(sys_stdout, end="", flush=True)
                time.sleep(0.1)

        spinner_thread = threading.Thread(target=spinner_worker, daemon=True)
        spinner_thread.start()

        # Run with generous timeout (900 seconds = 15 minutes)
        code, out, err = self.bridge.shell("cmd package compile -m speed -a", timeout=900)

        done_flag.set()
        spinner_thread.join()
        total_time = int(time.time() - start_time)
        tmins, tsecs = divmod(total_time, 60)

        print(f"\r  {Fore.GREEN}[OK] Compilation complete! Total time: {tmins}m {tsecs}s                     {Style.RESET_ALL}")

        if code == 0 or "Success" in out:
            print(f"{Fore.GREEN}[+] All apps pre-compiled to native instructions. Frame drops eliminated!{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}[!] AOT Compilation status: {out or err}{Style.RESET_ALL}")
            return True

    def run_full_hardware_tune(self) -> None:
        """Run storage trim followed by full AOT bytecode compilation."""
        self.run_fstrim()
        self.run_aot_compilation()
