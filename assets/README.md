# Assets Directory

This folder holds companion micro-APKs and resources that can optionally be injected or installed via CleanYourPhone.

## Micro-APKs

1. **`variable_torch.apk`**
   - A lightweight micro-service enabling granular, multi-level flashlight brightness controls (similar to iOS / Samsung OneUI flagship torch sliders) for stock or budget Android builds.
   - CleanYourPhone can silently install or push this APK over ADB and register its quick-settings toggle tile into `sysui_qs_tiles`.

2. **`dynamic_music.apk`**
   - A minimalist, zero-telemetry background media visualizer and controller tile.

Users can drop custom micro-APKs into this folder to automate quick-settings tile additions or background service provisioning.
