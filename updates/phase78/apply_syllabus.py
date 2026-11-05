#!/usr/bin/env python3
"""Agenda Clara 3.13.8 - syllabus-only source migration.
Run after extracting verified Agenda Clara 3.13.7 sources.
Imports only syllabus Java sources. Leaves existing timetables, categories and tasks intact.
"""
import base64
import io
import tarfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
NAMES={
    "SyllabusDateInterpreter.java",
    "SyllabusEventParser.java",
    "SyllabusCourseResolver.java",
    "SyllabusDocumentReader.java",
    "SyllabusImportActivity.java",
    "SyllabusAcademicTests.java",
}
def run():
    if not GRADLE.is_file():
        raise RuntimeError("Reconstruye primero las fuentes verificadas 3.13.7")
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 63")!=1 or gradle.count("versionName '3.13.7'")!=1:
        raise RuntimeError("Se requiere exactamente la versión 3.13.7; datos sin modificar")
    if not (JAVA/"AcademicCourseRouting.java").exists():
        raise RuntimeError("No se encontró la vinculación de cursos anterior")
    encoded=(HERE/"sources_b64.txt").read_text(encoding="ascii").strip()
    archive=base64.b64decode(encoded,validate=True)
    prepared={}
    with tarfile.open(fileobj=io.BytesIO(archive),mode="r:gz") as bundle:
        files=bundle.getmembers()
        if {item.name for item in files}!=NAMES:
            raise RuntimeError("Lista de fuentes de sílabos inesperada")
        for item in files:
            if not item.isfile() or item.size>100000:
                raise RuntimeError("Archivo inválido en el paquete académico")
            content=bundle.extractfile(item).read().decode("utf-8")
            if not content.startswith("package pe.agendaclara.app;"):
                raise RuntimeError("Archivo académico sin paquete de aplicación")
            if len(content)<800:raise RuntimeError("Fuente truncada: "+item.name)
            prepared[item.name]=content
    for name in NAMES:
        if name=="SyllabusAcademicTests.java":
            destination=HERE/name
        else:
            destination=JAVA/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text(prepared[name],encoding="utf-8")
    GRADLE.write_text(gradle.replace("versionCode 63","versionCode 64",1)
                            .replace("versionName '3.13.7'","versionName '3.13.8'",1),
                      encoding="utf-8")
    print("PASS: sílabos 3.13.8 instalados sin cambiar bases de datos existentes")
    print("PASS: exámenes, trabajos/productos finales, semanas y curso por perfil")
    print("PASS: eventos sin día exacto = tarea sin vencimiento ni aviso inventado")
if __name__=="__main__":run()
