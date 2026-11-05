package pe.agendaclara.app;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/** Extracts assessments from table-like text without guessing missing dates. */
public final class SyllabusTableInterpreter {
    private SyllabusTableInterpreter(){}
    public static List<SyllabusEventParser.Event> extract(List<SyllabusEventParser.Page> pages){
        ArrayList<SyllabusEventParser.Event> result=new ArrayList<>();
        if(pages==null)return result;
        for(SyllabusEventParser.Page page:pages){
            if(page==null||page.text==null)continue;
            boolean inTable=false;
            for(String raw:page.text.split("\\r?\\n")){
                String line=raw.trim();
                if(line.isEmpty()){inTable=false;continue;}
                if(line.length()>500)continue;
                String[] cells=line.split("\\s*\\|\\s*|\\t+| {3,}");
                if(cells.length<2)continue;
                String lower=line.toLowerCase(Locale.ROOT);
                if((lower.contains("semana")||lower.contains("fecha")) &&
                        (lower.contains("actividad")||lower.contains("evaluaci")||
                         lower.contains("producto")) &&
                        SyllabusReviewIntelligence.classify(line).isEmpty()){
                    inTable=true;continue;
                }
                if(!inTable&&cells.length<3)continue;
                String kind=SyllabusReviewIntelligence.classify(line);
                if(kind.isEmpty())continue;
                LocalDate date=null;
                boolean conflictingDates=false;
                String title="";
                for(String cell:cells){
                    LocalDate found=SyllabusEventParser.explicitDate(cell);
                    if(found!=null){
                        if(date!=null&&!date.equals(found))conflictingDates=true;
                        else date=found;
                    }
                    if(!SyllabusReviewIntelligence.classify(cell).isEmpty() &&
                            cell.trim().length()>title.length())title=cell.trim();
                }
                if(conflictingDates)date=null;
                if(title.isEmpty())title=line;
                if(title.length()>130)title=title.substring(0,130);
                String evidence=line;
                if(cells.length>1 && cells[0].trim().matches("(?i)[0-9]{1,2}|[ivxlcdm]{1,8}"))
                    evidence="Semana "+cells[0].trim()+" | "+line;
                result.add(new SyllabusEventParser.Event(title,kind,date,page.number,evidence));
                if(result.size()>=150)return result;
            }
        }
        return result;
    }
}
