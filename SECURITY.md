# Security Policy

## 🔒 Safety Philosophy: Non-Destructive & Backup-First

CleanYourPhone is designed with a **fail-safe, non-destructive architecture**. While system tweaking tools historically carried bootloop or bricking risks, CleanYourPhone eliminates these hazards by adhering to strict engineering boundaries:

### 1. No Root Required
All operations are executed within the boundaries of Android Debug Bridge (ADB) user-space permissions (`android.permission.WRITE_SECURE_SETTINGS`, `DEVICE_CONFIG`, and standard package manager user disabling). No `/system`, `/vendor`, or boot partitions are mounted as read-write.

### 2. Mandatory Pre-Execution Snapshot (`restore_cleanyourphone.bat`)
Before any optimization, debloat, or battery parameter is applied:
- The device's original animation scalars, Doze thresholds, DNS settings, and package statuses are queried via `adb shell settings get ...`.
- An inverse rollback batch script (`restore_cleanyourphone.bat`) and shell script (`restore_cleanyourphone.sh`) are generated locally on the host machine.
- If anything looks abnormal, running this script returns the phone to its initial stock state immediately.

### 3. Safe Package Disabling
Rather than deleting APK files via `pm uninstall`, CleanYourPhone solely leverages:
```bash
adb shell pm disable-user --user 0 <package_name>
```
This freezes the app package for User 0 (stopping CPU usage, RAM consumption, and telemetry), while leaving the underlying APK unharmed in read-only system partitions. The app can be instantly revived with `pm enable <package_name>`.

---

## 🛡️ Reporting a Vulnerability

If you discover a security flaw or a package modification that could lead to unexpected device lockups, please report it responsibly:

1. **Email**: Open an issue flagged as `[SECURITY]` or reach out to security maintainers at `security@cleanyourphone.dev`.
2. **Details**: Provide device manufacturer (`ro.product.brand`), Android OS version (`ro.build.version.release`), and the specific ADB command that exhibited unsafe behavior.
3. **Response Time**: We aim to acknowledge reports within 48 hours and patch bloat lists within 5 business days.
