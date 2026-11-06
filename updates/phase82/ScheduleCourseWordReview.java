package pe.agendaclara.app;
import java.util.*;
/** Una palabra significativa compartida exige confirmación humana. */
public final class ScheduleCourseWordReview {
    private ScheduleCourseWordReview(){}
    private static final Set<String> IGNORED=new HashSet<>(Arrays.asList(
        "de","del","la","las","el","los","y","e","en","un","una","unos",
        "unas","por","para","con","sin","a","al","o","u","su","sus",
        "se","que","ii","iii","iv","vi","vii","viii","ix",
        "curso","asignatura","clase","grupo"));
    private static String stem(String token){
        return token.length()>5&&token.endsWith("s")&&!token.endsWith("is")
            ?token.substring(0,token.length()-1):token;
    }
    private static Set<String> words(String title){
        LinkedHashSet<String> found=new LinkedHashSet<>();
        for(String token:ScheduleCourseColors.key(title).split(" ")){
            if(token.length()<3||IGNORED.contains(token)||token.matches("[0-9]+"))continue;
            found.add(stem(token));
        }
        return found;
    }
    public static String shared(String left,String right){
        Set<String> second=words(right);
        for(String token:words(left))if(second.contains(token))return token;
        return "";
    }
}
