#!/usr/bin/env python3
"""Agenda Clara 2.6.1: apply audited timetable improvements on top of 2.6.0."""
import base64,hashlib,io,lzma,subprocess,tarfile
from pathlib import Path
root=Path("AgendaClara")
encoded=Path("updates/phase11/payload.b64.txt").read_text(encoding="utf-8").strip()
digest=hashlib.sha256(encoded.encode()).hexdigest()
if digest!="b824ba6ab947e13c02bd4ef44269c272390be0a1e546964fb3fb3c7ea845b92c":
    raise RuntimeError("El paquete del parche 2.6.1 no coincide con el original.")
bundle=lzma.decompress(base64.b64decode(encoded))
if hashlib.sha256(bundle).hexdigest()!="81994988f8fd3cb3237430610b03cc62919de8ac1a45ae280fd7eee06b71ce51":
    raise RuntimeError("Archivo comprimido dañado.")
archive=tarfile.open(fileobj=io.BytesIO(bundle))
base=root/"app/src/main/java/pe/agendaclara/app"
for name in ("ScheduleConflict.java","SchedulePeriod.java","ScheduleBackup.java","SchedulePhotoLoader.java"):
    dest=base/name
    if dest.exists():raise RuntimeError("No se sobrescribirá el código existente: "+name)
    content=archive.extractfile(name).read()
    dest.write_bytes(content)
    print("Instalado",name,len(content))
update=subprocess.run(["patch","--batch","-p1"],cwd=root,input=archive.extractfile("schedule.patch").read(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if update.returncode!=0:raise RuntimeError(update.stdout.decode(errors="replace"))
gradle=root/"app/build.gradle"
source=gradle.read_text(encoding="utf-8")
if source.count("versionCode 15")!=1 or source.count("versionName '2.6.0'")!=1:
    raise RuntimeError("La actualización requiere el código fuente Agenda Clara 2.6.0")
gradle.write_text(source.replace("versionCode 15","versionCode 16").replace("versionName '2.6.0'","versionName '2.6.1'"),encoding="utf-8")
# Hotfix: close ternary wrapper in the diagnostics display expression.
reminderFile=base/"ScheduleReminders.java"
source=reminderFile.read_text(encoding="utf-8")
old='java.util.Locale.forLanguageTag("es-PE")));'
new='java.util.Locale.forLanguageTag("es-PE"))));'
if source.count(old)!=1:raise RuntimeError("Diagnostics formatting anchor changed")
reminderFile.write_text(source.replace(old,new,1),encoding="utf-8")
print("Agenda Clara 2.6.1 aplicada: respaldo, conflictos, cuadrícula, avisos y fotos optimizadas.")
