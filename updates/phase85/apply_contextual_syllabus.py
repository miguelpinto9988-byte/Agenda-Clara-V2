#!/usr/bin/env python3
"""Install Agenda Clara 3.15.4 contextual syllabus parsing without editing user data."""
from pathlib import Path
import hashlib
import os
import tempfile

APP = Path("AgendaClara/app/src/main")
JAVA = APP / "java/pe/agendaclara/app"
GRADLE = Path("AgendaClara/app/build.gradle")
STAGE = Path(__file__).resolve().parent

FILES = {
    JAVA / "SyllabusContextualPartials.java": STAGE / "SyllabusContextualPartials.java",
    JAVA / "SyllabusImportPipeline.java": STAGE / "SyllabusImportPipeline.java",
}
PROTECTED = (
    JAVA / "PhotoWidget.java",
    JAVA / "PhotoConfigActivity.java",
    JAVA / "PhotoTapActivity.java",
    APP / "res/layout/widget_photo.xml",
    APP / "res/xml/photo_widget_info.xml",
    APP / "res/layout/widget_academic_day.xml",
    APP / "res/layout/widget_academic_week.xml",
)


def atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                dir=path.parent, prefix=f".{path.name}.phase85-",
                delete=False) as out:
            temporary = Path(out.name)
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> None:
    gradle = GRADLE.read_text(encoding="utf-8")
    present = "versionCode 71" in gradle and "versionName '3.15.4'" in gradle
    for file in PROTECTED:
        if not file.is_file():
            raise RuntimeError(f"Missing protected widget file: {file}")
    if present:
        if gradle.count("versionCode 71") != 1 or gradle.count(
                "versionName '3.15.4'") != 1:
            raise RuntimeError("Inconsistent version fields")
        if any(not target.is_file() or target.read_bytes() != source.read_bytes()
               for target, source in FILES.items()):
            raise RuntimeError("3.15.4 version present but contextual sources differ")
        print("PASS: Agenda Clara 3.15.4 contextual migration already applied")
        return
    if gradle.count("versionCode 70") != 1 or gradle.count(
            "versionName '3.15.3'") != 1:
        raise RuntimeError("Requires verified Agenda Clara 3.15.3 sources")
    existing = (JAVA / "SyllabusImportPipeline.java").read_text(encoding="utf-8")
    if existing.count("return merged;") != 1 or "SyllabusContextualPartials" in existing:
        raise RuntimeError("Unexpected syllabus pipeline; refusing unsafe overwrite")
    if (JAVA / "SyllabusContextualPartials.java").exists():
        raise RuntimeError("Contextual resolver already present with an older version")
    proposed = (STAGE / "SyllabusImportPipeline.java").read_text(encoding="utf-8")
    if proposed.count("SyllabusContextualPartials.resolve(pages,merged)") != 1:
        raise RuntimeError("Missing contextual resolver integration")
    staged = (STAGE / "SyllabusContextualPartials.java").read_text(encoding="utf-8")
    for requirement in ("class SyllabusContextualPartials", "dates.size() == 1",
                        "TreeMap<Integer, Group>", "keepStandalone"):
        if requirement not in staged:
            raise RuntimeError("Contextual resolver missing evidence rule: " + requirement)
    changes = {target: source.read_bytes() for target, source in FILES.items()}
    changes[GRADLE] = (
        gradle.replace("versionCode 70", "versionCode 71", 1)
              .replace("versionName '3.15.3'", "versionName '3.15.4'", 1)
    ).encode("utf-8")
    hashes = {p: hashlib.sha256(p.read_bytes()).digest() for p in PROTECTED}
    previous = {p: p.read_bytes() if p.exists() else None for p in changes}
    completed = []
    try:
        for path, content in changes.items():
            atomic(path, content)
            completed.append(path)
        if any(hashlib.sha256(p.read_bytes()).digest() != hashes[p] for p in PROTECTED):
            raise RuntimeError("A protected widget changed unexpectedly")
    except BaseException:
        for path in reversed(completed):
            old = previous[path]
            if old is None:
                path.unlink(missing_ok=True)
            else:
                atomic(path, old)
        raise
    print("PASS: syllabus partial-exam correlation installed without modifying widgets")
    print("PASS: source migration 3.15.4 / versionCode 71 is transactional")


if __name__ == "__main__":
    main()
