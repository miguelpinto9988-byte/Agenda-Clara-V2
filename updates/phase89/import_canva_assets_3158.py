#!/usr/bin/env python3
"""Check vendored PNG assets offline. No expiring Canva URLs required."""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent/"assets"
NAMES=("ac_day_landscape","ac_day_icon_calendar","ac_day_icon_cap",
"ac_day_icon_books","ac_day_icon_flask","ac_day_icon_clock",
"ac_day_icon_room","ac_day_icon_check","ac_day_icon_arrow")
def main():
    files=list(ROOT.glob("ac_day_*.png"))
    if len(files)!=9:raise RuntimeError("Missing approved PNG assets")
    for name in NAMES:
        path=ROOT/(name+".png")
        with Image.open(path) as image:
            if image.format!="PNG":raise RuntimeError("Resource must be PNG")
            if name=="ac_day_landscape":
                if image.width<600 or image.height<200:
                    raise RuntimeError("Landscape too small")
            elif image.width<180 or image.height<180 or (
                image.convert("RGBA").getchannel("A").getextrema()[0]!=0
            ):raise RuntimeError("Invalid transparent icon: "+name)
    print("PASS: 9 real PNG images vendored in source for offline builds")
if __name__=="__main__":main()
