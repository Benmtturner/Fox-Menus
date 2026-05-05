## menus/ — your 7 production menus

| File | Page Size | Type |
|---|---|---|
| `Menu-SRA4.html/.pdf` | SRA4 (225×320mm) | À la carte (main) |
| `A-La-Carte-menu-sra4.html/.pdf` | SRA4 (225×320mm) | À la carte (May 6th) |
| `Sunday-Menu-A4.html/.pdf` | A4 (210×297mm) | Sunday menu (roasts) |
| `Bar-Menu-A5.html/.pdf` | A5 (148×210mm) | Bar menu |
| `Lunch-Specials-A5.html/.pdf` | A5 | Lunch specials |
| `Supper-Club-A5.html/.pdf` | A5 | Fixed-price set menu |
| `Daily-Specials-A5.html/.pdf` | A5 | Daily specials |
| `Dessert-Menu-A5.html/.pdf` | A5 | Desserts |

To edit: open the `.html` file in any text editor or VS Code. Find the `MENU` object near the top — that's where all the dish data lives. Change names, prices, descriptions, add/remove dishes. Then run the matching converter script to regenerate the PDF.

## scripts/ — turn HTML into PDF

Three converter scripts — one per page size — plus the migration tool.

### Setup (one time per machine)

## Requirements

- **Python 3.8+** — for running the PDF conversion scripts
- **Playwright** — headless browser engine for HTML-to-PDF rendering
- **Chromium** — browser component used by Playwright
- **pypdf** — PDF manipulation library (removes blank pages)

---

## Linux (Debian/Ubuntu/Arch)

### Debian/Ubuntu

```bash
# Update package lists
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip -y

# Install Playwright and pypdf
pip3 install playwright pypdf --break-system-packages

# Install Chromium for Playwright
python3 -m playwright install chromium

# Install Chromium dependencies (if needed)
python3 -m playwright install-deps chromium
```

### Arch Linux

```bash
# Install Python and pip (usually pre-installed)
sudo pacman -S python python-pip

# Install Playwright and pypdf
pip install playwright pypdf

# Install Chromium for Playwright
python -m playwright install chromium

# Install Chromium dependencies (if needed)
python -m playwright install-deps chromium
```

---

## macOS

### Using Homebrew (recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3 (macOS usually has it, but Homebrew version is Better)
brew install python3

# Install Playwright and pypdf
pip3 install playwright pypdf

# Install Chromium for Playwright
python3 -m playwright install chromium
```

### Alternative: Using system Python

```bash
# Check Python version (must be 3.8+)
python3 --version

# Install Playwright and pypdf
pip3 install --user playwright pypdf

# Install Chromium for Playwright
python3 -m playwright install chromium
```

---

## Windows

### Using PowerShell (recommended)

```powershell
# Check if Python is installed
python --version

# If Python is not installed, download and install from python.org:
# https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Install Playwright and pypdf
pip install playwright pypdf

# Install Chromium for Playwright
python -m playwright install chromium
```

### Using Chocolatey (alternative package manager)

```powershell
# Install Chocolatey if not already installed (run as Administrator)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python
choco install python -y

# Refresh environment variables
refreshenv

# Install Playwright and pypdf
pip install playwright pypdf

# Install Chromium for Playwright
python -m playwright install chromium
```

### Manual Python Installation (if needed)

1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Open PowerShell or Command Prompt
5. Verify installation: `python --version`
6. Install packages:
   ```
   pip install playwright pypdf
   python -m playwright install chromium
   ```

---

## Verification

After installation, verify everything is working:

```bash
# Check Python version
python3 --version  # Linux/macOS
python --version   # Windows

# Check pip is installed
pip3 --version     # Linux/macOS
pip --version      # Windows

# Check Playwright installation
python3 -m playwright --version  # Linux/macOS
python -m playwright --version   # Windows
```

## Test the Scripts

Generate a test PDF to confirm everything works:

```bash
# Linux/macOS
python3 scripts/a5.py menus/Bar-Menu-A5.html

# Windows
python scripts\a5.py menus\Bar-Menu-A5.html
```

If successful, you should see:
```
PDF created: menus/Bar-Menu-A5.pdf
Pages: 1
Size: XX.X KB
```

---

## Troubleshooting

### "command not found: python3" (macOS/Linux)
Try `python` instead of `python3`, or install Python using your package manager.

### "python is not recognized" (Windows)
Python is not in your PATH. Reinstall Python and check "Add Python to PATH", or add it manually to environment variables.

### Playwright Chromium fails to launch
Run the dependency installer:
```bash
# Linux/macOS
python3 -m playwright install-deps chromium

# Windows (usually not needed)
python -m playwright install-deps chromium
```

### Permission denied when installing packages (Linux/macOS)
Use `--user` flag or `--break-system-packages` for system Python:
```bash
pip3 install --user playwright pypdf
# or
pip3 install playwright pypdf --break-system-packages
```

### Import errors when running scripts
Make sure you're using the same Python version for installation and running:
```bash
# If installed with pip3, use python3 to run
python3 scripts/a5.py menus/Bar-Menu-A5.html
```

---


### Usage

```bash
# À la carte (SRA4):
python3 scripts/sra4.py menus/Menu-SRA4.html
python3 scripts/sra4.py menus/A-La-Carte-menu-sra4.html

# Sunday menu (A4):
python3 scripts/a4.py menus/Sunday-Menu-A4.html

# Any A5 menu:
python3 scripts/a5.py menus/Bar-Menu-A5.html
python3 scripts/a5.py menus/Lunch-Specials-A5.html
python3 scripts/a5.py menus/Supper-Club-A5.html
python3 scripts/a5.py menus/Daily-Specials-A5.html
python3 scripts/a5.py menus/Dessert-Menu-A5.html
```

Each script outputs a PDF with the same name as the input HTML (e.g. `Menu-SRA4.html` → `Menu-SRA4.pdf`). 

### Printing tips

- **Paper size:** match the menu (custom for SRA4, A4 / A5 from dropdown otherwise)
- **Scale:** 100% / "Actual size" — never "Fit to page"
- **Margins:** None (the design includes its own padding)


**Common edits:**

| To do this | Edit this |
|---|---|
| Change a dish price | The `price: "10"` value (no £ sign, just the number) |
| Add a dietary note | Add `note: "Plant based option available"` to the dish |
| Change seasonal subtitle | `header.subtitle` |
| Add a new dish | Add a new `{ name, price, desc }` line in the array |
| Remove a dish | Delete the whole `{ ... },` line |
| Reorder dishes | Cut and paste lines into new order |

After editing, save the file and run the matching `convert_*.py` script.

## Design notes

- **Font:** Cormorant Garamond + Cormorant SC, loaded from Google Fonts at PDF generation time
- **Colours:**
  - Rust: `#8B3A1F` (accents, prices)
  - Forest: `#2D4A2B` (subtitle, contact)
  - Charcoal: `#1A1A1A` (dish names)
  - Grey: `#5A5A5A` (descriptions)
- **Logo** is embedded as base64 inside each HTML file — no external image dependencies
