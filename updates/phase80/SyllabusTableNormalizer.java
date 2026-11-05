package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Reconstructs well-delimited PDF/Word table rows only when the column header
 * identifies an evaluation and its week/date. Never borrows a neighbouring
 * evaluation's date. Raw rows with insufficient evidence are left unchanged.
 */
public final class SyllabusTableNormalizer {
    private SyllabusTableNormalizer() {}
    private static final Pattern SEPARATOR=Pattern.compile("\\s*\\|\\s*|\\t+| {3,}");
    private static final Pattern WEEK=Pattern.compile(
        "(?iu)^(?:semana\\s*)?([0-9]{1,2}|[IVXLCDM]{1,8})$");
    private static final Pattern DATE=Pattern.compile(
        "(?iu)^(?:\\d{1,2}[./-]\\d{1,2}(?:[./-]\\d{2,4})?|"+
        "\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\\s+de\\s+[a-záéíóú]+.*)$");

    public static List<SyllabusEventParser.Page> normalize(List<SyllabusEventParser.Page> pages) {
        ArrayList<SyllabusEventParser.Page> results=new ArrayList<>();
        if(pages==null)return results;
        for(SyllabusEventParser.Page page:pages){
            if(page==null)continue;
            String[] lines=page.text.split("\\r?\\n");
            StringBuilder output=new StringBuilder();
            int weekIndex=-1,activityIndex=-1,dateIndex=-1,columns=0;
            for(int i=0;i<lines.length;i++){
                String[] fields=split(lines[i]);
                if(isHeader(fields)){
                    columns=fields.length;
                    weekIndex=index(fields,"semana","semanas","sem");
                    activityIndex=index(fields,"evaluacion","actividad","evidencia",
                        "producto","examen","evaluaciones");
                    dateIndex=index(fields,"fecha","dia","plazo");
                    output.append(lines[i]).append('\n');
                    continue;
                }
                if(columns>=2 && fields.length==1 && i+columns<=lines.length &&
                    activityIndex>=0 && (weekIndex>=0||dateIndex>=0)){
                    String[] candidates=new String[columns];
                    boolean oneCellPerLine=true;
                    for(int k=0;k<columns;k++){
                        String[] single=split(lines[i+k]);
                        if(single.length!=1||single[0].isEmpty()){
                            oneCellPerLine=false;break;
                        }
                        candidates[k]=single[0];
                    }
                    if(oneCellPerLine && !SyllabusEventParser.assessmentType(
                        candidates[activityIndex]).isEmpty() &&
                        validContext(candidates,weekIndex,dateIndex)){
                        String merged=merge(candidates,weekIndex,activityIndex,dateIndex);
                        output.append(merged).append('\n');
                        i+=columns-1;
                        continue;
                    }
                }
                // Ordinary inline row: the parser already reads its cells.
                output.append(lines[i]).append('\n');
            }
            results.add(new SyllabusEventParser.Page(page.number,output.toString()));
        }
        return results;
    }
    private static boolean validContext(String[] fields,int week,int date){
        if(week>=0&&week<fields.length && WEEK.matcher(fields[week]).matches())return true;
        return date>=0&&date<fields.length&&isDateCell(fields[date]);
    }
    private static String merge(String[] cells,int week,int activity,int date){
        StringBuilder result=new StringBuilder(cells[activity].trim());
        if(week>=0&&week<cells.length){
            Matcher w=WEEK.matcher(cells[week]);
            if(w.matches())result.append(" | Semana ").append(w.group(1));
        }
        if(date>=0&&date<cells.length&&isDateCell(cells[date]))
            result.append(" | ").append(cells[date]);
        return result.toString();
    }
    private static boolean isDateCell(String value){
        if(DATE.matcher(value).matches())return true;
        SyllabusDateInterpreter.Temporal parsed=
            SyllabusDateInterpreter.interpret(value,null);
        return parsed.exact!=null||parsed.rangeStart!=null||parsed.week>0;
    }
    public static String[] split(String line){
        if(line==null)return new String[0];
        String[] raw=SEPARATOR.split(line.trim());
        for(int i=0;i<raw.length;i++)raw[i]=raw[i].trim();
        return raw;
    }
    private static int index(String[] fields,String... names){
        for(int i=0;i<fields.length;i++){
            String column=AcademicCourseMatcher.fold(fields[i]);
            for(String name:names)if(column.equals(name)||column.startsWith(name+" "))
                return i;
        }
        return -1;
    }
    private static boolean isHeader(String[] fields){
        return fields.length>=2 &&
            index(fields,"evaluacion","actividad","evidencia","producto","examen")>=0 &&
            index(fields,"semana","semanas","sem","fecha","dia","plazo")>=0;
    }
}
