"""QR code generator for text/URLs and spec-compliant UPI payment links.

Usage examples:
    python qr_generator.py text "https://github.com/ashutosh2453" -o github.png
    python qr_generator.py upi --vpa name@okhdfcbank --name "Asha Kumar" --amount 250 --note "Dinner" -o pay.png
"""

from __future__ import annotations

import argparse
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote

import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q

# UPI virtual payment address: handle@psp (NPCI allows letters, digits, '.', '-', '_').
VPA_RE = re.compile(r"^[A-Za-z0-9._-]{2,256}@[A-Za-z][A-Za-z0-9]{1,63}$")
MAX_UPI_AMOUNT = Decimal("100000")  # standard per-transaction UPI P2P limit (INR)
ERROR_LEVELS = {"L": ERROR_CORRECT_L, "M": ERROR_CORRECT_M, "Q": ERROR_CORRECT_Q, "H": ERROR_CORRECT_H}


class QRInputError(ValueError):
    """Raised for invalid user input (bad UPI ID, amount, sizes...)."""


def validate_vpa(vpa: str) -> str:
    vpa = vpa.strip()
    if not VPA_RE.fullmatch(vpa):
        raise QRInputError(f"'{vpa}' is not a valid UPI ID (expected something like name@okhdfcbank)")
    return vpa


def normalise_amount(amount: str | float | Decimal | None) -> str | None:
    if amount is None or str(amount).strip() == "":
        return None
    try:
        value = Decimal(str(amount).strip())
    except InvalidOperation:
        raise QRInputError(f"amount '{amount}' is not a number") from None
    if not value.is_finite() or value <= 0:
        raise QRInputError("amount must be greater than 0")
    if value > MAX_UPI_AMOUNT:
        raise QRInputError(f"amount exceeds the UPI limit of {MAX_UPI_AMOUNT} INR")
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def build_upi_uri(vpa: str, name: str, amount: str | float | None = None, note: str | None = None) -> str:
    """Build a ``upi://pay`` deep link understood by every UPI app (GPay, PhonePe, Paytm, BHIM...).

    Only personal (P2P) fields are emitted. The previous implementation sent a
    hard-coded merchant code (``mc=1234``), which marks the payee as a merchant
    and can cause payments to personal UPI IDs to be declined.
    """
    name = name.strip()
    if not name:
        raise QRInputError("payee name must not be empty")
    params = [("pa", validate_vpa(vpa)), ("pn", name)]
    amt = normalise_amount(amount)
    if amt:
        params.append(("am", amt))
    params.append(("cu", "INR"))
    if note and note.strip():
        params.append(("tn", note.strip()[:80]))
    return "upi://pay?" + "&".join(f"{k}={quote(v, safe='@.-_')}" for k, v in params)


def make_qr(data: str, box_size: int = 10, border: int = 4, error_correction: str = "M",
            fill_color: str = "black", back_color: str = "white"):
    if not data:
        raise QRInputError("nothing to encode")
    if not 1 <= box_size <= 50:
        raise QRInputError("box size must be between 1 and 50")
    if not 0 <= border <= 20:
        raise QRInputError("border must be between 0 and 20")
    level = ERROR_LEVELS.get(error_correction.upper())
    if level is None:
        raise QRInputError("error correction must be one of L, M, Q, H")
    qr = qrcode.QRCode(error_correction=level, box_size=box_size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color=fill_color, back_color=back_color)


def save_qr(data: str, output: str | Path, **options) -> Path:
    path = Path(output)
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp"}:
        path = path.with_suffix(".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    make_qr(data, **options).save(path)
    return path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate QR codes for text, URLs or UPI payments.")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("-o", "--output", default="qr.png", help="output image path (default: qr.png)")
    common.add_argument("--box-size", type=int, default=10, help="pixels per QR module (1-50)")
    common.add_argument("--border", type=int, default=4, help="quiet-zone width in modules (0-20)")
    common.add_argument("--error-correction", default="M", choices=list(ERROR_LEVELS), help="L, M, Q or H")
    common.add_argument("--fill", default="black", help="foreground colour")
    common.add_argument("--background", default="white", help="background colour")
    common.add_argument("--show", action="store_true", help="open the image after saving")

    sub = parser.add_subparsers(dest="mode", required=True)
    p_text = sub.add_parser("text", parents=[common], help="encode any text or URL")
    p_text.add_argument("data")
    p_upi = sub.add_parser("upi", parents=[common], help="encode a UPI payment request")
    p_upi.add_argument("--vpa", required=True, help="payee UPI ID, e.g. name@okhdfcbank")
    p_upi.add_argument("--name", required=True, help="payee name shown in the payer's app")
    p_upi.add_argument("--amount", help="optional fixed amount in INR")
    p_upi.add_argument("--note", help="optional transaction note")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        data = args.data if args.mode == "text" else build_upi_uri(args.vpa, args.name, args.amount, args.note)
        path = save_qr(data, args.output, box_size=args.box_size, border=args.border,
                       error_correction=args.error_correction, fill_color=args.fill, back_color=args.background)
    except (QRInputError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Saved QR code to {path}")
    if args.mode == "upi":
        print(f"Encoded: {data}")
    if args.show:
        from PIL import Image
        Image.open(path).show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
