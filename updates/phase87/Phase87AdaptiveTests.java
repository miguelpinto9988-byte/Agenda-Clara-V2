package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/** Deterministic tests: learning requires user feedback, and can be undone. */
public final class Phase87AdaptiveTests {
    private static void check(boolean condition,String explanation){
        if(!condition)throw new AssertionError(explanation);
    }
    private static ScheduleAdaptiveRules.Rule find(List<ScheduleAdaptiveRules.Rule> history,
                                                    String a,String b){
        return ScheduleAdaptiveRules.find(history,a,b);
    }
    public static void main(String[] args){
        List<ScheduleAdaptiveRules.Rule> history=new ArrayList<>();
        check(find(history,"Tendencias","Tendencias educativas")==null,
            "No training from an unconfirmed OCR import");
        history=ScheduleAdaptiveRules.record(history,
            "Tendencias","Tendencias educativas",true,"Tendencias educativas",1000L);
        ScheduleAdaptiveRules.Rule learned=find(history,
            "TENDENCIAS EDUCATIVAS","tendéncias");
        check(learned!=null&&learned.together&&
              learned.canonical.equals("Tendencias educativas"),
              "Same pair should match case/diacritic changes in either order");
        check(ScheduleAdaptiveRules.canReuse(learned,"Tendencias","Tendencias educativas"),
            "Explicitly approved exact pair should be reusable");
        check(find(history,"Tutoría educativa","Investigación educativa")==null,
            "Never extrapolate a learned decision to unrelated names");
        check(!ScheduleAdaptiveRules.canReuse(learned,"Tutoría educativa","Investigación educativa"),
            "Learning must not act on an unseen pair");
        history=ScheduleAdaptiveRules.record(history,
            "Tendencias educativas","Tendencias",false,"",2000L);
        learned=find(history,"Tendencias","Tendencias educativas");
        check(learned!=null&&!learned.together&&learned.confirmations==2,
            "Later explicit separation must override an older merge");
        check(ScheduleAdaptiveRules.canReuse(learned,"Tendencias","Tendencias educativas"),
            "Previously rejected exact pair should prevent another repeated prompt");
        history=ScheduleAdaptiveRules.record(history,
            "Historia","Historia I",true,"Historia I",3000L);
        check(!ScheduleAdaptiveRules.canReuse(find(history,"Historia","Historia I"),
            "Historia","Historia I"),"Do not automatically merge an unqualified course with level I");
        history=ScheduleAdaptiveRules.record(history,
            "Historia I","Historia II",true,"Historia I",3000L);
        check(!ScheduleAdaptiveRules.canReuse(find(history,"Historia I","Historia II"),
            "Historia I","Historia II"),"Separate explicit course levels always take priority");
        history=ScheduleAdaptiveRules.record(history,
            "Matemática (grupo 2)","Matemática (grupo 3)",true,"Matemática",3000L);
        check(!ScheduleAdaptiveRules.canReuse(find(history,"Matemática (grupo 2)",
            "Matemática (grupo 3)"),"Matemática (grupo 2)","Matemática (grupo 3)"),
            "Do not merge distinct group labels, even with an older remembered decision");
        for(int i=0;i<ScheduleAdaptiveRules.MAX_RULES+25;i++){
            history=ScheduleAdaptiveRules.record(history,
                "Curso "+i,"Laboratorio "+i,false,"",4000L+i);
        }
        check(history.size()==ScheduleAdaptiveRules.MAX_RULES,
            "Adaptive history must have a hard upper bound");
        check(find(history,"Curso 104","Laboratorio 104")!=null,
            "Newer decisions remain when old history is trimmed");
        check(find(history,"Curso 0","Laboratorio 0")==null,
            "Oldest records expire to bound private storage");
        check(ScheduleAdaptiveRules.pairKey("A|B","C").equals(
            ScheduleAdaptiveRules.pairKey("C","A|B")),
            "Length-prefixed normalized pair keys must not depend on ordering");
        System.out.println("PASS: adaptive learning uses exact user-confirmed pairs only");
        System.out.println("PASS: a later separation overrides a previously accepted merge");
        System.out.println("PASS: protection of I/II levels, different groups and unrelated courses");
        System.out.println("PASS: repeat decisions, canonical name, finite private history");
    }
}