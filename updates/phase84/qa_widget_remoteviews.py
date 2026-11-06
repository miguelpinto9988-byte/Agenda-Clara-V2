#!/usr/bin/env python3
"""Check every widget XML against Android RemoteViews inflater restrictions."""
from pathlib import Path
import xml.etree.ElementTree as ET

APP = Path("AgendaClara/app/src/main")
LAYOUTS = APP / "res/layout"
XML = APP / "res/xml"
MANIFEST = APP / "AndroidManifest.xml"
AND = "{http://schemas.android.com/apk/res/android}"
ALLOWED = {
    "AdapterViewFlipper", "FrameLayout", "GridLayout", "GridView",
    "LinearLayout", "ListView", "RelativeLayout", "StackView",
    "ViewFlipper", "AnalogClock", "Button", "Chronometer", "ImageButton",
    "ImageView", "ProgressBar", "TextClock", "TextView", "ViewStub",
    # The project targets API 35; these became supported at API 31.
    "CheckBox", "RadioButton", "RadioGroup", "Switch",
}
EXPECTED = {
    "TaskWidget": ("task_widget_info", "widget_tasks"),
    "StickyNotesWidget": ("sticky_notes_widget_info", "widget_sticky_notes"),
    "AcademicDayWidget": ("widget_academic_day_info", "widget_academic_day"),
    "AcademicWeekWidget": ("widget_academic_week_info", "widget_academic_week"),
    "PhotoWidget": ("photo_widget_info", "widget_photo"),
}


def main() -> None:
    checked = 0
    names = set()
    for path in sorted(LAYOUTS.glob("widget*.xml")):
        root = ET.parse(path).getroot()
        names.add(path.stem)
        for node in root.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag not in ALLOWED:
                raise AssertionError(f"{path}: unsupported RemoteViews class <{tag}>")
        checked += 1
    manifest = ET.parse(MANIFEST).getroot()
    app = manifest.find("application")
    assert app is not None
    for provider, (info, layout) in EXPECTED.items():
        receivers = [
            node for node in app.findall("receiver")
            if node.get(AND + "name") == "." + provider
        ]
        assert len(receivers) == 1, f"Missing or duplicate receiver: {provider}"
        metadata = receivers[0].find("meta-data")
        assert metadata is not None and metadata.get(AND + "resource") == "@xml/" + info, provider
        provider_xml = ET.parse(XML / (info + ".xml")).getroot()
        assert provider_xml.get(AND + "initialLayout") == "@layout/" + layout, provider
        assert provider_xml.get(AND + "previewLayout") == "@layout/" + layout, provider
        assert layout in names, provider
    for layout in ("widget_academic_day", "widget_academic_week"):
        root = ET.parse(LAYOUTS / (layout + ".xml")).getroot()
        separators = [
            child for child in list(root)
            if child.tag == "FrameLayout" and child.get(AND + "layout_height") == "1dp"
        ]
        assert len(separators) == 1, f"Missing supported divider in {layout}"
    print(f"PASS: {checked} widget layouts use only Android RemoteViews-safe classes")
    print("PASS: all five providers declare valid receivers and resolvable initial/preview layouts")
    print("PASS: academic day and week separators are safe FrameLayouts")


if __name__ == "__main__":
    main()
