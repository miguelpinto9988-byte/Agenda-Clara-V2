package pe.agendaclara.app;

import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/** Local, deterministic suggestions. No automatic destination is ever committed. */
public final class AcademicCourseMatcher {
    private AcademicCourseMatcher() {}
    public static final class Course {
        public final String profileId, category, name;
        public Course(String profileId, String category, String name) {
            this.profileId=profileId;this.category=category;this.name=name;
        }
    }
    public static final class Match {
        public final Course course;
        public final int score;
        Match(Course course,int score) {this.course=course;this.score=score;}
    }
    private static final Set<String> GENERIC=new HashSet<>(Arrays.asList(
            "curso","cursos","educacion","estudio","estudios","taller","general",
            "practica","practicas","examen","parcial","trabajo","presentacion",
            "proyecto","actividad","actividades","semestre","universidad","el","la",
            "los","las","para","con","del","de","y","por","una","uno","un"));

    public static String fold(String raw) {
        if(raw==null)return "";
        return Normalizer.normalize(raw,Normalizer.Form.NFD).replaceAll("\\p{M}+","")
                .toLowerCase(Locale.ROOT).replaceAll("[^a-z0-9]+"," ")
                .trim().replaceAll("\\s+"," ");
    }
    public static List<Match> matches(String text,List<Course> catalog) {
        String phrase=fold(text);
        ArrayList<Match> found=new ArrayList<>();
        if(phrase.isEmpty()||catalog==null)return found;
        String padded=" "+phrase+" ";
        List<String> words=Arrays.asList(phrase.split(" "));
        Set<String> seen=new HashSet<>();
        for(Course c:catalog) {
            if(c==null||c.profileId==null||c.profileId.isEmpty()
                    ||c.name==null||c.name.trim().isEmpty())continue;
            String title=fold(c.name);
            String id=c.profileId+"|"+title;
            if(title.isEmpty()||!seen.add(id))continue;
            int score=0, matched=0;
            if(padded.contains(" "+title+" "))score=100;
            for(String token:title.split(" ")) {
                if(token.length()<5||GENERIC.contains(token))continue;
                if(padded.contains(" "+token+" ")) {matched++;score+=30;}
                else {
                    for(String word:words) {
                        if(word.length()>=6 && token.startsWith(word)) {
                            score+=12;break;
                        }
                    }
                }
            }
            if(matched>=2)score+=20;
            if(score>0)found.add(new Match(c,score));
        }
        Collections.sort(found,new Comparator<Match>() {
            public int compare(Match a,Match b) {
                int score=Integer.compare(b.score,a.score);
                if(score!=0)return score;
                int name=a.course.name.compareToIgnoreCase(b.course.name);
                return name!=0?name:a.course.profileId.compareTo(b.course.profileId);
            }
        });
        if(found.size()>10)return new ArrayList<>(found.subList(0,10));
        return found;
    }
}
