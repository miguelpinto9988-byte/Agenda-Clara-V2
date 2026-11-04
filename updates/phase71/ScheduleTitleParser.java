package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Conservative header-only schedule name suggestion from on-device OCR. */
public final class ScheduleTitleParser {
    private static final Pattern LABEL=Pattern.compile(
        "(?iu)^(?:horario(?:\\s+(?:acad[eé]mico|de\\s+clases))?|ciclo|semestre)\\s*[:—–-]\\s*(.+)$");
    private static final Pattern DIRECT=Pattern.compile(
        "(?iu)^horario\\s+((?!de\\s+clases$|acad[eé]mico$).{3,80})$");
    private static final Pattern DAY=Pattern.compile(
        "(?iu)\\b(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\\b");
    private ScheduleTitleParser(){}

    public static String suggest(String raw){
        if(raw==null||raw.trim().isEmpty())return "";
        String[] lines=raw.split("\\r?\\n");
        int max=Math.min(lines.length,14);
        for(int i=0;i<max;i++){
            String line=lines[i].trim().replaceAll("\\s+"," ");
            Matcher m=LABEL.matcher(line);
            if(!m.matches())m=DIRECT.matcher(line);
            if(!m.matches())continue;
            String value=m.group(1).trim();
            if(value.length()<3||value.length()>90)continue;
            if(DAY.matcher(value).find()||value.matches("(?s).*\\d{1,2}[:.]\\d{2}.*"))continue;
            if(value.matches("(?iu)^(?:de\\s+clases|acad[eé]mico|mis\\s+cursos)$"))continue;
            return value;
        }
        return "";
    }
}
