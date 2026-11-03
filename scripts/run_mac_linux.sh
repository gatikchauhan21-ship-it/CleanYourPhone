#!/usr/bin/env bash
# ========================================================
#         CleanYourPhone - macOS / Linux Launcher
# ========================================================

set -e

echo "========================================================"
echo "         CleanYourPhone - Linux/macOS Launcher"
echo "========================================================"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.8+."
    exit 1
fi

# Check for ADB
if ! command -v adb &> /dev/null; then
    echo "[WARNING] 'adb' command not found in PATH."
    echo "Please install Android platform-tools via homebrew or apt."
    echo ""
fi

# Check dependencies
python3 -c "import colorama, requests" 2>/dev/null || {
    echo "[INFO] Installing required dependencies..."
    pip3 install -r requirements.txt
}

echo "[INFO] Starting CleanYourPhone CLI..."
python3 -m src.cli
