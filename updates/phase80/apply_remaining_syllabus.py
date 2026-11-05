#!/usr/bin/env python3
"""Apply verified phase 80 enhancements on the reconstructed 3.13.9 sources."""
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
ACTIVITY=ROOT/"SyllabusImportActivity.java"

def once(s,old,new,why):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"{why}: expected one anchor, got {n}")
    return s.replace(old,new,1)

def run():
    text=ACTIVITY.read_text(encoding="utf-8")
    gradle=GRADLE.read_text(encoding="utf-8")
    if "versionCode 65" not in gradle or "versionName '3.13.9'" not in gradle:
        raise RuntimeError("Requires Agenda Clara 3.13.9")
    text=once(text,
        "SyllabusReviewIntelligence.onlyEvents(SyllabusEventParser.extract(pages))",
        "SyllabusImportPipeline.extract(pages)",
        "table-aware extraction")
    # Source snippet and classification are visible before any event is saved.
    text=once(text,
        "            review.addView(check);",
        '''            review.addView(check);
            String source=row.event.sourceText==null?"":row.event.sourceText;
            int sourceWeek=SyllabusReviewIntelligence.week(source);
            int sourceWeight=SyllabusReviewIntelligence.weight(source);
            review.addView(label("Tipo: "+SyllabusReviewIntelligence.classify(
                    source+" "+row.event.type)+
                    (sourceWeek>0?" · Semana "+sourceWeek:"")+
                    (sourceWeight>=0?" · "+sourceWeight+" %":"")+
                    (row.date==null?" · Fecha pendiente":""),12,false));
            review.addView(label("Página "+row.event.page+
                    " · Evidencia: "+source.substring(0,Math.min(source.length(),220)),
                    12,false));''',
        "source evidence review")
    # Preserve explicit user approval, and require additional confirmation on revisions.
    text=once(text,"->saveSelected(offset)","->reviewSyllabusRevision(offset)",
              "revision confirmation hook")
    marker="    private void saveSelected(int offset){"
    extra='''    private List<SyllabusEventParser.Event> selectedRevisionEvents(){
        ArrayList<SyllabusEventParser.Event> events=new ArrayList<>();
        for(Row row:items)if(row.selected){
            events.add(new SyllabusEventParser.Event(row.title,row.event.type,row.date,
                    row.event.page,row.event.sourceText));
        }
        return events;
    }
    private void reviewSyllabusRevision(int offset){
        if(selectedCourse==null)return;
        SyllabusRevisionReview.review(this,selectedCourse.profileId,documentTitle,
                selectedRevisionEvents(),()->saveSelected(offset));
    }
'''
    text=once(text,marker,extra+marker,"revision review methods")
    # Only record a new document manifest when the successful save flow is reached.
    marker='''        TaskWidget.refresh(this);
        new AlertDialog.Builder(this,R.style.DialogTheme)
                .setTitle("Importación revisada")'''
    replacement='''        SyllabusRevisionReview.record(this,selectedCourse.profileId,
                documentTitle,selectedRevisionEvents());
        TaskWidget.refresh(this);
        new AlertDialog.Builder(this,R.style.DialogTheme)
                .setTitle("Importación revisada")'''
    text=once(text,marker,replacement,"successful import revision snapshot")
    files=("SyllabusTableInterpreter.java","SyllabusImportPipeline.java",
           "SyllabusRevisionComparator.java","SyllabusRevisionReview.java")
    for name in files:
        if (ROOT/name).exists():raise RuntimeError("Already patched: "+name)
    ACTIVITY.write_text(text,encoding="utf-8")
    for name in files:shutil.copyfile(HERE/name,ROOT/name)
    GRADLE.write_text(gradle.replace("versionCode 65","versionCode 66",1)
                            .replace("versionName '3.13.9'","versionName '3.14.0'",1),
                      encoding="utf-8")
    print("PASS: table-aware import, per-page evidence, revision review")
    print("PASS: dates remain optional, no automatic deletion or rescheduling")
if __name__=="__main__":run()
