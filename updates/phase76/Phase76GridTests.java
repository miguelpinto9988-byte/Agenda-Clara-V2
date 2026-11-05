package pe.agendaclara.app;
import java.util.*;

/** Synthetic table: duplicate OCR rectangles must become visible warnings. */
public final class Phase76GridTests {
    public static void main(String[] args){
        List<ScheduleGridInterpreter.Line> lines=Arrays.asList(
            new ScheduleGridInterpreter.Line("Lunes",210,20,290,40),
            new ScheduleGridInterpreter.Line("Martes",505,20,585,40),
            new ScheduleGridInterpreter.Line("08:00 - 09:00",10,110,105,130),
            new ScheduleGridInterpreter.Line("09:00 - 10:00",10,230,105,250),
            new ScheduleGridInterpreter.Line("Investigación",215,110,290,130),
            new ScheduleGridInterpreter.Line("Investigación educativa",510,110,585,130)
        );
        List<ScheduleGridInterpreter.Tile> cells=Arrays.asList(
            new ScheduleGridInterpreter.Tile(190,100,310,140),
            new ScheduleGridInterpreter.Tile(190,100,310,140),
            new ScheduleGridInterpreter.Tile(480,100,610,140)
        );
        ScheduleParser.Result result=ScheduleGridInterpreter.parse(lines,cells,800,600);
        if(result.candidates.size()!=2)
            throw new AssertionError("Expected two subjects, got "+
                    result.candidates.size()+": "+result.uncertain);
        boolean warned=false;
        for(String warning:result.uncertain)
            if(warning.contains("Posible OCR duplicado"))warned=true;
        if(!warned)throw new AssertionError("Repeated OCR tile was silently discarded");
        System.out.println("PASS: Duplicate OCR rectangle is reported, not silently ignored");
    }
}
