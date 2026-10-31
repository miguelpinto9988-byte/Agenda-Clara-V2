#!/usr/bin/env python3
"""Structural safety tests for photo OCR name matching and review controls."""
from pathlib import Path
import xml.etree.ElementTree as ET
P=Path('AgendaClara/app/src/main')
J=P/'java/pe/agendaclara/app'
act=(J/'ScheduleActivity.java').read_text(encoding='utf-8')
ocr=(J/'ScheduleOcr.java').read_text(encoding='utf-8')
review=(J/'SchedulePhotoReview.java').read_text(encoding='utf-8')
rec=(J/'ScheduleCourseRecognition.java').read_text(encoding='utf-8')
nav=(J/'MainActivity.java').read_text(encoding='utf-8')
nav=nav[nav.index('        nav=row();'):nav.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
assert 'SchedulePhotoReview.provisionalEstimate(detected.candidates)' in act
assert 'SchedulePhotoReview.uniqueBlocks(approved)' in act
assert 'new GradientDrawable(GradientDrawable.Orientation.TL_BR' in act
assert 'Sí · mismo curso' in act and 'No · separados' in act
assert 'R.drawable.ic_course_merge' in act and 'R.drawable.ic_course_separate' in act
assert 'setContentDescription("No, conservar como dos cursos distintos")' in act
assert 'setContentDescription("Sí, unir nombres en un curso' in act
assert 'confirmPhotoPairs(approved,confirmed,onComplete)' in act
assert 'ScheduleCourseRecognition.compare' in review
assert 'ScheduleCourseRecognition.preferred' in review
assert 'provisionalCount' in rec
assert 'GENERIC.contains(shortName)' in rec
assert 'se cambian sus días u horas' in act
assert 'Tendencias / Tendencias Educativas' in ocr
assert '"Cursos posibles: "' not in act  # label is written as text fragment in another literal
for drawable in ('ic_course_merge.xml','ic_course_separate.xml'):
    node=ET.parse(P/'res/drawable'/drawable).getroot()
    assert node.tag=='vector'
    assert len(node.findall('path'))>0
build=Path('AgendaClara/app/build.gradle').read_text(encoding='utf-8')
assert 'versionCode 37' in build and "versionName '3.9.6'" in build
print('PASS phase36 structure: guarded OCR proposals, yes/no pastel confirmations, no data loss, original navigation')
