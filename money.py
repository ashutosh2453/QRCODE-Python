"""Interactive UPI QR generator (kept for backwards compatibility).

A UPI QR code is app-agnostic: the same code works in Google Pay, PhonePe,
Paytm, BHIM and every other UPI app, so only one image is generated.
For scripting, use ``python qr_generator.py upi --help``.
"""

import sys

from qr_generator import QRInputError, build_upi_uri, save_qr


def main() -> int:
    try:
        vpa = input("Enter your UPI ID (e.g. name@okhdfcbank): ")
        name = input("Enter the payee name: ")
        amount = input("Amount in INR (leave blank to let the payer choose): ")
        note = input("Note (optional): ")
        uri = build_upi_uri(vpa, name, amount or None, note or None)
        path = save_qr(uri, "upi_qr.png")
    except QRInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Saved {path} - scan it with any UPI app.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
