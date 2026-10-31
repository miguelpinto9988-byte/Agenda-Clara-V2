#!/usr/bin/env python3
from pathlib import Path
S=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def java(name):return (S/name).read_text(encoding="utf-8")
w=java("WindowLayout.java")
assert "previousHeight[0]=max;" in w and "WindowManager.LayoutParams.WRAP_CONTENT" in w
assert "removeOnGlobalLayoutListener" in w
assert "decor.requestLayout()" in w
dial=java("ModernPickers.java")
assert "final TextView[] dialCells=new TextView[13]" in dial
assert "if(dialCells[1]==null)" in dial
assert "dial.removeAllViews();" not in dial
assert "lastHighlighted[0]!=hour[0]" in dial
main=java("MainActivity.java")
assert 'Store.get(this).scanState(chat.key,"Solicitando "+choice[0]+" mensajes anteriores…");' in main
assert 'if(!Prefs.get(this).getBoolean("wa_connected",false)||!WhatsAppSessionService.running)' in main
assert "Settings.ACTION_APP_NOTIFICATION_SETTINGS" in main
assert "Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM" in main
session=java("WhatsAppSessionService.java")
assert 'void requestHistory(String action,String jid,int count)throws Exception' in session
assert 'Store.linkedKey(jid)' in session and '!chat.selected||!chat.joined' in session
assert 'WhatsAppNative.call(req);' in session
assert 'db.scanState(key,"Error al recuperar mensajes.' in session
flow=java("ReviewFlow.java")
assert "db.withdrawMissing(chatKey,ids,origins)" not in flow
reminders=java("Reminders.java")
assert "channel.getImportance()!=NotificationManager.IMPORTANCE_NONE" in reminders
assert "public static void acknowledge" in reminders
assert ".setSilent(true)" in reminders
receiver=java("ReminderReceiver.java")
assert 'Reminders.acknowledge(c,t,"Tarea completada")' in receiver
assert 'Reminders.acknowledge(c,t,"Aviso pospuesto "+minutes+" minutos")' in receiver
schedule=java("ScheduleReminders.java")
assert '"En 10 min",again' in schedule and '"Ver horario",click' in schedule
class_receiver=java("ScheduleAlarmReceiver.java")
assert "SCHEDULE_SNOOZE_DELIVER" in class_receiver and "if(!snoozed)ScheduleReminders.schedule(c,s);" in class_receiver
nav=main[main.index('        nav=row();'):main.index('        View line=new View(this);')]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
assert 'versionCode 41' in Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert "versionName '3.10.0'" in Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
print("PASS phase40: history connection/permission/progress, size restoration, fast time picker, task/class alarm feedback, nav unchanged")
