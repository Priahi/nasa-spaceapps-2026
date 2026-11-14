#!/usr/bin/env python3
"""Headless Playwright smoke test for the local Hot Spots demo.

Usage (server already running at BASE_url):
    python3 smoke_test.py --base http://127.0.0.1:8765 --out screenshots
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8765")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "screenshots"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {"ok": True, "console_errors": [], "pages": {}, "checks": []}

    def fail(msg):
        report["ok"] = False
        report["checks"].append({"check": msg, "ok": False})
        print("FAIL:", msg)

    def ok(msg):
        report["checks"].append({"check": msg, "ok": True})
        print("OK:", msg)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        def on_console(msg):
            if msg.type in ("error", "warning"):
                entry = {"type": msg.type, "text": msg.text}
                report["console_errors"].append(entry)
                print("CONSOLE", msg.type, msg.text)

        page.on("console", on_console)
        page.on("pageerror", lambda exc: report["console_errors"].append({"type": "pageerror", "text": str(exc)}))

        # Health + meta first (API)
        resp = page.request.get(f"{args.base}/api/health")
        health = resp.json()
        report["pages"]["health"] = health
        if not (resp.ok and health.get("ready")):
            fail(f"health not ready: {health}")
        else:
            ok("api health ready")

        meta = page.request.get(f"{args.base}/api/meta").json()
        if "Canada" not in (meta.get("countries") or {}) or meta["countries"]["Canada"].get("status") != "ok":
            fail("Canada metrics missing")
        else:
            ok("api meta has Canada metrics")

        # Default Canada calendar
        cal = page.request.get(
            f"{args.base}/api/calendar?country=Canada&west=-141&south=41.7&east=-52.6&north=83.1"
        ).json()
        n_cal = len(cal.get("calendar") or [])
        if n_cal != 26 * 12:
            fail(f"Canada calendar has {n_cal} cells, expected 312")
        else:
            ok("Canada country calendar is a full 2000-2025 grid")
        # 2023-09 should be a high unusual month for Canada
        sep23 = next((r for r in cal["calendar"] if r["year"] == 2023 and r["month"] == 9), None)
        if not sep23 or not sep23.get("harmonized") or sep23["harmonized"] < 1000:
            fail(f"Canada Sep 2023 unexpected: {sep23}")
        else:
            ok(f"Canada Sep 2023 harmonized={sep23['harmonized']} unusual={sep23.get('unusual')}")

        csv = page.request.get(
            f"{args.base}/api/export.csv?country=Canada&west=-120&south=49&east=-110&north=60"
        )
        body = csv.body()
        if csv.ok and b"harmonized_count" in body and b"2023" in body and len(body) > 500:
            ok(f"CSV export {len(body)} bytes, content-type={csv.headers.get('content-type')}")
            (out / "sample_alberta.csv").write_bytes(body)
        else:
            fail(f"CSV export failed status={csv.status} bytes={len(body)}")

        page.goto(args.base, wait_until="networkidle", timeout=60000)
        page.wait_for_function(
            "document.getElementById('status') && !document.getElementById('status').textContent.startsWith('Loading')",
            timeout=60000,
        )
        page.wait_for_selector("#calTable")
        status = page.inner_text("#status")
        n_cells = page.evaluate("document.querySelectorAll('#calendar td[data-year]').length")
        if "Failed" in status:
            fail(f"UI status failed: {status}")
        elif n_cells != 312:
            fail(f"UI calendar cells={n_cells}")
        else:
            ok(f"UI loaded Canada calendar ({n_cells} cells). status={status[:120]}")
        page.screenshot(path=str(out / "01_canada_overview.png"), full_page=True)
        ok("screenshot 01_canada_overview.png")

        # Switch to Alberta
        page.select_option("#preset", "alberta")
        page.wait_for_function(
            "document.getElementById('aoiLabel') && document.getElementById('aoiLabel').textContent.includes('Alberta') || document.getElementById('aoiLabel').textContent.includes('-120')",
            timeout=30000,
        )
        # wait for reload
        page.wait_for_timeout(1500)
        page.wait_for_function(
            "document.getElementById('status') && document.getElementById('status').textContent.startsWith('Loaded')",
            timeout=60000,
        )
        aoi = page.inner_text("#aoiLabel")
        reasons = page.inner_text("#reasons")
        if "VIIRS / MODIS" not in reasons:
            fail(f"reasons panel did not update: {reasons[:200]}")
        else:
            ok(f"Alberta preset updated reasons. aoi={aoi}")
        page.screenshot(path=str(out / "02_alberta_calendar.png"), full_page=True)
        ok("screenshot 02_alberta_calendar.png")

        # Switch to Argentina Chaco
        page.select_option("#preset", "chaco")
        page.wait_for_timeout(1500)
        page.wait_for_function(
            "document.getElementById('status') && document.getElementById('status').textContent.startsWith('Loaded')",
            timeout=60000,
        )
        aoi = page.inner_text("#aoiLabel")
        if "Argentina" not in aoi and "Argentina" not in page.inner_text("#status"):
            # aoi label includes country
            fail(f"Chaco preset did not switch country: {aoi}")
        else:
            ok(f"Chaco preset loaded. aoi={aoi}")
        page.screenshot(path=str(out / "03_argentina_chaco.png"), full_page=True)
        ok("screenshot 03_argentina_chaco.png")

        # Download CSV via the button (also hits the same endpoint)
        with page.expect_download() as dl_info:
            page.click("#csvBtn")
        download = dl_info.value
        dest = out / download.suggested_filename
        download.save_as(str(dest))
        text = dest.read_text(encoding="utf-8")
        if "harmonized_count" in text and "FIRMS" in text:
            ok(f"UI CSV download saved {dest.name} ({len(text)} chars)")
        else:
            fail(f"UI CSV download unexpected content ({dest})")

        hard_errors = [e for e in report["console_errors"] if e["type"] in ("error", "pageerror") and "favicon.ico" not in e.get("text", "")]
        # Leaflet / font 404s shouldn't happen; filter known benign warnings if any
        if hard_errors:
            fail(f"{len(hard_errors)} console errors: {hard_errors}")
        else:
            ok("no console errors")

        browser.close()

    (out / "smoke_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "n_checks": len(report["checks"]), "n_console": len(report["console_errors"])}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
