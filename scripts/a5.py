"""
Convert any Fox at Walton A5 menu HTML to a print-ready PDF.

Usage:
    python3 convert_a5.py <input.html>           # outputs <input>.pdf
    python3 convert_a5.py <input.html> <out.pdf> # outputs to specified path

Key settings:
- Exact page size: 148mm x 210mm (A5)
- No margins (HTML has its own padding built in)
- Print background graphics enabled (cream page colour)
- Waits for Google Fonts to load before capturing
- Strips blank trailing pages
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter


def is_blank_page(page):
    text = page.extract_text().strip()
    if text:
        return False
    resources = page.get("/Resources") or {}
    xobjects = resources.get("/XObject") or {}
    return len(xobjects) == 0


def html_to_pdf(html_path, pdf_path):
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path)
    temp_path = pdf_path.with_suffix(".temp.pdf")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto(f"file://{html_path}")
        page.evaluate("document.fonts.ready")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        page.pdf(
            path=str(temp_path),
            width="148mm",
            height="210mm",
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            print_background=True,
            prefer_css_page_size=False,
        )

        browser.close()

    reader = PdfReader(str(temp_path))
    writer = PdfWriter()
    kept = 0
    for i, pg in enumerate(reader.pages):
        if is_blank_page(pg):
            print(f"  - Skipping blank page {i + 1}")
            continue
        writer.add_page(pg)
        kept += 1

    with open(pdf_path, "wb") as f:
        writer.write(f)

    temp_path.unlink()

    size_kb = pdf_path.stat().st_size / 1024
    print(f"PDF created: {pdf_path}")
    print(f"Pages: {kept}")
    print(f"Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 convert_a5.py <input.html> [output.pdf]")
        sys.exit(1)

    html_path = Path(sys.argv[1])
    pdf_path = Path(sys.argv[2]) if len(sys.argv) > 2 else html_path.with_suffix(".pdf")
    html_to_pdf(html_path, pdf_path)
