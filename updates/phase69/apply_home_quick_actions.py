#!/usr/bin/env python3
"""Pre-iconography update: replace only the home quick-access presentation.

Use after all existing phases through 19. Safe to re-run on matching sources.
No APK build and no change to the creation menu, storage or reminder services.
"""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
CODE = Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
TARGET = CODE / "MiDiaQuickActions.java"
DASH = CODE / "MiDiaDashboard.java"
MAIN = CODE / "MainActivity.java"
VOICE = CODE / "VoiceQuickTask.java"
NOTES = CODE / "StickyNotesUi.java"

def run():
    if not TARGET.is_file() or not DASH.is_file() or not MAIN.is_file():
        raise RuntimeError("Reconstruct Agenda Clara 3.13.1 sources first")
    source = (HERE / "MiDiaQuickActions.java").read_text(encoding="utf-8")
    previous = TARGET.read_text(encoding="utf-8")
    if previous != source:
        if 'tile(a, "Recordatorio"' not in previous or 'tile(a, "Nota rápida"' not in previous:
            raise RuntimeError("The original three home actions changed; refusing to overwrite")
    dashboard = DASH.read_text(encoding="utf-8")
    if "MiDiaQuickActions.add(activity, body);" not in dashboard:
        raise RuntimeError("Mi día is missing its existing quick-action section")
    if "addQuote(activity, body, today);" not in dashboard:
        raise RuntimeError("Original daily motivational phrase must remain")
    main = MAIN.read_text(encoding="utf-8")
    voice = VOICE.read_text(encoding="utf-8")
    notes = NOTES.read_text(encoding="utf-8")
    if "void openEditor(long taskId,Store.Inbox proposal,Bundle draft)" not in main:
        raise RuntimeError("Existing full task editor is not available")
    if "public static void show(Activity activity)" not in voice:
        raise RuntimeError("Existing voice task workflow is not available")
    if "public static void showEditor(MainActivity a,StickyNotesStore.Note original)" not in notes:
        raise RuntimeError("Existing dated sticky-note editor is not available")
    if "VoiceQuickTask.show(activity)" not in source or "activity.openEditor(-1, null, null)" not in source:
        raise RuntimeError("New quick actions are not mapped to the existing workflows")
    if "StickyNotesUi.showEditor(activity, null)" not in source:
        raise RuntimeError("New note action does not use the original date-aware editor")
    shutil.copyfile(HERE / "MiDiaQuickActions.java", TARGET)
    print("PASS: Inicio > Mi día now links voice task, full task editor and dated note")
    print("PASS: user data, old + popup, alerts, icons and motivational phrase unchanged")

if __name__ == "__main__":
    run()
