#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.55,<2.0"]
# ///
"""Fail if any built page overflows horizontally at 360px or 390px.

Usage: python scripts/check_overflow.py [base_url]
Serve dist/ first (e.g. `python -m http.server 8899 --directory dist`).
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8899"
DIST = Path(__file__).resolve().parents[1] / "dist"

# Map every built index.html to its clean URL path.
paths = []
for p in sorted(DIST.rglob("index.html")):
    rel = p.parent.relative_to(DIST).as_posix()
    paths.append("/" if rel == "." else f"/{rel}/")

WIDTHS = [360, 390]
bad = []

with sync_playwright() as pw:
    browser = pw.webkit.launch()
    for w in WIDTHS:
        page = browser.new_page(viewport={"width": w, "height": 844})
        for path in paths:
            page.goto(BASE + path, wait_until="networkidle")
            over = page.evaluate(
                "document.documentElement.scrollWidth - window.innerWidth"
            )
            if over > 0:
                bad.append((w, path, over))
        page.close()
    browser.close()

if bad:
    print("OVERFLOW FOUND:")
    for w, path, over in bad:
        print(f"  {w}px  {path}  +{over}px")
    sys.exit(1)
print(f"OK: 0 overflow on {len(paths)} pages at {'/'.join(map(str, WIDTHS))}px")
