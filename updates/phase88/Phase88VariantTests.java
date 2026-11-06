package pe.agendaclara.app;

import java.util.ArrayList;
import java.util.List;

/** New variants must be suggested, not automatically imported or renamed. */
public final class Phase88VariantTests {
    private static void check(boolean ok,String message) {
        if(!ok)throw new AssertionError(message);
    }
    private static List<ScheduleAdaptiveRules.Rule> learn(List<ScheduleAdaptiveRules.Rule> history,
                                    String a,String b,boolean together,String canonical){
        return ScheduleAdaptiveRules.record(history,a,b,together,canonical,
            1000L+history.size());
    }
    private static void suggests(List<ScheduleAdaptiveRules.Rule> rules,
                                 String observed,String canonical){
        ScheduleAdaptiveVariants.Suggestion suggestion=
            ScheduleAdaptiveVariants.suggest(rules,observed);
        check(suggestion!=null,"Expected a proposal for "+observed);
        check(canonical.equals(suggestion.canonical),
            "Unexpected proposed course for "+observed+": "+suggestion.canonical);
    }
    private static void refuses(List<ScheduleAdaptiveRules.Rule> rules,String observed){
        check(ScheduleAdaptiveVariants.suggest(rules,observed)==null,
            "Unrequested or unsafe proposal for "+observed);
    }
    public static void main(String[] ignored) {
        List<ScheduleAdaptiveRules.Rule> history=new ArrayList<>();
        refuses(history,"Tendencas educativas");
        history=learn(history,"Tendencias","Tendencias educativas",true,
            "Tendencias educativas");
        suggests(history,"Tendencas educativas","Tendencias educativas");
        suggests(history,"Tendencias","Tendencias educativas");
        suggests(history,"Tendencias educativs","Tendencias educativas");
        refuses(history,"Tendencias educativas"); // Already the desired canonical name.
        refuses(history,"Tendencias tecnológicas");
        refuses(history,"Tutoría educativa");
        refuses(history,"Investigación educativa");
        refuses(history,"Tendencias educativas I"); // Unconfirmed module suffix.
        refuses(history,"Tendencias educativas (grupo 2)");
        refuses(history,"Tendencia"); // One-word fuzzy generalization is unsafe.
        history=learn(history,"Tendencas educativas","Tendencias educativas",
            false,"");
        refuses(history,"Tendencas educativas"); // Explicit rejection has priority.
        suggests(history,"Tendencias educativs","Tendencias educativas");
        history=learn(history,"Tendencas educativas","Tendencias educativas",
            true,"Tendencias educativas");
        suggests(history,"Tendencas educativas","Tendencias educativas");
        // Positive aliases are NOT chained into unapproved cross-course merges.
        List<ScheduleAdaptiveRules.Rule> levels=new ArrayList<>();
        levels=learn(levels,"Historia I","Historia parcial I",true,"Historia I");
        refuses(levels,"Historia II");
        refuses(levels,"Historia");
        refuses(levels,"Historia III");
        List<ScheduleAdaptiveRules.Rule> groups=new ArrayList<>();
        groups=learn(groups,"Investigación educativa (grupo 2)",
            "Investigacion educatíva (grupo 2)",true,
            "Investigación educativa (grupo 2)");
        refuses(groups,"Investigacion educativa (grupo 3)");
        refuses(groups,"Investigacion educativa"); // Missing explicit group.
        List<ScheduleAdaptiveRules.Rule> conflicting=new ArrayList<>();
        conflicting=learn(conflicting,"Didáctica educativa","Didactica educatíva",
            true,"Didáctica general");
        conflicting=learn(conflicting,"Didáctica educativa","Didactica evaluativa",
            true,"Didáctica aplicada");
        refuses(conflicting,"Didactica educativa"); // Two equally supported destinations.
        // Rejection remembered against exact observed/canonical pair overrides
        // other positive examples involving the same destination.
        List<ScheduleAdaptiveRules.Rule> veto=new ArrayList<>();
        veto=learn(veto,"Metodología educativa","Metodologia educatíva",
            true,"Metodología educativa");
        veto=learn(veto,"Metodologa educativa","Metodología educativa",false,"");
        refuses(veto,"Metodologa educativa");
        System.out.println("PASS: newly seen OCR spelling variants receive only an optional suggestion");
        System.out.println("PASS: educational adjectives alone do not create unrelated proposals");
        System.out.println("PASS: explicit rejection, I/II levels and class groups override inference");
        System.out.println("PASS: conflicting confirmed names fail closed without a suggestion");
    }
}