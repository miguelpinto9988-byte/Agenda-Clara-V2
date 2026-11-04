#!/usr/bin/env python3
"""Phase 13: responsive panoramic hero for compact Android phones AND tablets.
Keep the existing quote and all 30 backgrounds unchanged.
Apply after phase60; no classes outside the home header are touched.
"""
from pathlib import Path

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HEADER = CODE / "MiDiaHeaderView.java"

OLD = """        // Phones as narrow as 280dp need a taller cover to hold the greeting
        // and leave the date floating below. Tablets retain a panoramic ratio.
        float widthDp = width / getResources().getDisplayMetrics().density;
        int minimum = widthDp < 360 ? 224 : widthDp < 480 ? 215 : 205;
        int visualHeight = Math.max(dp(minimum),
                Math.min(dp(450), Math.round(width * 864f / 1920f)));
        greeting.setTextSize(widthDp < 330 ? 19 : widthDp < 400 ? 21 : 23);"""
NEW = """        // Compact phones need an actual scenic hero, not a thin panoramic strip.
        // Tablets can keep the 1920x864 artwork ratio at much larger heights.
        float density = getResources().getDisplayMetrics().density;
        float widthDp = width / Math.max(0.1f, density);
        int visualHeight;
        if (widthDp < 360f) {
            visualHeight = Math.max(dp(225), Math.min(dp(285),
                    Math.round(width * 0.73f)));
        } else if (widthDp < 600f) {
            visualHeight = Math.max(dp(225), Math.min(dp(365),
                    Math.round(width * 0.62f)));
        } else {
            visualHeight = Math.max(dp(285), Math.min(dp(480),
                    Math.round(width * 864f / 1920f)));
        }
        greeting.setTextSize(widthDp < 360f ? 21f : 23f);
        dateTitle.setTextSize(widthDp < 360f ? 13f : 15f);
        dateSubtitle.setTextSize(widthDp < 360f ? 10f : 11f);"""

def run():
    if not HEADER.is_file():
        raise RuntimeError("Phase56 must be applied first")
    source = HEADER.read_text(encoding="utf-8")
    if NEW not in source:
        if source.count(OLD) != 1:
            raise RuntimeError("Unexpected header version, refusing unreviewed change")
        source = source.replace(OLD, NEW, 1)
    # Prevent a long, custom greeting from overlapping the date on small devices.
    original = '        greeting.setContentDescription("Saludo del día. Toca para personalizar el nombre");'
    replacement = original + """
        greeting.setMaxLines(2);
        greeting.setEllipsize(TextUtils.TruncateAt.END);"""
    if replacement not in source:
        if source.count(original) != 1:
            raise RuntimeError("Greeting structure has changed")
        source = source.replace(original, replacement, 1)
    required = (
        "landscape.setScaleType(ImageView.ScaleType.CENTER_CROP)",
        "MiDiaDailyRotation.backgroundResource(getContext(), today)",
        "MiDiaDailyRotation.quote(getContext(), today)",
        "quote.setVisibility(View.GONE)",
        "Math.round(width * 864f / 1920f)",
        "widthDp < 360f",
        "widthDp < 600f",
    )
    if not all(item in source for item in required):
        raise RuntimeError("Panorama, quote or small-device rules missing")
    HEADER.write_text(source, encoding="utf-8")
    print("PASS phase13: scenic hero 225-365dp on phones, aspect-ratio hero on tablets")
    print("PASS phase13: greeting adapts to compact widths, 30 landscape/50 quote rotation preserved")

if __name__ == "__main__":
    run()
