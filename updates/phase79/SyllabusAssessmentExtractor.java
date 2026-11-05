package pe.agendaclara.app;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Conservative academic timeline extraction from PDF/Word table cells.
 * Dates/weeks may be in adjacent rows. Never invent an exact date from a week.
 */
public final class SyllabusAssessmentExtractor {
    private SyllabusAssessmentExtractor(){}
    private static final Pattern WEIGHT=Pattern.compile(
        "(?<![\\d])([1-9]\\d?|100)(?:[.,](\\d{1,2}))?\\s*%(?!\\d)");
    private static final Pattern WEEKDAY=Pattern.compile(
        "(?iu)\\b(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\\b");
    private static final Pattern HEADER=Pattern.compile(
        "(?iu)\\b(?:semana(?:s)?|sem\\.|evaluaci[oó]n|fecha|cronograma|"+
        "actividad|producto|evidencia|entregable|ponderaci[oó]n)\\b");
    private static final Pattern DATE_WORD=Pattern.compile(
        "(?iu)\\b(?:del\\s+\\d|desde\\s+\\d|hasta\\s+\\d|\\d{1,2}\\s+de\\s+"+
        "(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"+
        "setiembre|octubre|noviembre|diciembre))\\b");
    private static final Pattern YEAR=Pattern.compile("\\b20\\d{2}\\b");

    public static final class Finding {
        public final SyllabusEventParser.Event event;
        public final double weight;
        public final LocalDate suggestedDay;
        public final String dateBasis;
        Finding(SyllabusEventParser.Event e,double w,LocalDate date,String basis) {
            event=e;weight=w;suggestedDay=date;dateBasis=basis;
        }
    }
    private static String normalized(String value){
        return value==null?"":value.trim().replaceAll("\\s+"," ");
    }
    private static String fold(String value){return AcademicCourseMatcher.fold(value);}
    private static boolean isDateCell(String value) {
        String input=normalized(value);
        if(input.isEmpty()||input.length()>110)return false;
        if(!SyllabusEventParser.assessmentType(input).isEmpty())return false;
        boolean hasDate=SyllabusDateInterpreter.date(input,0)!=null ||
            SyllabusDateInterpreter.weekNumbers(input)[0]>0 ||
            DATE_WORD.matcher(input).find();
        return hasDate && (input.length()<58 || HEADER.matcher(input).find());
    }
    private static boolean isWeightCell(String value) {
        String input=normalized(value);
        return input.length()<24 && WEIGHT.matcher(input).find();
    }
    public static double weight(String value){
        if(value==null)return -1;
        Matcher m=WEIGHT.matcher(value);
        if(!m.find())return -1;
        double valuePercent=Double.parseDouble(m.group(1)+
            (m.group(2)!=null?"."+m.group(2):""));
        return valuePercent<=100?valuePercent:-1;
    }
    private static String title(String value){
        String cleaned=normalized(value.replace('|',' ').replace('\t',' '));
        cleaned=cleaned.replaceAll("(?iu)\\b(?:fecha|semana|ponderaci[oó]n)\\s*[:=]\\s*"," ");
        return cleaned.length()>165?cleaned.substring(0,165):cleaned;
    }
    private static boolean generic(String value){
        String low=fold(value);
        return (low.startsWith("el examen ")||low.startsWith("los examenes ")||
                low.startsWith("la evaluacion "))&&
                (low.contains("consiste en")||low.contains("se realizara")||
                 low.contains("se evaluara")) &&
                SyllabusDateInterpreter.date(value,0)==null &&
                SyllabusDateInterpreter.weekNumbers(value)[0]==0;
    }
    private static String adjacent(String[] lines,int index) {
        StringBuilder out=new StringBuilder();
        // Table layouts: the nearest NEXT cell belongs to the assessment row.
        // Prefer it to an assessment weight/date from the PREVIOUS row.
        for(int distance=1;distance<=3;distance++){
            int next=index+distance;
            if(next>=lines.length)break;
            String raw=normalized(lines[next]);
            if(!SyllabusEventParser.assessmentType(raw).isEmpty())break;
            // A new "Semana 13" heading AFTER the current row's weight
            // belongs to the NEXT evaluation, not this one.
            if(distance>1&&SyllabusDateInterpreter.weekNumbers(raw)[0]>0)break;
            if(isDateCell(raw)||isWeightCell(raw)){
                if(out.length()>0)out.append(" | ");
                out.append(raw);
            }else if(distance>1)break;
        }
        for(int distance=1;distance<=3;distance++) {
            int prev=index-distance;
            if(prev<0)break;
            String raw=normalized(lines[prev]);
            if(!SyllabusEventParser.assessmentType(raw).isEmpty())break;
            // A percentage on the preceding line normally closes the previous
            // assessment row. Never borrow its date/weight for this exam.
            if(isWeightCell(raw))break;
            if(isDateCell(raw)){
                if(out.length()>0)out.append(" | ");
                out.append(raw);
                if(SyllabusDateInterpreter.weekNumbers(raw)[0]>0)break;
            }else if(distance>1)break;
        }
        return out.toString();
    }
    private static DayOfWeek day(String text) {
        Matcher found=WEEKDAY.matcher(text);
        if(!found.find())return null;
        String name=fold(found.group(1));
        String[] values={"lunes","martes","miercoles","jueves","viernes","sabado","domingo"};
        for(int i=0;i<values.length;i++)if(values[i].equals(name))return DayOfWeek.of(i+1);
        return null;
    }
    private static LocalDate suggestion(String evidence,SyllabusDateInterpreter.Temporal period,
                                         SyllabusDateInterpreter.CalendarInfo calendar) {
        if(period.exact!=null||period.week==0||calendar==null||!calendar.anchored())
            return null;
        DayOfWeek weekday=day(evidence);
        if(weekday==null)return null;
        LocalDate first=calendar.weekStart(period.week);
        if(first==null)return null;
        LocalDate candidate=first.plusDays(weekday.getValue()-1);
        // Suggest a specific day only inside the stated academic week interval.
        return period.rangeStart!=null&&!candidate.isBefore(period.rangeStart)&&
            !candidate.isAfter(period.rangeEnd)?candidate:null;
    }
    private static String signature(SyllabusEventParser.Event event) {
        String normalized=fold(event.title)
            .replaceAll("\\b20\\d{2}\\b"," ")
            .replaceAll("\\b\\d{1,2}[./-]\\d{1,2}(?:[./-]\\d{2,4})?\\b"," ")
            .replaceAll("\\b\\d{1,2}\\s*%\\b"," ")
            .replaceAll("\\s+"," ").trim();
        String location=event.week>0?"w"+event.week+"-"+event.weekEnd:
            event.date!=null?"d"+event.date:
            event.windowStart!=null?"p"+event.windowStart+"-"+event.windowEnd:"?";
        return fold(event.type)+"|"+normalized+"|"+location;
    }
    public static List<Finding> extract(List<SyllabusEventParser.Page> pages) {
        ArrayList<Finding> out=new ArrayList<>();
        if(pages==null)return out;
        SyllabusDateInterpreter.CalendarInfo calendar=SyllabusDateInterpreter.calendar(pages);
        Map<String,Integer> dedup=new HashMap<>();
        for(SyllabusEventParser.Page page:pages){
            if(page==null||page.text.isEmpty())continue;
            String[] lines=page.text.split("\\r?\\n");
            int[] weekContext={0,0};int headingIndex=-100;
            for(int i=0;i<lines.length;i++){
                String line=normalized(lines[i]);
                if(line.isEmpty()||line.length()>600)continue;
                int[] weeks=SyllabusDateInterpreter.weekNumbers(line);
                if(weeks[0]>0&&line.length()<80&&
                        SyllabusEventParser.assessmentType(line).isEmpty()){
                    weekContext=weeks;headingIndex=i;
                }
                String type=SyllabusEventParser.assessmentType(line);
                if(type.isEmpty()||generic(line))continue;
                String suffix=adjacent(lines,i);
                String context=line+(suffix.isEmpty()?"":" | "+suffix);
                SyllabusDateInterpreter.Temporal temporal=
                    SyllabusDateInterpreter.interpret(context,calendar);
                if(temporal.exact==null&&temporal.rangeStart==null&&
                        headingIndex>=0&&i-headingIndex<=12&&weekContext[0]>0){
                    String week="Semana "+weekContext[0]+
                        (weekContext[1]>weekContext[0]?" a "+weekContext[1]:"");
                    temporal=SyllabusDateInterpreter.interpret(week,calendar);
                    context=week+" | "+context;
                }
                double percent=weight(context);
                LocalDate proposed=suggestion(context,temporal,calendar);
                SyllabusEventParser.Event event=new SyllabusEventParser.Event(
                    title(line),type,temporal.exact,temporal.rangeStart,temporal.rangeEnd,
                    temporal.week,temporal.weekEnd,page.number,line,context);
                String key=signature(event);
                Integer earlier=dedup.get(key);
                Finding candidate=new Finding(event,percent,proposed,
                    proposed==null?"":("Día inferido de la semana académica: "+proposed+
                        ". Debe confirmarse."));
                if(earlier!=null){
                    Finding previous=out.get(earlier);
                    int oldQuality=(previous.event.date!=null?3:
                        previous.event.windowStart!=null?2:0);
                    int newQuality=(event.date!=null?3:event.windowStart!=null?2:0);
                    if(newQuality>oldQuality)out.set(earlier,candidate);
                    continue;
                }
                dedup.put(key,out.size());out.add(candidate);
                if(out.size()>=100)return out;
            }
        }
        return out;
    }
}
