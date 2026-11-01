#!/usr/bin/env python3
"""Check voice-task source, privacy invariant, PNGs and Spanish command parser."""
from pathlib import Path
import subprocess,tempfile,struct
root=Path('AgendaClara')
src=root/'app/src/main/java/pe/agendaclara/app'
parser=(src/'QuickTaskVoiceParser.java').read_text(encoding='utf-8')
voice=(src/'VoiceQuickTask.java').read_text(encoding='utf-8')
menu=(src/'CreationChoices.java').read_text(encoding='utf-8')
manifest=(root/'app/src/main/AndroidManifest.xml').read_text()
gradle=(root/'app/build.gradle').read_text()
assert 'case "titulo":' in parser and 'case "fecha":' in parser and 'case "hora":' in parser
assert 'case "recordatorio":' in parser
assert 'scheduleOffsets' in parser and 'repeatMinutes' in voice and 'Reminders.schedule(activity,task)' in voice
assert 'TaskPriority.label' in voice and 'task.urgent=false' in voice
assert 'VoiceQuickTask.show(this)' in (src/'MainActivity.java').read_text()
assert 'Tarea rápida' in menu and 'Nueva nota' in menu and 'Nueva tarea' in menu
assert 'android.permission.RECORD_AUDIO' in manifest
assert "versionCode 47" in gradle and "versionName '3.10.6'" in gradle
assert 'vosk-android:0.3.75@aar' in gradle
for forbidden in ['MediaRecorder','FileOutputStream','getExternalStorageDirectory','AudioRecord.write','File.createTempFile']:
    assert forbidden not in voice, 'Audio must stay in memory: '+forbidden
for name in ['microphone','waveform','bell','check','calendar','clock']:
    png=root/'app/src/main/res/drawable-nodpi'/('ic_ref_voice_'+name+'.png')
    data=png.read_bytes()
    assert data.startswith(b'\x89PNG\r\n\x1a\n') and struct.unpack('>II',data[16:24])==(256,256)
tests=r'''
import java.time.*;
import pe.agendaclara.app.QuickTaskVoiceParser;
public final class VoiceCommandsTests {
    static void check(boolean result,String why){if(!result)throw new AssertionError(why);}
    public static void main(String[] args){
        LocalDate today=LocalDate.of(2026,11,1);
        QuickTaskVoiceParser.Result r=QuickTaskVoiceParser.parse(
            "título pagar la luz fecha 10 de octubre hora 4 de la tarde recordatorio cada 3 horas",today);
        check(r.title.equals("pagar la luz"),"title");
        check(r.date.equals(LocalDate.of(2027,10,10)),"next future 10 October");
        check(r.time.equals(LocalTime.of(16,0)),"four pm");
        check(r.repeatMinutes==180,"three-hour repeat");
        r=QuickTaskVoiceParser.parse("título entregar trabajo fecha mañana hora 9 a. m. recordatorio 2 horas antes",today);
        check(r.date.equals(today.plusDays(1)),"tomorrow");
        check(r.time.equals(LocalTime.of(9,0)),"nine am");
        check(r.beforeMinutes==120,"two hours before");
        r=QuickTaskVoiceParser.parse("título comprar papel fecha 31 de febrero hora 25:70",today);
        check(!r.validDate&&!r.validTime,"invalid date and time");
        r=QuickTaskVoiceParser.parse("título informe fecha pasado mañana hora 4 p. m. recordatorio cada dos horas",today);
        check(r.date.equals(today.plusDays(2)),"day after tomorrow");
        check(r.time.equals(LocalTime.of(16,0)),"spoken afternoon");
        check(r.repeatMinutes==120,"number words");
        r=QuickTaskVoiceParser.parse("título examen",today);
        check(r.title.equals("examen")&&r.date==null&&r.time==null,"title only allowed");
        System.out.println("PASS: Spanish voice parser and date/time/reminder grammar");
    }
}'''
with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp)/'VoiceCommandsTests.java';t.write_text(tests)
    subprocess.run(['javac','-encoding','UTF-8','-d',tmp,str(src/'QuickTaskVoiceParser.java'),str(t)],check=True)
    subprocess.run(['java','-cp',tmp,'VoiceCommandsTests'],check=True)
print("PASS: offline voice flow structure, ephemeral audio, 256px PNG assets, version 3.10.6")
