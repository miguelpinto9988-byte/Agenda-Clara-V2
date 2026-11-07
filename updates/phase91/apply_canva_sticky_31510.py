#!/usr/bin/env python3
"""Apply the approved Canva sticky-notes widget using its separate PNG assets.

Keeps real notes, stored colors, dates, editing/creation routes, and other widget
providers untouched. Base: Agenda Clara 3.15.9, versionCode 76.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
from tempfile import NamedTemporaryFile
import os
import stat
import zipfile

STAGE=Path(__file__).resolve().parent
ROOT=Path('AgendaClara/app/src/main')
JAVA=ROOT/'java/pe/agendaclara/app'
RES=ROOT/'res'
GRADLE=Path('AgendaClara/app/build.gradle')
PROTECTED=[
 JAVA/'PhotoWidget.java', JAVA/'AcademicDayWidget.java', JAVA/'AcademicWeekWidget.java',
 JAVA/'StickyNotesStore.java',JAVA/'StickyNotesUi.java', JAVA/'StickyNotesWidgetService.java',
 RES/'layout/widget_photo.xml',RES/'layout/widget_tasks.xml',
 RES/'layout/widget_academic_day.xml',RES/'layout/widget_academic_week.xml',
]
PNG_NAMES={
 'ac_notes_landscape','ac_notes_header','ac_notes_add','ac_notes_counter',
 'ac_notes_stack','ac_notes_date',
 *{'ac_notes_square_'+c for c in ('yellow','purple','green','blue','peach','pink')},
 *{'ac_notes_horizontal_'+c for c in ('yellow','purple','green','blue','peach','pink')},
 *{'ac_notes_pin_'+c for c in ('blue','purple','green','pink','yellow')},
}


def atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 mode=stat.S_IMODE(path.stat().st_mode) if path.is_file() else 0o644
 temporary=None
 try:
  with NamedTemporaryFile(dir=path.parent,prefix='.ac-sticky-',delete=False) as f:
   temporary=Path(f.name)
   f.write(data);f.flush();os.fsync(f.fileno())
  temporary.chmod(mode)
  os.replace(temporary,path)
 finally:
  if temporary is not None:temporary.unlink(missing_ok=True)


def plan():
 files={
  JAVA/'StickyNotesWidget.java':(STAGE/'StickyNotesWidget.java').read_bytes(),
  Path('AgendaClara/app/src/debug/java/pe/agendaclara/app/WidgetRenderProbeActivity.java'):(STAGE/'WidgetRenderProbeActivity.java').read_bytes(),
  RES/'layout/widget_notes_board.xml':(STAGE/'widget_notes_board.xml').read_bytes(),
  RES/'layout/widget_notes_board_compact.xml':(STAGE/'widget_notes_board_compact.xml').read_bytes(),
  RES/'layout/widget_notes_board_row.xml':(STAGE/'widget_notes_board_row.xml').read_bytes(),
  RES/'layout/widget_notes_board_row_compact.xml':(STAGE/'widget_notes_board_row_compact.xml').read_bytes(),
  RES/'drawable/ac_notes_shell.xml':(STAGE/'ac_notes_shell.xml').read_bytes(),
  RES/'drawable/ac_notes_empty.xml':(STAGE/'ac_notes_empty.xml').read_bytes(),
 }
 meta=RES/'xml/sticky_notes_widget_info.xml'
 info=meta.read_text(encoding='utf-8')
 if info.count('@layout/widget_sticky_notes')==2:
  info=info.replace('@layout/widget_sticky_notes','@layout/widget_notes_board')
 elif info.count('@layout/widget_notes_board')!=2:
  raise RuntimeError('Unexpected sticky widget metadata')
 files[meta]=info.encode()
 with zipfile.ZipFile(STAGE/'assets.zip') as bundle:
  names=set(bundle.namelist());expected={name+'.png' for name in PNG_NAMES}
  if names!=expected:raise RuntimeError(f'PNG assets incomplete: {expected-names}; extras={names-expected}')
  for name in sorted(expected):
   data=bundle.read(name)
   if not data.startswith(b'\x89PNG\r\n\x1a\n') or len(data)>500_000:
    raise RuntimeError('Invalid PNG: '+name)
   files[RES/'drawable-nodpi'/name]=data
 return files


def main():
 for f in PROTECTED:
  if not f.is_file():raise RuntimeError('Missing protected file '+str(f))
 version=GRADLE.read_text(encoding='utf-8')
 changes=plan()
 if 'versionCode 77' in version and "versionName '3.15.10'" in version:
  if any(not f.is_file() or f.read_bytes()!=data for f,data in changes.items()):
   raise RuntimeError('Version 3.15.10 present but Canva resources differ')
  print('PASS: patch already applied, no changes')
  return
 if version.count('versionCode 76')!=1 or version.count("versionName '3.15.9'")!=1:
  raise RuntimeError('Requires verified version 3.15.9 (code 76)')
 protected={p:sha256(p.read_bytes()).digest() for p in PROTECTED}
 changes[GRADLE]=(version.replace('versionCode 76','versionCode 77',1)
   .replace("versionName '3.15.9'","versionName '3.15.10'",1)).encode()
 originals={p:p.read_bytes() if p.is_file() else None for p in changes}
 written=[]
 try:
  for path,data in changes.items():
   atomic(path,data);written.append(path)
  if any(sha256(path.read_bytes()).digest()!=digest for path,digest in protected.items()):
   raise RuntimeError('Protected original provider or storage was changed')
 except BaseException:
  for p in reversed(written):
   if originals[p] is None:p.unlink(missing_ok=True)
   else:atomic(p,originals[p])
  raise
 print('PASS: PNG backgrounds/cards/pins separate, real note fields preserved')
 print('PASS: Other widgets, notes DB/editor, and photo unchanged')
 print('PASS: Agenda Clara 3.15.10, versionCode 77')

if __name__=='__main__':main()
