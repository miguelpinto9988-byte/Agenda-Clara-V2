#!/usr/bin/env python3
"""Phase 16: add dedicated top/bottom edge fades to the full-bleed native header.

Must run after phases 9-14. Only the home header changes; the image rotation,
course schedule, task storage, five tabs and motivational phrase are untouched.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEADER = Path("AgendaClara/app/src/main/java/pe/agendaclara/app/MiDiaHeaderView.java")

BEFORE = """        landscapeFrame.addView(readableOverlay, new FrameLayout.LayoutParams(-1, -1));

        LinearLayout welcome = new LinearLayout(context);"""
AFTER = """        landscapeFrame.addView(readableOverlay, new FrameLayout.LayoutParams(-1, -1));

        // Phase 16: independent edge fades visually join white chrome and the
        // floating date without bleaching the middle of the selected landscape.
        View topEdgeFade = new View(context);
        topEdgeFade.setTag("mi_dia_hero_edge_top");
        topEdgeFade.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{0xffffffff, 0x8cffffff, 0x00ffffff}));
        landscapeFrame.addView(topEdgeFade,
                new FrameLayout.LayoutParams(-1, dp(68), Gravity.TOP));

        View bottomEdgeFade = new View(context);
        bottomEdgeFade.setTag("mi_dia_hero_edge_bottom");
        bottomEdgeFade.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{0x00ffffff, 0x58ffffff, 0xffffffff}));
        landscapeFrame.addView(bottomEdgeFade,
                new FrameLayout.LayoutParams(-1, dp(74), Gravity.BOTTOM));

        LinearLayout welcome = new LinearLayout(context);"""

CLIP_BEFORE = """        landscapeFrame.setBackgroundColor(0xffe9f4ff);
        FrameLayout.LayoutParams coverParams ="""
CLIP_AFTER = """        landscapeFrame.setBackgroundColor(0xffe9f4ff);
        // Clip the photo and overlays to the scenic panel; the date card floats
        // in the outer imageStack and is deliberately not clipped.
        landscapeFrame.setClipChildren(true);
        landscapeFrame.setClipToPadding(true);
        FrameLayout.LayoutParams coverParams ="""

def only_once(text, old, new, name):
    if new in text and old not in text:
        return text
    if text.count(old) != 1:
        raise RuntimeError("Unexpected header around " + name + "; no files changed")
    return text.replace(old, new, 1)

def run():
    original = HEADER.read_text(encoding="utf-8")
    changed = only_once(original, BEFORE, AFTER, "gradient overlay stack")
    changed = only_once(changed, CLIP_BEFORE, CLIP_AFTER, "photo clip")
    required = (
        "MiDiaDailyRotation.backgroundResource(getContext(), today)",
        "MiDiaDailyRotation.quote(getContext(), today)",
        "quote.setVisibility(View.GONE)",
        "landscape.setScaleType(ImageView.ScaleType.CENTER_CROP)",
        "greeting.setMaxLines(2)",
        'new FrameLayout.LayoutParams(-1, dp(68), Gravity.TOP)',
        'new FrameLayout.LayoutParams(-1, dp(74), Gravity.BOTTOM)',
    )
    missing = [token for token in required if token not in changed]
    if missing:
        raise RuntimeError("Header protection failure: " + repr(missing))
    HEADER.write_text(changed, encoding="utf-8")
    print("PASS phase16: subtle white edge fades, clipped photo, floating date intact")

if __name__ == "__main__":
    run()
