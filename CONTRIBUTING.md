# Contributing to CleanYourPhone

Thank you for your interest in contributing to **CleanYourPhone**! We are building an open-source, safe, community-driven optimizer that transforms budget Android phones into clean, flagship-grade devices.

## 🤝 Code of Conduct
We are committed to providing a friendly, safe, and welcoming environment for all contributors. Please be respectful and constructive in all discussions, pull requests, and issue reports.

---

## 🧭 Core Principles & Constraints

When proposing changes or opening Pull Requests, keep these rules in mind:

1. **Safety & Non-Destructive Operations**:
   - Never use permanent uninstall commands (e.g. `pm uninstall -k --user 0`) unless accompanied by an explicit warning and a backup plan. Always prefer `pm disable-user --user 0`.
   - Never remove essential system components like emergency dialers, telephony packages, keyboards, or package installers.
2. **Strict Backup-First Policy**:
   - Any new setting or tweak introduced must have a corresponding restore routine recorded in `src/backup_engine.py` to keep `restore_cleanyourphone.bat` up to date.
3. **No Closed-Source Bloatware**:
   - We do not bundle proprietary or closed binaries. Any companion micro-tools must be open-source and dropped optionally into `/assets/`.
4. **Clean Code & Typing**:
   - Use Python 3.8+ idioms, type annotations, and descriptive docstrings.

---

## 🛠️ Development Setup

```bash
# Fork & clone the repo
git clone https://github.com/your-username/CleanYourPhone.git
cd CleanYourPhone

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run test suite
python -m unittest discover tests
```

---

## 📋 Adding New Bloatware Lists

If you would like to submit a new OEM or refine an existing list:
1. Locate or create `lists/bloat_<oem>.json`.
2. Format the file consistently:
   ```json
   {
     "oem": "ManufacturerName",
     "packages": [
       "com.example.telemetry",
       "com.example.adservice"
     ]
   }
   ```
3. Test disabling and re-enabling on a physical device or emulator before opening a PR.

---

## 🚀 Submitting a Pull Request

1. Create a feature branch: `git checkout -b feature/awesome-optimization`
2. Commit your changes: `git commit -m "feat: add support for Nothing Phone telemetry disable"`
3. Push to your fork: `git push origin feature/awesome-optimization`
4. Open a Pull Request on GitHub with a clear explanation of testing performed.
