#!/usr/bin/env python3
"""Remove the confusing event-duration option from the New/Edit Task dialog.

Runs after the native phase22 design. Existing calendar event durations remain
stored for compatibility; new tasks continue to use Task.duration's safe
60-minute default internally when calendar integration is enabled. Reminders,
due time, task data and the approved header + button are not modified.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/java/pe/agendaclara/app"
MAIN=ROOT/"MainActivity.java"

def one(source,old,new,description):
    found=source.count(old)
    if found!=1:
        raise RuntimeError(f"phase23 {description}: expected exactly one anchor, found {found}")
    return source.replace(old,new,1)

def apply():
    java=MAIN.read_text(encoding="utf-8")
    plus=next((s for s in java.splitlines() if 'setTag("new_task_button")' in s),None)
    if not plus or "TopPlusButtonMotion.install(this)" not in java:
        raise RuntimeError("The approved plus button is missing")

    java=one(java,
        '        subtitle(advanced,"Duración del evento");\n'
        '        EditText duration=input("Duración en minutos",""+(draft!=null?draft.getInt("duration",60):t.duration),android.text.InputType.TYPE_CLASS_NUMBER);advanced.addView(duration);\n',
        '',"remove event-duration controls")
    java=one(java,
        'try{b.putInt("duration",Integer.parseInt(duration.getText().toString()));}catch(NumberFormatException e){b.putInt("duration",60);}restoreDraft=b;',
        'restoreDraft=b;', "remove duration from transient editor draft")
    java=one(java,
        '                int minutes;try{minutes=Integer.parseInt(duration.getText().toString());if(minutes<5||minutes>1440)throw new NumberFormatException();}catch(NumberFormatException e){duration.setError("Entre 5 y 1440 minutos.");return;}\n',
        '',"remove unnecessary duration validation")
    java=one(java,'t.duration=minutes;t.calendarEnabled=',
        't.calendarEnabled=',"preserve existing duration or internal default")

    # The user's agreed task workflow is still available.
    for required in ('"Hora límite · "','Reminders.schedule(this,t)',
                     't.repeatMinutes=intervals[repeat.getSelectedItemPosition()]',
                     't.calendarEnabled=google.isChecked()&&schedule.isChecked()'):
        if required not in java:raise RuntimeError("Expected unaffected functionality missing: "+required)
    if next((s for s in java.splitlines() if 'setTag("new_task_button")' in s),None)!=plus:
        raise RuntimeError("The approved header plus changed")
    MAIN.write_text(java,encoding="utf-8")
    print("PASS phase23: event-duration field and its validation removed; due dates, reminders and calendar link retained")

if __name__=="__main__":
    apply()
