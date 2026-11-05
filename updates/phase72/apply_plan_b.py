#!/usr/bin/env python3
"""Entrega B: add manual/voice routing and PDF/DOC/DOCX syllabus import. SOURCE ONLY.
Run after: python3 updates/phase71/apply_plan_a.py
Never runs Gradle, Android build, emulator or signs/publishes an APK.
"""
from pathlib import Path
import shutil
from patch_task_routing import main_editor,voice_editor

ROOT=Path("AgendaClara/app/src/main")
JAVA=ROOT/"java/pe/agendaclara/app"
HERE=Path(__file__).resolve().parent
FILES=("AcademicCourseMatcher.java","AcademicTaskLinks.java","AcademicCourseRouting.java",
       "SyllabusEventParser.java","SyllabusDocumentReader.java","SyllabusImportActivity.java")

def one(src,old,new,label):
    if src.count(old)==1:return src.replace(old,new,1)
    if old not in src and new in src:return src
    raise RuntimeError("Entrega B: anclaje incompatible en "+label)

def run():
    manifest=ROOT/"AndroidManifest.xml"
    gradle=Path("AgendaClara/app/build.gradle")
    main=JAVA/"MainActivity.java"
    voice=JAVA/"VoiceQuickTask.java"
    panel=JAVA/"CalendarStudyPanel.java"
    profiles=JAVA/"AcademicSchedules.java"
    for path in (manifest,gradle,main,voice,panel,profiles):
        if not path.is_file():raise RuntimeError("Fuentes de Entrega A no disponibles: "+str(path))
    for name in FILES:
        staged=HERE/name
        dest=JAVA/name
        if not staged.is_file() or (dest.exists() and dest.read_bytes()!=staged.read_bytes()):
            raise RuntimeError("Archivo de Entrega B ausente o en conflicto: "+name)
    main_text=main_editor(main.read_text(encoding="utf-8"))
    voice_text=voice_editor(voice.read_text(encoding="utf-8"))
    panel_text=panel.read_text(encoding="utf-8")
    panel_text=one(panel_text,
        '''        exams.addView(a.text("Importación de sílabos, exámenes y recordatorios: Entrega B.",
                12,MUTED,false));''',
        '''        exams.addView(a.button("Subir sílabo · PDF, DOC o DOCX",
                ()->a.startActivity(new Intent(a,SyllabusImportActivity.class))));''',
        "panel importar sílabo")
    panel_text=one(panel_text,
        '''        exams.addView(a.text("Los cursos registrados aquí estarán disponibles para elegir al crear evaluaciones.",
                13,MUTED,false));''',
        '''        exams.addView(a.button("Agregar examen o entrega manualmente",()->{
            Intent intent=new Intent(a,SyllabusImportActivity.class);
            intent.putExtra("manual",true);
            a.startActivity(intent);
        }));
        exams.addView(a.text("Los exámenes confirmados crearán tareas en el curso elegido.",
                13,MUTED,false));''',
        "panel exámenes manuales")
    profile_text=profiles.read_text(encoding="utf-8")
    profile_text=one(profile_text,
        '        ScheduleDatabase.get(c).deleteProfile(id);',
        '        ScheduleDatabase.get(c).deleteProfile(id);\n        AcademicTaskLinks.get(c).clearProfile(id);',
        "eliminación segura de vínculos de curso")
    manifest_text=manifest.read_text(encoding="utf-8")
    manifest_text=one(manifest_text,
        '<activity android:name=".ScheduleActivity" android:exported="false"',
        '<activity android:name=".SyllabusImportActivity" android:exported="false" '
        'android:theme="@style/AppTheme" android:windowSoftInputMode="adjustResize" />\n'
        '        <activity android:name=".ScheduleActivity" android:exported="false"',
        "registrar actividad de sílabos")
    gradle_text=gradle.read_text(encoding="utf-8")
    if "versionCode 59" not in gradle_text or "versionName '3.13.3'" not in gradle_text:
        raise RuntimeError("Versión base 3.13.3 requerida; NO compilar")
    gradle_text=one(gradle_text,
        "    implementation 'com.google.mlkit:text-recognition:16.0.1'",
        "    implementation 'com.google.mlkit:text-recognition:16.0.1'\n"
        "    implementation 'com.tom-roush:pdfbox-android:2.0.27.0'\n"
        "    implementation 'org.apache.poi:poi-scratchpad:5.4.1'",
        "dependencias de lectura de documentos")
    # Write only after all validations and transformations have succeeded.
    for name in FILES:shutil.copyfile(HERE/name,JAVA/name)
    main.write_text(main_text,encoding="utf-8")
    voice.write_text(voice_text,encoding="utf-8")
    panel.write_text(panel_text,encoding="utf-8")
    profiles.write_text(profile_text,encoding="utf-8")
    manifest.write_text(manifest_text,encoding="utf-8")
    gradle.write_text(gradle_text,encoding="utf-8")
    print("PASS Entrega B: tareas manuales/voz vinculables a cursos confirmados")
    print("PASS Entrega B: importar PDF/DOC/DOCX, OCR PDF y fechas de evaluaciones")
    print("PASS Entrega B: 10 días y 12 horas o 7 días, revisión antes de guardar")
    print("NO APK: las dependencias y la compilación se validarán en Entrega C")

if __name__=="__main__":run()
