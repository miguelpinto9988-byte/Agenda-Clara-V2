#!/usr/bin/env python3
"""Source QA for Agenda Clara 3.15.10 Canva sticky-note widget."""
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
from hashlib import sha256
p=Path('AgendaClara/app/src/main')
res=p/'res'
ns='{http://schemas.android.com/apk/res/android}'
checks={
 'widget_notes_board.xml':{'sticky_widget_root','sticky_widget_header','sticky_widget_count','sticky_widget_add','sticky_widget_add_label','sticky_widget_list','sticky_widget_empty'},
 'widget_notes_board_compact.xml':{'sticky_widget_root','sticky_widget_header','sticky_widget_count','sticky_widget_add','sticky_widget_add_label','sticky_widget_list','sticky_widget_empty'},
 'widget_notes_board_row.xml':{'sticky_widget_row','sticky_widget_art','sticky_widget_pin','sticky_widget_title','sticky_widget_body','sticky_widget_date'},
 'widget_notes_board_row_compact.xml':{'sticky_widget_row','sticky_widget_art','sticky_widget_pin','sticky_widget_title','sticky_widget_body','sticky_widget_date'},
}
for name,wanted in checks.items():
 root=ET.parse(res/'layout'/name).getroot()
 ids={e.get(ns+'id','').split('/')[-1] for e in root.iter()}
 assert wanted<=ids,(name,wanted-ids)
 assert ('GridView' if name=='widget_notes_board.xml' else 'ListView' if name=='widget_notes_board_compact.xml' else 'ImageView') in ET.tostring(root,encoding='unicode')
 for element in root.iter():
  for value in element.attrib.values():
   if value.startswith('@drawable/'):
    label=value.split('/')[-1]
    assert (res/'drawable-nodpi'/(label+'.png')).is_file() or (res/'drawable'/(label+'.xml')).is_file(),(name,label)
 info=ET.parse(res/'xml/sticky_notes_widget_info.xml').getroot()
 assert info.get(ns+'initialLayout')=='@layout/widget_notes_board'
 assert info.get(ns+'previewLayout')=='@layout/widget_notes_board'
for file in (res/'drawable-nodpi').glob('ac_notes_*.png'):
 with Image.open(file) as img:
  assert img.format=='PNG'
  if file.stem!='ac_notes_landscape':
   assert img.mode=='RGBA' and img.getchannel('A').getextrema()[0]==0,file
asset_count=len(list((res/'drawable-nodpi').glob('ac_notes_*.png')))
assert asset_count==23,asset_count
java=(p/'java/pe/agendaclara/app/StickyNotesWidget.java').read_text()
for required in ['StickyNotesStore.get(context).all()','note.title','note.body','note.day',
 'note.color','sticky_widget_list','sticky_widget_add','sticky_widget_header',
 'setOnClickFillInIntent','setPendingIntentTemplate','StickyNotesWidgetService.class',
 'sticky_widget_pin','sticky_widget_count','RemoteCollectionItems.Builder','sticky_widget_empty']:
 assert required in java,required
for fake in ['Resolver dudas académicas','Revisar el sílabo','Ideas para el proyecto','Organizar mis estudios']:
 assert fake not in java
assert 'versionCode 77' in Path('AgendaClara/app/build.gradle').read_text()
print('PASS: 23 PNG assets, transparency, remote layouts and real note bindings')
print('PASS: 2-column board, compact list, existing stored notes and intents')
