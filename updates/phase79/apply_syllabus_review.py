#!/usr/bin/env python3
"""Phase 79, safe changes on the verified 3.13.8 reconstructed sources."""
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")

def replace_once(text, old, new, reason):
    if text.count(old)!=1:
        raise RuntimeError(f"{reason}: expected exactly one anchor, found {text.count(old)}")
    return text.replace(old,new,1)

def run():
    source=ROOT/"SyllabusImportActivity.java"
    if not source.is_file():raise RuntimeError("Missing 3.13.8 reconstructed sources")
    old=source.read_text(encoding="utf-8")
    text=old
    # Do not touch the document reader, profile database or old events.
    text=replace_once(text,
        "List<SyllabusEventParser.Event> extracted=SyllabusEventParser.extract(pages);",
        "List<SyllabusEventParser.Event> rawEvents=SyllabusEventParser.extract(pages);\n"
        "                List<SyllabusReviewIntelligence.Review> verified="
        "SyllabusReviewIntelligence.filter(rawEvents);\n"
        "                List<SyllabusEventParser.Event> extracted=new ArrayList<>();\n"
        "                for(SyllabusReviewIntelligence.Review candidate:verified)\n"
        "                    extracted.add(candidate.event);",
        "filter ordinary coursework before review")
    # The original source already displays source page; supplement it with
    # reliable metadata, but never imply a week is a specific due date.
    old_source='''            review.addView(label(row.event.page>0?"Fuente: página "+row.event.page:
                    "Fuente: texto del documento o registro manual",12,false));'''
    new_source='''            review.addView(label(row.event.page>0?"Fuente: página "+row.event.page:
                    "Fuente: texto del documento o registro manual",12,false));
            if(!"Registro manual".equals(row.event.sourceText)){
                String evidence=row.event.sourceText==null?"":row.event.sourceText;
                int academicWeek=SyllabusReviewIntelligence.week(evidence);
                int percentage=SyllabusReviewIntelligence.weight(evidence);
                String classification=SyllabusReviewIntelligence.classify(evidence+" "+row.event.type);
                review.addView(label("Tipo: "+classification+
                    (academicWeek>0?" · Semana "+academicWeek:"")+
                    (percentage>=0?" · Valor "+percentage+" %":"")+
                    (row.date==null?" · Fecha pendiente de confirmación":""),12,false));
                review.addView(label("Fragmento: "+evidence,12,false));
            }'''
    text=replace_once(text,old_source,new_source,"source evidence UI")
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 64")!=1 or gradle.count("versionName '3.13.8'")!=1:
        raise RuntimeError("Expected version 3.13.8 (64); abort without modifying sources")
    if (ROOT/"SyllabusReviewIntelligence.java").exists():
        raise RuntimeError("Phase 79 already applied")
    # Atomic preparation: validate all anchors before writing any file.
    source.write_text(text,encoding="utf-8")
    shutil.copyfile(HERE/"SyllabusReviewIntelligence.java",ROOT/"SyllabusReviewIntelligence.java")
    GRADLE.write_text(gradle.replace("versionCode 64","versionCode 65",1)
                            .replace("versionName '3.13.8'","versionName '3.13.9'",1),
                      encoding="utf-8")
    print("PASS: syllabus review limited to exams and final deliverables")
    print("PASS: week, weight, page and source evidence shown; no speculative date")
    print("PASS: user still confirms course, events and dates before persistence")
if __name__=="__main__":run()
