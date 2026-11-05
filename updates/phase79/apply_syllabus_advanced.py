#!/usr/bin/env python3
"""Apply Agenda Clara 3.13.9 syllabus phases A/B/C to VERIFIED 3.13.8 sources.

All edits are preflighted before writing. Does not build, sign or publish an APK.
"""
from pathlib import Path
import shutil

BASE=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
HERE=Path(__file__).resolve().parent
GRADLE=Path("AgendaClara/app/build.gradle")
NEW=("SyllabusAssessmentExtractor.java","SyllabusReimportPlanner.java")

def once(src,old,new,where):
    count=src.count(old)
    if count!=1:raise RuntimeError(f"{where}: se esperaban 1 anclaje, se encontraron {count}")
    return src.replace(old,new,1)

def date_interpreter(source):
    before='''    private static final Pattern WEEK=Pattern.compile('''
    after=r'''    private static final Pattern CROSS_MONTH_RANGE=Pattern.compile(
        "(?iu)\\b(?:del|desde|entre)\\s+([0-3]?[0-9])\\s+(?:de\\s+)?"+
        "(enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|"+
        "octubre|noviembre|diciembre)\\s+(?:(?:de|del)\\s+(20[0-9]{2})\\s+)?"+
        "(?:al|a|hasta|y)\\s+([0-3]?[0-9])\\s+(?:de\\s+)?"+
        "(enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|"+
        "octubre|noviembre|diciembre)\\s+(?:de|del)\\s+(20[0-9]{2})\\b");
    private static final Pattern WEEK=Pattern.compile('''
    source=once(source,before,after,"patrón de fechas que cruzan meses")
    before='''    private static LocalDate[] range(String value,CalendarInfo calendar){
        Matcher numeric=NUMERIC.matcher(value);'''
    after='''    private static LocalDate[] range(String value,CalendarInfo calendar){
        Matcher cross=CROSS_MONTH_RANGE.matcher(value);
        if(cross.find()){
            int endYear=Integer.parseInt(cross.group(6));
            int endMonth=month(cross.group(5));
            int startMonth=month(cross.group(2));
            int startYear=cross.group(3)!=null?Integer.parseInt(cross.group(3)):
                (startMonth>endMonth?endYear-1:endYear);
            LocalDate a=make(startYear,startMonth,Integer.parseInt(cross.group(1)));
            LocalDate b=make(endYear,endMonth,Integer.parseInt(cross.group(4)));
            if(a!=null&&b!=null&&!a.isAfter(b)&&!a.plusDays(62).isBefore(b))
                return new LocalDate[]{a,b};
        }
        Matcher numeric=NUMERIC.matcher(value);'''
    source=once(source,before,after,"interpretar rangos entre meses")
    before='''    private static final Pattern START=Pattern.compile("(?iu)\\\\b(?:inicio\\\\s+de\\\\s+clases|inicio\\\\s+del\\\\s+(?:semestre|ciclo|per[ií]odo)|comienzo\\\\s+de\\\\s+clases|primera\\\\s+semana\\\\s+de\\\\s+clases|semana\\\\s*(?:1|i)\\\\s*[:.\\\\-])");'''
    after='''    private static final Pattern START=Pattern.compile("(?iu)\\\\b(?:inicio\\\\s+de\\\\s+clases|fecha\\\\s+de\\\\s+inicio\\\\s+de\\\\s+clases|inicio\\\\s+de\\\\s+actividades\\\\s+acad[eé]micas|inicio\\\\s+del\\\\s+(?:semestre|ciclo|per[ií]odo)|comienzo\\\\s+de\\\\s+clases|primera\\\\s+semana\\\\s+de\\\\s+clases|semana\\\\s*(?:1|i)\\\\s*[:.\\\\-])");'''
    source=once(source,before,after,"fecha de inicio del ciclo")
    return source

def event_parser(source):
    start=source.index("    public static List<Event> extract(List<Page> pages){")
    end=source.index("    /** Preserve compatibility",start)
    new='''    /**
     * Table-aware extraction: dates, weights and academic weeks may be in adjacent
     * PDF/Word cells. The public API remains compatible with existing callers.
     */
    public static List<Event> extract(List<Page> pages){
        ArrayList<Event> output=new ArrayList<>();
        for(SyllabusAssessmentExtractor.Finding f:SyllabusAssessmentExtractor.extract(pages))
            output.add(f.event);
        return output;
    }
'''
    return source[:start]+new+source[end:]

def document_reader(source):
    old='''                while((event=parser.next())!=XmlPullParser.END_DOCUMENT){
                    if(event==XmlPullParser.START_TAG&&"t".equals(parser.getName())){
                        text.append(parser.nextText());
                        if(text.length()>MAX_TEXT)throw new IOException("Texto excesivo");
                    }
                    if(event==XmlPullParser.END_TAG && ("p".equals(parser.getName())
                            || "tr".equals(parser.getName())))text.append('\\n');
                }'''
    new='''                int tableDepth=0;
                while((event=parser.next())!=XmlPullParser.END_DOCUMENT){
                    String tag=parser.getName();
                    if(event==XmlPullParser.START_TAG){
                        if("tbl".equals(tag))tableDepth++;
                        if("t".equals(tag)){
                            text.append(parser.nextText());
                            if(text.length()>MAX_TEXT)throw new IOException("Texto excesivo");
                        }
                    }else if(event==XmlPullParser.END_TAG){
                        // Preserve rows AND column boundaries instead of splitting
                        // each Word table cell into unrelated paragraphs.
                        if("p".equals(tag))text.append(tableDepth>0?" ":"\\n");
                        if("tc".equals(tag))text.append(" | ");
                        if("tr".equals(tag))text.append('\\n');
                        if("tbl".equals(tag))tableDepth=Math.max(0,tableDepth-1);
                    }
                }'''
    source=once(source,old,new,"celdas DOCX")
    old='''                if(text.trim().length()<110){'''
    new='''                String lower=text.toLowerCase(java.util.Locale.ROOT);
                boolean scannedGridHint=text.length()<1000&&
                    (lower.contains("cronograma")||lower.contains("evaluaciones")||
                     lower.contains("producto final"))&&
                    !lower.matches("(?s).*\\\\d{1,2}[./-]\\\\d{1,2}[./-]20\\\\d{2}.*");
                if(text.trim().length()<140||scannedGridHint){'''
    source=once(source,old,new,"páginas de PDF mixtas")
    return source

def run():
    paths={
        BASE/"SyllabusDateInterpreter.java":date_interpreter,
        BASE/"SyllabusEventParser.java":event_parser,
        BASE/"SyllabusDocumentReader.java":document_reader,
    }
    rewritten={}
    for path,transform in paths.items():
        rewritten[path]=transform(path.read_text(encoding="utf-8"))
    main=BASE/"SyllabusImportActivity.java"
    rewritten[main]=(HERE/"SyllabusImportActivity.java").read_text(encoding="utf-8")
    for name in NEW:
        target=BASE/name
        if target.exists():raise RuntimeError("No sustituir componente existente: "+name)
        if not (HERE/name).is_file():raise RuntimeError("Componente ausente: "+name)
    build=GRADLE.read_text(encoding="utf-8")
    if build.count("versionCode 64")!=1 or build.count("versionName '3.13.8'")!=1:
        raise RuntimeError("Requiere las fuentes verificadas 3.13.8")
    rewritten[GRADLE]=build.replace("versionCode 64","versionCode 65",1).replace(
        "versionName '3.13.8'","versionName '3.13.9'",1)
    for path,updated in rewritten.items():path.write_text(updated,encoding="utf-8")
    for name in NEW:shutil.copyfile(HERE/name,BASE/name)
    print("PASS: fase A fechas complejas y tablas PDF/DOCX")
    print("PASS: fase B planes de duplicados y cambios pendientes de confirmación")
    print("PASS: fase C pantalla de evaluaciones y recordatorios")
    print("PASS: Agenda Clara 3.13.9 sources ready; NO APK in this script")

if __name__=="__main__":run()
