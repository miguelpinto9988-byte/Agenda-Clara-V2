package pe.agendaclara.app;

import java.time.DateTimeException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Cautious offline extraction of academic dates. Unknown days are never guessed. */
public final class SyllabusEventParser {
    private SyllabusEventParser(){}
    private static final Pattern KIND=Pattern.compile(
        "(?iu)\\b(primer\\s+parcial|segundo\\s+parcial|tercer\\s+parcial|"+
        "parcial\\s*(?:[1-9]|[IVX]{1,4})?|examen(?:\\s+(?:final|parcial|sustitutorio))?|"+
        "evaluaci[oó]n|pr[aá]ctica\\s*(?:calificada)?|entrega(?:\\s+final)?|"+
        "trabajo\\s+final|proyecto\\s+final|sustentaci[oó]n)\\b");
    private static final Pattern NUM=Pattern.compile(
        "(?<!\\d)(\\d{1,2})[./-](\\d{1,2})[./-](\\d{2}|\\d{4})(?!\\d)");
    private static final Pattern WORD=Pattern.compile(
        "(?iu)\\b(\\d{1,2})\\s+(?:de\\s+)?"+
        "(enero|febrero|marzo|abril|mayo|junio|julio|agosto|setiembre|septiembre|"+
        "octubre|noviembre|diciembre)\\s+(?:de\\s+)?(\\d{4})\\b");
    private static final String[] MONTHS={
        "enero","febrero","marzo","abril","mayo","junio","julio","agosto",
        "septiembre","octubre","noviembre","diciembre"};

    public static final class Page {
        public final int number;
        public final String text;
        public Page(int number,String text){this.number=number;this.text=text==null?"":text;}
    }
    public static final class Event {
        public final String title,type,sourceText;
        public final LocalDate date; // null: user must resolve manually
        public final int page;
        public Event(String title,String type,LocalDate date,int page,String sourceText){
            this.title=title;this.type=type;this.date=date;this.page=page;
            this.sourceText=sourceText;
        }
        public boolean needsDate(){return date==null;}
    }
    private static int month(String text){
        String s=text.toLowerCase(Locale.ROOT);
        if(s.equals("setiembre"))s="septiembre";
        for(int i=0;i<MONTHS.length;i++)if(MONTHS[i].equals(s))return i+1;
        return 0;
    }
    public static LocalDate explicitDate(String text){
        if(text==null)return null;
        Matcher m=NUM.matcher(text);
        if(m.find())try{
            int year=Integer.parseInt(m.group(3));
            if(year<100)year+=2000;
            if(year<2000||year>2100)return null;
            return LocalDate.of(year,Integer.parseInt(m.group(2)),Integer.parseInt(m.group(1)));
        }catch(DateTimeException|NumberFormatException ignored){}
        m=WORD.matcher(text);
        if(m.find())try{
            int y=Integer.parseInt(m.group(3));
            return LocalDate.of(y,month(m.group(2)),Integer.parseInt(m.group(1)));
        }catch(DateTimeException|NumberFormatException ignored){}
        return null;
    }
    public static List<Event> extract(List<Page> pages){
        ArrayList<Event> found=new ArrayList<>();
        if(pages==null)return found;
        Set<String> dedupe=new HashSet<>();
        for(Page page:pages){
            if(page==null||page.text.isEmpty())continue;
            String[] lines=page.text.split("\\r?\\n");
            for(int i=0;i<lines.length;i++){
                String line=lines[i].trim().replaceAll("\\s+"," ");
                if(line.isEmpty()||line.length()>400)continue;
                Matcher label=KIND.matcher(line);
                if(!label.find())continue;
                LocalDate when=explicitDate(line);
                if(when==null && i+1<lines.length){
                    String following=lines[i+1].trim();
                    // Accept a next-line date only if the line is short and date-like.
                    if(following.length()<48)when=explicitDate(following);
                }
                String title=line.length()>130?line.substring(0,130):line;
                String kind=label.group(1);
                String key=AcademicCourseMatcher.fold(title)+"|"+(when==null?"?":when);
                if(!dedupe.add(key))continue;
                found.add(new Event(title,kind,when,page.number,line));
                if(found.size()>=100)return found;
            }
        }
        return found;
    }
}
