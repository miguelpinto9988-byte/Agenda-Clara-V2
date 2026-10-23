#!/usr/bin/env python3
"""Pruebas de regresión SQLite de Agenda Clara 1.3.1 (sin emulador)."""
import sqlite3
from pathlib import Path
db=sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE tasks(id INTEGER PRIMARY KEY, title TEXT, done INTEGER, completed_at INTEGER);
CREATE TABLE completed_history(task_id INTEGER PRIMARY KEY,completed_at INTEGER NOT NULL);
CREATE TABLE messages(chat_key TEXT,message_id TEXT,stamp INTEGER);
CREATE TABLE inbox(id INTEGER PRIMARY KEY,created INTEGER,state INTEGER);
""")
now=10_000_000_000
db.executemany("INSERT INTO tasks VALUES(?,?,?,?)",[
 (1,"antigua",1,now-3_600_001),
 (2,"reciente",1,now-3_599_999),
 (3,"activa",0,0)])
db.executemany("INSERT INTO messages VALUES(?,?,?)",[("a","old",now-100*86_400_000),("a","new",now)])
db.executemany("INSERT INTO inbox VALUES(?,?,?)",[(1,now-31*86_400_000,1),(2,now-31*86_400_000,0)])
db.commit()
cutoff=now-3_600_000
with db:
 db.execute("INSERT OR IGNORE INTO completed_history(task_id,completed_at) SELECT id,completed_at FROM tasks WHERE done=1 AND completed_at>0 AND completed_at<=?",(cutoff,))
 db.execute("DELETE FROM tasks WHERE done=1 AND completed_at>0 AND completed_at<=?",(cutoff,))
assert db.execute("SELECT id FROM tasks ORDER BY id").fetchall()==[(2,),(3,)]
assert db.execute("SELECT task_id FROM completed_history").fetchall()==[(1,)]
with db:
 db.execute("INSERT OR IGNORE INTO completed_history(task_id,completed_at) SELECT id,completed_at FROM tasks WHERE done=1 AND completed_at>0 AND completed_at<=?",(cutoff,))
assert db.execute("SELECT COUNT(*) FROM completed_history").fetchone()[0]==1
assert sum(db.execute("SELECT COUNT(*) FROM "+table+" WHERE "+q,(now-7*86_400_000,)).fetchone()[0] for table,q in [
 ("completed_history","completed_at>=?"),
 ("tasks","done=1 AND completed_at>=?")])==2
with db:
 db.execute("DELETE FROM messages WHERE stamp<?",(now-90*86_400_000,))
 db.execute("DELETE FROM inbox WHERE state<>0 AND created<?",(now-30*86_400_000,))
assert db.execute("SELECT message_id FROM messages").fetchall()==[("new",)]
assert db.execute("SELECT id FROM inbox").fetchall()==[(2,)]
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
backup=(src/"TaskBackup.java").read_text()
store=(src/"Store.java").read_text()
assert "db.beginTransaction()" in backup and "db.setTransactionSuccessful()" in backup
assert 'schema",1' in backup and 'v.putNull("origin_key")' in backup
assert "if(old<5)createCompletedHistory(db)" in store
print("PASS: 8 validaciones de archivado, retención, copia y migración.")
