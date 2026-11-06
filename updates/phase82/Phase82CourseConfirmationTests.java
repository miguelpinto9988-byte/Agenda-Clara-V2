package pe.agendaclara.app;
import java.util.*;
public final class Phase82CourseConfirmationTests {
    private static int checks=0;
    private static void yes(boolean v,String message){
        checks++;if(!v)throw new AssertionError(message);
    }
    private static ScheduleEntry e(String name,int day){
        ScheduleEntry s=new ScheduleEntry();
        s.course=name;s.day=day;s.start=480;s.end=540;return s;
    }
    private static void ask(String a,String b){
        yes(ScheduleCourseRecognition.compare(a,b)!=ScheduleCourseRecognition.Relation.DIFFERENT,
            "Debió preguntar: "+a+" | "+b);
    }
    public static void main(String[] args){
        ask("Investigación Educativa","Didáctica de Investigación");
        ask("Matemática Aplicada","Didáctica de Matemática");
        ask("Evaluación del Aprendizaje","Aprendizaje y Desarrollo");
        ask("Historia de la Educación","Teoría de la Educación");
        ask("Tendencias Educativas","Tendencias Tecnológicas");
        ask("Investigación Educativa","Investigacion Educatva");
        ask("Historia I","Historia II");
        ask("Historia (grupo 2)","Historia (grupo 3)");
        ask("Cálculo Numérico","Calculo numerico");
        yes(!ScheduleCourseRecognition.sharedWord("Historia de la Educación",
             "Teoría de la Educación").isEmpty(),"Palabra al final");
        yes(ScheduleCourseRecognition.compare("Didáctica de la ciencia",
             "Análisis de la literatura")==ScheduleCourseRecognition.Relation.DIFFERENT,
             "Solo conectores no justifican pregunta");
        yes(ScheduleCourseRecognition.compare("Programación avanzada",
             "Evaluación educativa")==ScheduleCourseRecognition.Relation.DIFFERENT,
             "Cursos sin términos compartidos");
        ArrayList<ScheduleEntry> three=new ArrayList<>(Arrays.asList(
            e("Ciencia Computacional",1),e("Arte Visual",2),
            e("Taller de Ciencia y Arte",3)));
        Set<String> resolved=new HashSet<>();
        SchedulePhotoReview.Pair first=SchedulePhotoReview.nextPair(
            three,Collections.emptySet(),resolved);
        yes(first!=null&&first.later==2,"Primera pregunta");
        SchedulePhotoReview.rememberDecision(three,first,resolved,false);
        SchedulePhotoReview.Pair second=SchedulePhotoReview.nextPair(
            three,Collections.emptySet(),resolved);
        yes(second!=null&&second.later==2&&second.earlier!=first.earlier,
            "Un NO no debe ocultar otras coincidencias");
        SchedulePhotoReview.rememberDecision(three,second,resolved,false);
        yes(SchedulePhotoReview.nextPair(three,Collections.emptySet(),resolved)==null,
            "Toda pareja revisada");
        ArrayList<ScheduleEntry> multiple=new ArrayList<>(Arrays.asList(
            e("Tendencias",1),e("Tendencias",3),
            e("Tendencias Educativas",4),e("Tendencias Educativas",5)));
        resolved.clear();
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(
            multiple,Collections.emptySet(),resolved);
        yes(pair!=null&&pair.exact,"Los nombres repetidos también preguntan");
        SchedulePhotoReview.rememberDecision(multiple,pair,resolved,true);
        SchedulePhotoReview.accept(multiple,pair);
        pair=SchedulePhotoReview.nextPair(multiple,Collections.emptySet(),resolved);
        yes(pair!=null&&!pair.exact,"Las otras lecturas siguen pendientes");
        SchedulePhotoReview.rememberDecision(multiple,pair,resolved,true);
        SchedulePhotoReview.acceptWithName(multiple,pair,"Tendencias Educativas");
        yes(SchedulePhotoReview.nextPair(multiple,Collections.emptySet(),resolved)==null,
            "No debe repetir preguntas resueltas");
        yes(SchedulePhotoReview.courseEstimate(multiple)==1&&multiple.size()==4,
            "Un curso, cuatro sesiones conservadas");
        ArrayList<ScheduleEntry> dup=new ArrayList<>(Arrays.asList(
            e("Historia",1),e("Historia",2)));
        resolved.clear();
        pair=SchedulePhotoReview.nextPair(dup,Collections.emptySet(),resolved);
        SchedulePhotoReview.rememberDecision(dup,pair,resolved,false);
        SchedulePhotoReview.reject(dup,pair);
        yes(dup.get(1).course.contains("grupo 2"),"Rechazo conserva grupos separados");
        yes(SchedulePhotoReview.nextPair(dup,Collections.emptySet(),resolved)==null,
            "Rechazo no debe iniciar bucle de confirmaciones");
        ArrayList<ScheduleEntry> imported=new ArrayList<>(Arrays.asList(
            e("Educación",1),e("Educación",3)));
        List<ScheduleEntry> stored=Arrays.asList(e("Educación",4),e("Educación (grupo 2)",5));
        SchedulePhotoReview.distinguishFromExisting(imported,stored,"Educación");
        yes(imported.get(0).course.equals("Educación (grupo 3)"),"Rechazo contra curso guardado");
        yes(imported.get(1).course.equals(imported.get(0).course),"Conservar todas las sesiones");
        ScheduleParser.Result primary=new ScheduleParser.Result();
        ScheduleParser.Result fallback=new ScheduleParser.Result();
        primary.candidates.add(e("Investigación Educativa",1));
        fallback.candidates.add(e("Investigacion Educatva",1));
        ScheduleParser.Result output=ScheduleOcrFusion.reconcile(
            primary,fallback,new ScheduleParser.Result());
        yes(output.candidates.size()==2,"No descartar error OCR silenciosamente");
        yes(output.reviewOnlyKeys.contains(ScheduleOcrFusion.key(fallback.candidates.get(0))),
            "Candidato adicional debe iniciar desmarcado");
        System.out.println("PASS: "+checks+" verificaciones de confirmación y fusión OCR");
    }
}
