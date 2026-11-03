#!/usr/bin/env python3
"""Resource budget and non-regression checks before Android compilation."""
from pathlib import Path
import json,re
r=Path('AgendaClara');src=r/'app/src/main/java/pe/agendaclara/app';res=r/'app/src/main/res/drawable-nodpi'
meta=json.loads((r/'app/src/main/assets/adaptive_icon_catalog.json').read_text())
assert meta['count']>=300
assert meta['png_bytes']<=15*1024*1024
png=list(res.glob('ic_adapt_*.png'))
assert len(png)==meta['count']
assert sum(f.stat().st_size for f in png)==meta['png_bytes']
for k in ('matematicas','fisica','quimica','historia','social_studies','didactica','literatura','educacion','examen','parcial','practica','notas','general'):
    assert (res/('ic_adapt_'+k+'.png')).exists(),k
assert (src/'AdaptiveIconLibrary.java').exists()
assert (src/'ExamStore.java').exists()
assert (src/'SyllabusInterpreter.java').exists()
assert (src/'ExamActivity.java').exists()
assert (src/'SyllabusPdfReader.java').exists()
main=(src/'MainActivity.java').read_text();
for token in ('calendarPanel','HomeDashboard.show(this,body)','HomeDashboard.studyPlan(this,body)','HomeDashboard.selectedDateClasses(this,body,selectedDay)','"Mi guía"'):
    assert token in main,token
exam=(src/'ExamActivity.java').read_text()
for token in ('ExamStore.scheduleMatch','ACTION_OPEN_DOCUMENT','Revisar y completar','100 MB','start_import'):
    assert token in exam,token
ocr=(src/'SyllabusPdfReader.java').read_text()
for token in ('MAX_FILE=100L*1024L*1024L','TessBaseAPI','finally{if(tmp.exists()','PDDocument.load','result.ocrPages'):
    assert token in ocr,token
assert (r/'app/src/main/assets/tessdata/spa.traineddata').is_file()
assert 'versionCode 55' in (r/'app/build.gradle').read_text()
assert "versionName '3.12.0'" in (r/'app/build.gradle').read_text()
assert '.ExamActivity' in (r/'app/src/main/AndroidManifest.xml').read_text()
print('PASS 3.12.0: Home/Calendar/Study plan, exam review and persistence, course linking, %d adaptive PNGs (%d bytes), Tesseract model checked'%(len(png),meta['png_bytes']))
