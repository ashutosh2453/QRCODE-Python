# 🧩 QR Code Generator

A simple and efficient **Python-based QR Code Generator** that allows users to create QR codes from text or URLs.  
Built using the `qrcode` and `pillow` libraries, this tool lets you generate clean, high-quality QR codes in seconds.

---

## 🚀 Features

- Generate QR codes for **URLs**, **text**, or any custom input
- Generate **UPI payment QR codes** that work in every UPI app (Google Pay, PhonePe, Paytm, BHIM…)
- Optional fixed **amount** and **note** for payment requests
- Validation of UPI IDs and amounts, with clear error messages
- Customizable **size**, **border**, **error-correction level** and **colours**
- Output as PNG (or JPG/BMP)
- Tested with `pytest` and checked in CI on Python 3.10–3.13

---

## 🛠️ Installation

Make sure you have **Python 3.10+** installed.
Then, install the dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Usage

### Text or URL

```bash
python qr_generator.py text "https://github.com/ashutosh2453" -o github.png
python qr_generator.py text "Hello!" --box-size 6 --border 2 --error-correction H --fill navy
```

### UPI payment

```bash
python qr_generator.py upi --vpa yourname@okhdfcbank --name "Your Name" -o pay.png
python qr_generator.py upi --vpa yourname@okhdfcbank --name "Your Name" --amount 250 --note "Dinner" -o pay.png
```

This produces a standard `upi://pay` link, for example
`upi://pay?pa=yourname@okhdfcbank&pn=Your%20Name&am=250.00&cu=INR&tn=Dinner`.
A single UPI QR code works in every UPI app, so you don't need a separate code per app.

### Interactive mode

```bash
python money.py
```

### Options

| Option | Default | Description |
|---|---|---|
| `-o, --output` | `qr.png` | Output image path |
| `--box-size` | `10` | Pixels per QR module (1–50) |
| `--border` | `4` | Quiet-zone width in modules (0–20) |
| `--error-correction` | `M` | `L` (7%), `M` (15%), `Q` (25%), `H` (30%) |
| `--fill` / `--background` | `black` / `white` | Colours |
| `--show` | off | Open the image after saving |

## ✅ Tests

```bash
pip install pytest
pytest -q
```

## 📝 Changelog

- **2026-11-15**
  - Fixed UPI links. They used a hard-coded merchant code (`mc=1234`), which can get payments to personal UPI IDs declined; they now follow the standard P2P fields (`pa`, `pn`, `am`, `cu`, `tn`) with proper URL encoding.
  - Replaced the three identical per-app QR codes with one universal code, and fixed the `gppgle_pay_qr.png` filename typo.
  - Added UPI ID and amount validation, the text/URL mode, size/border/colour options, a CLI, tests and CI.
  - Removed a committed `.pyc` file.
