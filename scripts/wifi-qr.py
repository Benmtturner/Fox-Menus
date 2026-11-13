"""
Generate a self-contained WiFi-join QR code as inline SVG.

Scanning the code offers to join the network automatically (no typing the
password). The SVG has no external references, so it can be pasted straight
into a menu HTML file and will render in the CI PDF build and on the website
under its strict CSP — the same "bake the asset in" approach used for the
fox logo and horse watermark.

Usage:
    python3 scripts/wifi-qr.py "The Fox WIFI" "Food&Drink" [--auth WPA] [--scale 10]

Prints the <svg> markup to stdout. Requires: pip install segno

The WiFi URI scheme escapes \\ ; , : and " with a backslash. Spaces and &
are literal, so "The Fox WIFI" and "Food&Drink" need no escaping.
"""

import argparse
import sys

try:
    import segno
except ImportError:
    sys.exit("segno is required: pip install segno")

SPECIAL = set('\\;,:"')


def escape(value: str) -> str:
    """Backslash-escape the characters reserved by the WIFI: URI scheme."""
    return "".join("\\" + ch if ch in SPECIAL else ch for ch in value)


def wifi_payload(ssid: str, password: str, auth: str = "WPA", hidden: bool = False) -> str:
    return (
        f"WIFI:T:{auth};S:{escape(ssid)};P:{escape(password)};"
        f"{'H:true;' if hidden else ''};"
    )


def build_svg(ssid: str, password: str, auth: str, scale: int, border: int) -> str:
    payload = wifi_payload(ssid, password, auth)
    # error correction Q (25%) survives print smudging on a paper menu
    qr = segno.make(payload, error="q")
    import io

    buf = io.BytesIO()
    qr.save(
        buf,
        kind="svg",
        scale=scale,
        border=border,
        dark="#1A1A1A",      # charcoal to match the menu ink, still high-contrast
        light=None,          # transparent — the HTML places it on a white card
        xmldecl=False,
        svgns=True,
        omitsize=True,       # drop width/height so CSS can size it
    )
    return buf.getvalue().decode("utf-8").strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="WiFi-join QR code as inline SVG")
    ap.add_argument("ssid", help="network name, e.g. 'The Fox WIFI'")
    ap.add_argument("password", help="network password")
    ap.add_argument("--auth", default="WPA", choices=["WPA", "WEP", "nopass"],
                    help="security type (default WPA, covers WPA/WPA2/WPA3)")
    ap.add_argument("--scale", type=int, default=10, help="module size in SVG units")
    ap.add_argument("--border", type=int, default=2, help="quiet-zone width in modules")
    args = ap.parse_args()

    sys.stdout.write(build_svg(args.ssid, args.password, args.auth, args.scale, args.border))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
