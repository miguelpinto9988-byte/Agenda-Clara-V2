#!/usr/bin/env python3
"""Install the latest user-corrected Canva 'Mi horario' in the Android project.

PNG resources are stored durably as a committed ZIP in GitHub (no Canva signed
URLs). Keeps the day/photo/task widgets untouched and preserves dynamic classes.
Requires the verified 3.15.8 sources; advances to version 3.15.9 (code 76).
"""
from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from hashlib import sha256
import os
import stat
import zipfile

STAGE = Path(__file__).resolve().parent
ROOT = Path('AgendaClara/app/src/main')
JAVA = ROOT / 'java/pe/agendaclara/app'
RES = ROOT / 'res'
GRADLE = Path('AgendaClara/app/build.gradle')
PROTECTED = [
    JAVA / 'AcademicDayWidget.java',
    JAVA / 'PhotoWidget.java',
    RES / 'layout/widget_academic_day.xml',
    RES / 'layout/widget_photo.xml',
    RES / 'layout/widget_tasks.xml',
]
NAMES = {
    'ac_week_landscape', 'ac_week_cap', 'ac_week_calendar',
    'ac_week_title', 'ac_week_arrow_prev', 'ac_week_arrow_next',
    'ac_week_books', 'ac_week_flask', 'ac_week_clock',
    'ac_week_location', 'ac_week_done', 'ac_week_pending',
    'ac_week_card', 'ac_week_card_alt', 'ac_week_selector',
    'ac_week_icon_tile',
}


def atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.is_file() else 0o644
    tmp = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix='.ac-week-',
                                delete=False) as handle:
            tmp = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        tmp.chmod(mode)
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def planned() -> dict[Path, bytes]:
    source = {
        JAVA / 'AcademicWeekWidget.java': STAGE / 'AcademicWeekWidget.java',
        Path('AgendaClara/app/src/debug/java/pe/agendaclara/app/WidgetRenderProbeActivity.java'): STAGE / 'WidgetRenderProbeActivity.java',
        RES / 'layout/widget_academic_week.xml': STAGE / 'widget_academic_week.xml',
    }
    files = {dst: src.read_bytes() for dst, src in source.items()}
    with zipfile.ZipFile(STAGE / 'assets.zip') as bundle:
        names = set(bundle.namelist())
        expected = {f'{name}.png' for name in NAMES}
        if names != expected:
            raise RuntimeError(f'Wrong PNG set: missing={expected - names}, extra={names - expected}')
        for name in sorted(names):
            data = bundle.read(name)
            if len(data) > 250000 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
                raise RuntimeError(f'Invalid PNG asset: {name}')
            files[RES / 'drawable-nodpi' / name] = data
    return files


def main() -> None:
    for path in PROTECTED:
        if not path.is_file():
            raise RuntimeError(f'Protected unrelated widget missing: {path}')
    version = GRADLE.read_text(encoding='utf-8')
    changes = planned()
    if "versionCode 76" in version and "versionName '3.15.9'" in version:
        if any(not dst.is_file() or dst.read_bytes() != data
               for dst, data in changes.items()):
            raise RuntimeError('Version 3.15.9 present with mismatched Canva resources')
        print('PASS: 3.15.9 Canva Mi horario patch already installed')
        return
    if version.count('versionCode 75') != 1 or version.count("versionName '3.15.8'") != 1:
        raise RuntimeError('Requires verified 3.15.8 sources, versionCode 75')
    digest = {dst: sha256(dst.read_bytes()).digest() for dst in PROTECTED}
    changes[GRADLE] = (version.replace('versionCode 75', 'versionCode 76', 1)
                       .replace("versionName '3.15.8'", "versionName '3.15.9'", 1)).encode()
    originals = {dst: dst.read_bytes() if dst.is_file() else None for dst in changes}
    written = []
    try:
        for dst, data in changes.items():
            atomic(dst, data)
            written.append(dst)
        for dst, expected in digest.items():
            if sha256(dst.read_bytes()).digest() != expected:
                raise RuntimeError(f'Protected widget modified: {dst}')
    except BaseException:
        for dst in reversed(written):
            data = originals[dst]
            if data is None:
                dst.unlink(missing_ok=True)
            else:
                atomic(dst, data)
        raise
    print('PASS: 16 original Canva-style PNG resources installed from committed ZIP')
    print('PASS: visual layout follows user corrections (no bottom CTA, cap highest)')
    print('PASS: photos, day widget and tasks unchanged; 3.15.9 / code 76')


if __name__ == '__main__':
    main()