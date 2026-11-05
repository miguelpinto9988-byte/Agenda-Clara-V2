package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Reconstructs only well-delimited academic table rows, without joining unrelated weeks. */
public final class SyllabusTableNormalizer {
    private SyllabusTableNormalizer() {}
    private static final Pattern CELL_SEPARATOR=Pattern.compile("\\s*\\|\\s*|\\t+| {3,}");
    private static final Pattern WEEK_CELL=Pattern.compile("(?iu)^(?:semana\\s*)?([0-9]{1,2}|[IVXLCDM]{1,8})$");
    private static final Pattern DATE_CELL=Pattern.compile(
        "(?iu)^(?:\\d{1,2}[./-]\\d{1,2}(?:[./-]\\d{2,4})?|"+
        "\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\\s+de\\s+[a-záéíóú]+.*)$");

    public static List<SyllabusEventParser.Page> normalize(List<SyllabusEventParser.Page> pages){
        ArrayList<SyllabusEventParser.Page> out=new ArrayList<>();
        if(pages==null)return out;
        for(SyllabusEventParser.Page page:pages){
            if(page==null){continue;}
            String[] lines=page.text.split("\\r?\\n");
            StringBuilder extras=new StringBuilder();
            int weekColumn=-1,activityColumn=-1,dateColumn=-1;
            for(int i=0;i<lines.length;i++){
                String[] fields=split(lines[i]);
                if(fields.length<2)continue;
                if(isHeader(fields)){
                    weekColumn=index(fields,"semana","sem.");
                    activityColumn=index(fields,"evaluacion","actividad","evidencia","producto","examen");
                    dateColumn=index(fields,"fecha","dia");
                    continue;
                }
                if(activityColumn<0||activityColumn>=fields.length)continue;
                String activity=fields[activityColumn].trim();
                if(SyllabusEventParser.assessmentType(activity).isEmpty())continue;
                StringBuilder line=new StringBuilder(activity);
                if(weekColumn>=0&&weekColumn<fields.length){
                    Matcher week=WEEK_CELL.matcher(fields[weekColumn].trim());
                    if(week.matches())line.append(" | Semana ").append(week.group(1));
                }
                if(dateColumn>=0&&dateColumn<fields.length){
                    String value=fields[dateColumn].trim();
                    if(DATE_CELL.matcher(value).matches()||
                       SyllabusDateInterpreter.weekNumbers(value)[0]>0){
                        line.append(" | ").append(value);
                    }
                }
                String reconstructed=line.toString();
                // Source text stays present; only a bounded, evidenced second reading is added.
                if(reconstructed.length()>activity.length()+4 && reconstructed.length()<500
                        && !page.text.contains(reconstructed))
                    extras.append('\n').append(reconstructed);
            }
            // Do not add speculative rows on documents without recognizable columns.
            out.add(new SyllabusEventParser.Page(page.number,page.text+extras));
        }
        return out;
    }
    static String[] split(String line){
        if(line==null)return new String[0];
        String[] raw=CELL_SEPARATOR.split(line.trim());
        ArrayList<String> values=new ArrayList<>();
        for(String cell:raw)values.add(cell.trim());
        return values.toArray(new String[0]);
    }
    private static int index(String[] header,String... labels){
        for(int i=0;i<header.length;i++){
            String s=AcademicCourseMatcher.fold(header[i]);
            for(String label:labels)if(s.equals(label)||s.startsWith(label+" "))return i;
        }
        return -1;
    }
    private static boolean isHeader(String[] cells){
        return index(cells,"semana","sem.","fecha")>=0&&
                index(cells,"evaluacion","actividad","evidencia","producto","examen")>=0;
    }
}
