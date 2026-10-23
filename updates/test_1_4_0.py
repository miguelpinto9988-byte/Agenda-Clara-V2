#!/usr/bin/env python3
"""Pruebas de regresión de esquema y capacidades 1.4 (sin datos personales)."""
import sqlite3
from pathlib import Path

project=Path("AgendaClara")
app=project/"app/src/main/java/pe/agendaclara/app"
db=sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys=ON")
# Simula tablas 1.3.1 y su migración 1.4.0
db.executescript("""
CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,notes TEXT NOT NULL,source TEXT NOT NULL,due INTEGER NOT NULL,created INTEGER NOT NULL,done INTEGER NOT NULL,urgent INTEGER NOT NULL,offsets TEXT NOT NULL,repeat_minutes INTEGER NOT NULL,duration INTEGER NOT NULL,event_id INTEGER NOT NULL,calendar_id INTEGER NOT NULL,calendar_enabled INTEGER NOT NULL,origin_key TEXT UNIQUE,completed_at INTEGER NOT NULL DEFAULT 0);
INSERT INTO tasks(title,notes,source,due,created,done,urgent,offsets,repeat_minutes,duration,event_id,calendar_id,calendar_enabled,completed_at) VALUES('Anterior','','manual',0,100,0,0,'60',0,60,-1,-1,0,0);
""")
db.execute("ALTER TABLE tasks ADD COLUMN category TEXT NOT NULL DEFAULT 'General'")
db.executescript("""
CREATE TABLE IF NOT EXISTS subtasks(id INTEGER PRIMARY KEY AUTOINCREMENT,task_id INTEGER NOT NULL,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);
CREATE INDEX IF NOT EXISTS subtasks_task ON subtasks(task_id);
""")
assert db.execute("SELECT category FROM tasks WHERE id=1").fetchone()==("General",)
db.execute("INSERT INTO subtasks(task_id,title,done) VALUES(1,'Leer',0)")
db.execute("INSERT INTO subtasks(task_id,title,done) VALUES(1,'Resumir',1)")
assert db.execute("SELECT count(*),sum(done) FROM subtasks WHERE task_id=1").fetchone()==(2,1)
db.execute("UPDATE subtasks SET done=1 WHERE task_id=1 AND id=1")
assert db.execute("SELECT sum(done) FROM subtasks WHERE task_id=1").fetchone()==(2,)
try:
    db.execute("INSERT INTO subtasks(task_id,title,done) VALUES(999,'Sin padre',0)")
except sqlite3.IntegrityError: pass
else: raise AssertionError("Se admitió subtarea huérfana")
db.execute("DELETE FROM tasks WHERE id=1")
assert db.execute("SELECT count(*) FROM subtasks").fetchone()[0]==0
assert "versionCode 7" in (project/"app/build.gradle").read_text()
assert "versionName '1.4.0'" in (project/"app/build.gradle").read_text()
task=(app/"Task.java").read_text()
assert 'category="General"' in task
code=(app/"Store.java").read_text()
assert "if(old<6)" in code and "createSubtasks(db)" in code
backup=(app/"TaskBackup.java").read_text()
assert '.put("schema",2)' in backup
assert "root.optInt(\"schema\",-1)!=1" in backup and 'root.optInt("schema",-1)!=2' in backup
assert "children.get(index)" in backup
ui=(app/"MainActivity.java").read_text()
assert "openSubtasks(long taskId)" in ui
assert "categoryFilter>0" in ui
assert "taskLimit+=24" in ui
print("PASS: 14 validaciones de migración, categorías, subtareas, backup, compatibilidad y paginación")
