#!/usr/bin/env python3
"""Install the approved PNG + native touch motion on Agenda Clara 3.8.2.

Apply strictly after updates/phase18/apply_3_8_2.py. The existing onClick
handler and navigation for the top-right + button are not changed.
"""
from pathlib import Path
import base64
import struct

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "AgendaClara/app"
SOURCE = APP / "src/main/java/pe/agendaclara/app/MainActivity.java"
MOTION = APP / "src/main/java/pe/agendaclara/app/TopPlusButtonMotion.java"
RESOURCE = APP / "src/main/res/drawable-nodpi/ic_top_plus_animated.png"
ANCHOR = "        body.removeAllViews();if(page==0)tasksPage();"
INSTALL = "        body.post(() -> TopPlusButtonMotion.install(this));\n"


def integrate(source: str) -> str:
    if source.count(ANCHOR) != 1 or "TopPlusButtonMotion.install(this)" in source:
        raise RuntimeError("Agenda Clara 3.8.2 MainActivity anchor differs; refusing to modify the button")
    # Post the scan; do not insert a statement between an if/else chain.
    return source.replace(ANCHOR, INSTALL + ANCHOR, 1)


def main():
    source = SOURCE.read_text(encoding="utf-8")
    revised = integrate(source)
    java = (Path(__file__).with_name("TopPlusButtonMotion.java")).read_text(encoding="utf-8")
    artwork = base64.b64decode(Path(__file__).with_name("icon_top_plus.b64").read_text().strip(), validate=True)
    if artwork[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", artwork[16:24]) != (144, 144):
        raise RuntimeError("Approved transparent 144px icon is invalid")
    if MOTION.exists() or RESOURCE.exists():
        raise RuntimeError("Top-plus resource already exists; refusing a partial overwrite")
    MOTION.write_text(java, encoding="utf-8")
    RESOURCE.parent.mkdir(parents=True, exist_ok=True)
    RESOURCE.write_bytes(artwork)
    SOURCE.write_text(revised, encoding="utf-8")
    print("Applied top-right + PNG and touch motion; original click remains intact")


if __name__ == "__main__":
    main()
