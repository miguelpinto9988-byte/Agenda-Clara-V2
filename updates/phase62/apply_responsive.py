#!/usr/bin/env python3
"""Phase 14: responsive/accessibility polish for 280dp+ phones and wide tablets."""
from pathlib import Path

CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HEADER = CODE / "MiDiaHeaderView.java"
CARD = CODE / "MiDiaClassCard.java"
DASH = CODE / "MiDiaDashboard.java"

def replace_once(source, old, new, label):
    if new in source and old not in source:
        return source
    if source.count(old) != 1:
        raise RuntimeError("Phase14 unsafe anchor: " + label)
    return source.replace(old, new, 1)

def run():
    header = HEADER.read_text(encoding="utf-8")
    card = CARD.read_text(encoding="utf-8")
    dashboard = DASH.read_text(encoding="utf-8")
    header = replace_once(header,
        "        welcome.setPadding(dp(15), dp(16), dp(13), dp(8));",
        "        welcome.setPadding(dp(15), dp(16), dp(13), dp(8));\n"
        "        welcome.setClipChildren(false);",
        "hero welcome")
    header = replace_once(header,
        "        dateSubtitle = text(context, \"\", 11, MUTED, false);\n        dateLines.addView(dateSubtitle);",
        "        dateSubtitle = text(context, \"\", 11, MUTED, false);\n"
        "        dateSubtitle.setSingleLine(true);\n"
        "        dateSubtitle.setEllipsize(TextUtils.TruncateAt.END);\n"
        "        dateLines.addView(dateSubtitle);",
        "date subtitle overflow")
    card = replace_once(card,
        "        card.setMinimumHeight(a.dp(84));" if "card.setMinimumHeight(a.dp(84));" in card
        else "        card.setFocusable(true);",
        "        card.setMinimumHeight(a.dp(84));" if "card.setMinimumHeight(a.dp(84));" in card
        else "        card.setMinimumHeight(a.dp(84));\n        card.setFocusable(true);",
        "class card minimum height")
    dashboard = replace_once(dashboard,
        "        boolean twoRows = widthDp < 360 || fontScale > 1.28f;",
        "        boolean twoRows = widthDp < 400 || fontScale > 1.28f;",
        "small phone stat layout")
    if "greeting.setTextSize(widthDp < 360f ? 21f : 23f)" not in header:
        raise RuntimeError("Phase9 small-phone fix is missing")
    if "MiDiaQuickActions.add(activity, body);" not in dashboard:
        raise RuntimeError("Phase12 quick actions missing")
    if "addQuote(activity, body, today);" not in dashboard:
        raise RuntimeError("Phase13 original motivation missing")
    HEADER.write_text(header, encoding="utf-8")
    CARD.write_text(card, encoding="utf-8")
    DASH.write_text(dashboard, encoding="utf-8")
    print("PASS phase14: small phone cards wrap, date truncates, panorama adapts; no data changes")

if __name__ == "__main__":
    run()
