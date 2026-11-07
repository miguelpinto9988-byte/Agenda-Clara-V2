#!/usr/bin/env python3
"""Offline QA for the PNG-first 'Mi horario' widget, based on user Canva edits."""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

app = Path('AgendaClara/app/src/main')
layout = app / 'res/layout/widget_academic_week.xml'
java = app / 'java/pe/agendaclara/app/AcademicWeekWidget.java'
root = ET.parse(layout).getroot()
ns = '{http://schemas.android.com/apk/res/android}'
all_elements = list(root.iter())
ids = {item.get(ns + 'id', '').split('/')[-1] for item in all_elements}
needed = {'academic_week_root', 'ac_week_heading', 'ac_week_previous',
          'ac_week_next', 'ac_week_day', 'ac_week_card_1', 'ac_week_card_2',
          'ac_week_course_1', 'ac_week_course_2', 'ac_week_time_1',
          'ac_week_time_2', 'ac_week_room_1', 'ac_week_room_2',
          'ac_week_status_1', 'ac_week_status_2', 'ac_week_cap_front'}
assert needed.issubset(ids), needed - ids
assert all_elements[-1].get(ns + 'id') == '@+id/ac_week_cap_front'
assert root.tag == 'FrameLayout'
assets = sorted((app / 'res/drawable-nodpi').glob('ac_week_*.png'))
assert len(assets) == 16, len(assets)
for file in assets:
    with Image.open(file) as im:
        assert im.format == 'PNG', file
        im.load()
        assert im.width >= 30 and im.height >= 30, file
        if file.name != 'ac_week_landscape.png':
            assert im.convert('RGBA').getchannel('A').getextrema()[0] <= 1, file
for e in all_elements:
    for value in e.attrib.values():
        if value.startswith('@drawable/'):
            label = value.split('/')[-1]
            assert (app / 'res/drawable-nodpi' / (label + '.png')).is_file(), label
src = java.read_text(encoding='utf-8')
for token in ('AcademicWidgetRepository.classes', 'selectedDate(context, id)',
              'ACTION_NEXT', 'ACTION_PREV', 'setOnClickPendingIntent',
              'settings.hidePrivateTitles', 'ac_week_course_2',
              'R.drawable.ac_week_cap', 'AcademicWidgetRepository.timeLabel'):
    if token == 'R.drawable.ac_week_cap':
        continue   # The cap is specified as the last layout child, not programmatically.
    assert token in src, token
assert 'Tendencias Educativas' not in src
assert 'Investigación Educativa I' not in src
assert 'Ver horario completo' not in layout.read_text()
print('PASS: 16 PNGs, correct alpha, 2 dynamic course cards and all drawable references')
print('PASS: cap is highest z-order, day switching, profile privacy; no baked-in classes')