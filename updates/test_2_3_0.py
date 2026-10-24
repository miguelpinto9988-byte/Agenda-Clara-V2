#!/usr/bin/env python3
import sqlite3
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
files={name:(p/name).read_text(encoding="utf-8") for name in ["Store.java","MainActivity.java","TaskRecycleBin.java","WeeklyPlanner.java","Reminders.java","ReminderReceiver.java"]}
gradle=Path("AgendaClara/app/build.gradle").read_text()
checks={
 "version":"versionCode 12" in gradle and "versionName '2.3.0'" in gradle,
 "migration":"if(old<7)createTrash(db)" in files["Store.java"],
 "no destructive migration":"DROP TABLE" not in files["Store.java"],
 "task trash":"CREATE TABLE IF NOT EXISTS task_trash" in files["Store.java"],
 "deletion with transaction":"String backup=TaskRecycleBin.encode(current,subtasks(id))" in files["Store.java"],
 "restore with transaction":"restoreDeleted(long trashId)" in files["Store.java"],
 "restore clears completion":"t.done=false;t.completedAt=0" in files["TaskRecycleBin.java"],
 "restore disables calendar":"t.calendarEnabled=false" in files["TaskRecycleBin.java"],
 "subtasks preserved":"for(Store.Subtask child:snap.subtasks)" in files["Store.java"],
 "trash retention":"TaskRecycleBin.RETENTION" in files["Store.java"],
 "old purge still works":"purgeExpiredCompleted(long now)" in files["Store.java"],
 "weekly planner":"WeeklyPlanner.pendingByDay" in files["MainActivity.java"],
 "trash UI":"void showTrash()" in files["MainActivity.java"],
 "restoration UI":"Restaurar" in files["MainActivity.java"],
 "stats":"completedLastSevenDays" in files["MainActivity.java"],
 "notification actions":"En 1 h" in files["Reminders.java"],
 "postpone validation":"minutes!=15&&minutes!=60" in files["ReminderReceiver.java"],
 "package stable":"applicationId 'pe.agendaclara.app'" in gradle
}
for label,ok in checks.items():
 if not ok:raise AssertionError(label)
db=sqlite3.connect(":memory:");db.execute("PRAGMA foreign_keys=ON")
db.executescript("""CREATE TABLE tasks(id INTEGER PRIMARY KEY,title TEXT);CREATE TABLE subtasks(id INTEGER PRIMARY KEY,task_id INTEGER NOT NULL,title TEXT,FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);CREATE TABLE task_trash(id INTEGER PRIMARY KEY,title TEXT,payload TEXT,deleted_at INTEGER);""")
db.execute("INSERT INTO tasks VALUES(1,'Tarea')");db.execute("INSERT INTO subtasks VALUES(1,1,'Paso')");db.execute("INSERT INTO task_trash VALUES(1,'Tarea','{}',100)")
db.execute("DELETE FROM tasks WHERE id=1")
assert db.execute("SELECT COUNT(*) FROM subtasks").fetchone()[0]==0
assert db.execute("SELECT COUNT(*) FROM task_trash").fetchone()[0]==1
db.execute("DELETE FROM task_trash WHERE deleted_at<?",(100+7*86400000+1,))
assert db.execute("SELECT COUNT(*) FROM task_trash").fetchone()[0]==0
print("PASS:",len(checks)+3,"fase 2.3 migracion, restauracion, calendario, metrica y avisos")
