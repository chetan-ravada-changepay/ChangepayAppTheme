"""ChangePay icons — copied byte-for-byte from the apps' own icon folders.

    python brand/scripts/build_icons.py

Sources, in priority order: ConsumerApp/assets/icons, then SellerApp/assets/icons. A name already taken
by an earlier source is skipped (and reported), so ConsumerApp's version wins. DeliveryApp has no
vector icons (PNG bitmaps + Flutter's Material icon font), so it is not a source.
Writes brand/icons/<category>/<name>.svg with the apps' own file names, plus
brand/icons/sprite.svg (themeable icons only: <use href="sprite.svg#cp-wallet"/>) and
brand/icons/icons.json (name -> category, themeable, path, source app). Add new icons to an app
first, then rerun this. Nothing here is redrawn.
"""

import json
import re
import shutil
import sys
from pathlib import Path

BRAND = Path(__file__).resolve().parent.parent
REPO = BRAND.parent.parent
SOURCES = [("ConsumerApp", REPO / "MobileApps/ConsumerApp/assets/icons"), ("SellerApp", REPO / "MobileApps/SellerApp/assets/icons")]
OUT = BRAND / "icons"

BRAND_MARKS = {
    "payments": {"google-pay", "phonepe", "upi", "razorpay", "ondc_logo"},
    "social": {"facebook", "instagram", "tiktok", "twitter", "whatsapp", "youtube"},
    "food": {"food_egg", "food_non_veg", "food_veg"},
    "changepay": {"changepay_coin", "quiz_coin", "nexus_ai"},
}


def category(name, text):
    for cat, names in BRAND_MARKS.items():
        if name in names:
            return cat
    if "currentColor" not in text:
        return "other"
    return "material" if name.startswith("ms_") else "outline"


def symbol(name, text):
    """Turn a standalone <svg> into a <symbol>, keeping its own presentation attributes."""
    m = re.search(r"<svg\b([^>]*)>(.*)</svg>", text, re.S)
    attrs = re.sub(r'\s(xmlns(:\w+)?|width|height|role|aria-[\w-]+)="[^"]*"', "", m.group(1))
    return f'<symbol id="cp-{name}"{attrs}>{m.group(2).strip()}</symbol>'


def main():
    for app, src in SOURCES:
        if not src.is_dir():
            sys.exit(f"{app} icons not found at {src}")
    if OUT.exists():
        shutil.rmtree(OUT)
    index, symbols, skipped = {}, [], []
    for app, src in SOURCES:
        for f in sorted(src.glob("*.svg")):
            name, text = f.stem, f.read_text()
            if name in index:
                same = f.read_bytes() == (OUT / index[name]["path"]).read_bytes()
                kept = "identical" if same else "differs — kept " + index[name]["source"]
                skipped.append(f"{app}/{f.name} ({kept})")
                continue
            cat = category(name, text)
            dest = OUT / cat / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)  # exact copy — never edited
            themeable = cat in ("outline", "material")
            index[name] = {"category": cat, "themeable": themeable, "path": f"{cat}/{f.name}", "source": app}
            if themeable:
                symbols.append(symbol(name, text))
    OUT.joinpath("sprite.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" style="display:none">{"".join(symbols)}</svg>\n'
    )
    OUT.joinpath("icons.json").write_text(
        json.dumps({"sources": [f"MobileApps/{a}/assets/icons" for a, _ in SOURCES], "icons": index}, indent=1) + "\n"
    )
    counts = {}
    for v in index.values():
        counts[v["category"]] = counts.get(v["category"], 0) + 1
    by_app = {}
    for v in index.values():
        by_app[v["source"]] = by_app.get(v["source"], 0) + 1
    print(f"{len(index)} icons → {OUT}: {counts} from {by_app}")
    for s_ in skipped:
        print("  skipped", s_)


if __name__ == "__main__":
    main()
