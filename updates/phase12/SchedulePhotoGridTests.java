import pe.agendaclara.app.*;
import java.util.*;
/** Positional fixture: blocks and labels measured in the supplied 1536x1086 schedule.
 * Text lines are manually annotated: this checks interpretation, NOT ML Kit accuracy.
 */
public final class SchedulePhotoGridTests {
 static int checks;
 static void ok(boolean good,String label){checks++;if(!good)throw new AssertionError(label);}
 static void label(List<ScheduleGridInterpreter.Line> all,String text,int x,int y,int w){
   all.add(new ScheduleGridInterpreter.Line(text,x,y-11,x+w,y+12));
 }
 static void cell(List<ScheduleGridInterpreter.Line> lines,List<ScheduleGridInterpreter.Tile> tiles,
                  int x,int y,int right,int bottom,String text){
   tiles.add(new ScheduleGridInterpreter.Tile(x,y,right,bottom));
   String[] parts=text.split("\\|");int gap=(bottom-y)/(parts.length+1);
   for(int i=0;i<parts.length;i++)label(lines,parts[i],x+14,y+gap*(i+1),right-x-35);
 }
 public static void main(String[] unused){
   List<ScheduleGridInterpreter.Line> lines=new ArrayList<>();
   List<ScheduleGridInterpreter.Tile> tiles=new ArrayList<>();
   String[] headers={"LUNES","MARTES","MIÉRCOLES","JUEVES","VIERNES"};
   int[] x={400,649,886,1135,1381};
   for(int i=0;i<5;i++)label(lines,headers[i],x[i]-58,337,116);
   String[] periods={"07:00 - 07:50","07:50 - 08:40","08:50 - 09:40","09:40 - 10:30",
           "10:40 - 11:30","11:30 - 12:20","12:20 - 13:10","13:10 - 14:00"};
   int[] y={418,497,579,658,738,816,898,978};
   for(int i=0;i<8;i++)label(lines,periods[i],65,y[i],215);
   cell(lines,tiles,287,545,517,692,"TUTORÍA|EDUCATIVA");
   cell(lines,tiles,287,784,515,1013,"RECURSOS|DIGITALES");
   cell(lines,tiles,536,383,763,531,"TEXTOS LÍRICOS");
   cell(lines,tiles,536,545,763,772,"DIDÁCTICA DE|LA LENGUA Y|LITERATURA II");
   cell(lines,tiles,536,869,763,1016,"TENDENCIAS|EDUCATIVAS (E)");
   cell(lines,tiles,775,550,1003,698,"TENDENCIAS|EDUCATIVAS (E)");
   cell(lines,tiles,775,709,1003,857,"RESPONSABILIDAD|SOCIAL Y RENDICIÓN|DE CUENTAS (E)");
   cell(lines,tiles,775,869,1003,1016,"INVESTIGACIÓN|EDUCATIVA I");
   cell(lines,tiles,1022,383,1250,531,"RECURSOS|DIGITALES");
   cell(lines,tiles,1023,544,1249,692,"TUTORÍA|EDUCATIVA");
   cell(lines,tiles,1023,705,1249,852,"DIDÁCTICA DE|LA LENGUA Y|LITERATURA II");
   cell(lines,tiles,1023,865,1249,1013,"INVESTIGACIÓN|EDUCATIVA I");
   cell(lines,tiles,1268,619,1494,846,"LITERATURA|HISPANOAMERIC|ANA");
   cell(lines,tiles,1268,865,1496,1013,"RESPONSABILIDAD|SOCIAL Y RENDICIÓN|DE CUENTAS (E)");
   label(lines,"REPRESENTANTES ESTUDIANTILES",20,70,230);
   label(lines,"L.L.F. y P. TERCER AÑO",550,180,370);
   ScheduleParser.Result parsed=ScheduleGridInterpreter.parse(lines,tiles,1536,1086);
   ok(parsed.candidates.size()==14,"Expected fourteen cells, got "+parsed.candidates.size());
   Map<String,ScheduleEntry> found=new HashMap<>();
   for(ScheduleEntry s:parsed.candidates){
     ok(s.day>=1&&s.day<=5,"Valid weekdays");ok(s.end>s.start,"Positive class duration");
     found.put(s.day+"-"+s.start,s);
   }
   int[][] expected={{1,530,630},{1,690,840},{2,420,520},{2,530,690},{2,740,840},
      {3,530,630},{3,640,740},{3,740,840},{4,420,520},{4,530,630},
      {4,640,740},{4,740,840},{5,580,740},{5,740,840}};
   for(int[] e:expected){
     ScheduleEntry s=found.get(e[0]+"-"+e[1]);
     ok(s!=null,"Missing day/start "+e[0]+"/"+e[1]);
     ok(s.end==e[2],"Incorrect end for "+s.course);
   }
   ok(found.get("5-580").course.contains("HISPANOAMERICANA"),"Recombine split word");
   ok(found.get("2-530").course.contains("LITERATURA II"),"Keep multi-line course together");
   ok(ScheduleGridInterpreter.parse(lines.subList(0,5),tiles,1536,1086).candidates.isEmpty(),
          "No invented times when period labels are missing");
   System.out.println("PASS: "+checks+" 2.7 positional class timetable checks");
 }
}
