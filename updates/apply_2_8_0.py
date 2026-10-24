#!/usr/bin/env python3
"""Agenda Clara 2.8.0 — offline 72+ HSV swatches, stable course colors, OCR photo flexibility."""
from pathlib import Path
import textwrap
src=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
def write(name,code):
    (src/name).write_text(textwrap.dedent(code).lstrip(),encoding='utf-8')
def replace(file,old,new,expected=1):
    p=src/file; s=p.read_text(encoding='utf-8')
    if s.count(old)!=expected:raise RuntimeError(f'{file}: expected {expected} anchors, got {s.count(old)}: {old[:100]!r}')
    p.write_text(s.replace(old,new),encoding='utf-8')
write('ScheduleCourseColors.java',r'''
package pe.agendaclara.app;
import java.text.Normalizer;
import java.util.*;
/** Deterministic course identity and HSV spectrum. Offline, no color data download. */
public final class ScheduleCourseColors {
    private ScheduleCourseColors(){}
    public static String key(String title){
        if(title==null)return "";
        String n=Normalizer.normalize(title,Normalizer.Form.NFD).replaceAll("\\p{M}+","").toLowerCase(Locale.ROOT);
        return n.replaceAll("[^\\p{L}\\p{N}]+"," ").trim().replaceAll("\\s+"," ");
    }
    public static boolean same(String a,String b){String x=key(a);return !x.isEmpty()&&x.equals(key(b));}
    public static int hsv(float hue,float saturation,float brightness){
        float h=((hue%360)+360)%360,s=Math.max(0,Math.min(1,saturation)),v=Math.max(0,Math.min(1,brightness));
        float c=v*s,x=c*(1-Math.abs((h/60)%2-1)),m=v-c;float r=0,g=0,b=0;
        if(h<60){r=c;g=x;}else if(h<120){r=x;g=c;}else if(h<180){g=c;b=x;}
        else if(h<240){g=x;b=c;}else if(h<300){r=x;b=c;}else{r=c;b=x;}
        return 0xff000000 | (Math.round((r+m)*255)<<16) | (Math.round((g+m)*255)<<8) | Math.round((b+m)*255);
    }
    /** 12 hues x 6 lightness/saturation variations = 72 ready choices. */
    public static int[] palette(){
        int[] shades=new int[72];int p=0;
        float[][] variants={{.64f,.96f},{.46f,.98f},{.79f,.82f},{.52f,.78f},{.35f,.93f},{.73f,.64f}};
        for(float[] variant:variants)for(int h=0;h<360;h+=30)shades[p++]=hsv(h,variant[0],variant[1]);
        return shades;
    }
    public static int accessibleText(int color){
        double r=((color>>>16)&255)/255.0,g=((color>>>8)&255)/255.0,b=(color&255)/255.0;
        r=r<=.04045?r/12.92:Math.pow((r+.055)/1.055,2.4);
        g=g<=.04045?g/12.92:Math.pow((g+.055)/1.055,2.4);
        b=b<=.04045?b/12.92:Math.pow((b+.055)/1.055,2.4);
        return .2126*r+.7152*g+.0722*b>.19?0xff101d43:0xffffffff;
    }
    public static int deterministic(String title){
        String k=key(title);if(k.isEmpty())return 0xff4989f7;
        int hash=k.hashCode()&0x7fffffff;
        return hsv((hash%360),.53f,.92f);
    }
    public static Integer existingColor(String name,Collection<ScheduleEntry> saved){
        if(saved==null)return null;for(ScheduleEntry s:saved)if(same(name,s.course))return s.color;return null;
    }
    /** Exact normalized course names share color; ambiguous near matches are never auto-merged. */
    public static void align(List<ScheduleEntry> detected,Collection<ScheduleEntry> saved){
        if(detected==null)return;
        LinkedHashMap<String,Integer> colors=new LinkedHashMap<>();
        if(saved!=null)for(ScheduleEntry s:saved)colors.putIfAbsent(key(s.course),s.color);
        for(ScheduleEntry s:detected){String k=key(s.course);if(k.isEmpty())continue;
            Integer color=colors.get(k);if(color==null){color=deterministic(s.course);colors.put(k,color);}s.color=color;
        }
    }
    public static Map<String,List<ScheduleEntry>> groups(Collection<ScheduleEntry> sessions){
        LinkedHashMap<String,List<ScheduleEntry>> out=new LinkedHashMap<>();
        if(sessions!=null)for(ScheduleEntry s:sessions)out.computeIfAbsent(key(s.course),k->new ArrayList<>()).add(s);
        return out;
    }
}
''')
write('ScheduleVirtualGrid.java',r'''
package pe.agendaclara.app;
import java.util.*;
import java.util.regex.*;
/** Conservative OCR fallback for photos containing weekday columns and a time ruler
 * but no reliably detected cell boundaries. Each candidate remains user-reviewable. */
public final class ScheduleVirtualGrid {
    private ScheduleVirtualGrid(){}
    static final class Header {int day,x,y;Header(int d,int x,int y){day=d;this.x=x;this.y=y;}}
    static final class Period {int y,start,end;Period(int y,int s,int e){this.y=y;start=s;end=e;}}
    public static ScheduleParser.Result parse(List<ScheduleGridInterpreter.Line> lines,int width,int height){
        ScheduleParser.Result output=new ScheduleParser.Result();
        if(lines==null||width<150||height<150)return output;
        ArrayList<Header> headers=new ArrayList<>();ArrayList<Period> periods=new ArrayList<>();
        for(ScheduleGridInterpreter.Line line:lines){
            String text=ScheduleParser.fold(line.text).replace(".","").trim();
            int day=ScheduleParser.day(text);
            if(day>0&&text.matches("(?:lunes|martes|miercoles|jueves|viernes|sabado|domingo|lun|mar|mie|jue|vie|sab|dom)"))
                headers.add(new Header(day,line.x(),line.y()));
            Matcher m=ScheduleParser.TIME.matcher(text);
            if(m.find()&&line.x()<width*.33){
                int st=Integer.parseInt(m.group(1))*60+Integer.parseInt(m.group(2));
                int en=Integer.parseInt(m.group(3))*60+Integer.parseInt(m.group(4));
                if(en>st&&en<=1440&&en-st<=240)periods.add(new Period(line.y(),st,en));
            }
        }
        if(headers.size()<2||periods.size()<2)return output;
        headers.sort(Comparator.comparingInt(h->h.x));
        ArrayList<Header> distinct=new ArrayList<>();HashSet<Integer> seenDays=new HashSet<>();
        for(Header h:headers)if(seenDays.add(h.day))distinct.add(h);
        headers=distinct;
        periods.sort(Comparator.comparingInt(p->p.y));
        ArrayList<Period> distinctPeriods=new ArrayList<>();HashSet<String> times=new HashSet<>();
        for(Period p:periods)if(times.add(p.start+"/"+p.end))distinctPeriods.add(p);
        periods=distinctPeriods;
        if(headers.size()<2||periods.size()<2)return output;
        int headerEnd=0;for(Header h:headers)headerEnd=Math.max(headerEnd,h.y);
        int approximateRowHeight=Math.max(18,(periods.get(periods.size()-1).y-periods.get(0).y)/Math.max(1,periods.size()-1));
        HashSet<String> seen=new HashSet<>();
        for(ScheduleGridInterpreter.Line line:lines){
            String caption=line.text.trim();if(caption.length()<3||line.y()<=headerEnd+8)continue;
            if(ScheduleParser.TIME.matcher(ScheduleParser.fold(caption)).find()||ScheduleParser.day(caption)>0&&caption.length()<11)continue;
            Header column=null;int dx=Integer.MAX_VALUE;
            for(Header h:headers){int distance=Math.abs(line.x()-h.x);if(distance<dx){dx=distance;column=h;}}
            if(column==null||dx>Math.max(width/12,approximateRowHeight*2))continue;
            Period period=null;int dy=Integer.MAX_VALUE;
            for(Period p:periods){int distance=Math.abs(line.y()-p.y);if(distance<dy){dy=distance;period=p;}}
            if(period==null||dy>approximateRowHeight*.46f)continue;
            // One row maximum in boundary-less fallback; never invent multi-period duration.
            if(caption.length()>120)continue;
            ScheduleEntry entry=new ScheduleEntry();entry.day=column.day;entry.start=period.start;entry.end=period.end;entry.course=caption;
            String key=entry.day+"/"+entry.start+"/"+ScheduleCourseColors.key(caption);
            if(seen.add(key))output.candidates.add(entry);
        }
        if(!output.candidates.isEmpty()){
            output.uncertain.add("La fotografía no muestra bordes claros: estas clases se ubicaron por proximidad a las filas de horas. Corrige los bloques que duren más de una franja.");
        }
        return output;
    }
}
''')
# UI changes: duplicate OCR colors resolved against existing sessions, manual edit and import grouped
replace('ScheduleActivity.java','chosen.clear();for(int n=0;n<detected.candidates.size();n++)chosen.add(true);show(5);',
        'ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all());chosen.clear();for(int n=0;n<detected.candidates.size();n++)chosen.add(true);show(5);')
replace('ScheduleActivity.java','for(int i=0;i<detected.candidates.size();i++){\n            ScheduleEntry s=detected.candidates.get(i);final int index=i;LinearLayout c=card();',
'''Map<String,List<ScheduleEntry>> related=ScheduleCourseColors.groups(detected.candidates);
        for(int i=0;i<detected.candidates.size();i++){
            ScheduleEntry s=detected.candidates.get(i);final int index=i;LinearLayout c=card();
            int relatedCount=related.get(ScheduleCourseColors.key(s.course)).size();
            if(relatedCount>1){TextView group=txt("▣  Mismo curso · "+relatedCount+" días/sesiones · color compartido",12,BLUE,true);c.addView(group);}
            View accent=new View(this);accent.setBackground(bg(s.color,8));c.addView(accent,new LinearLayout.LayoutParams(-1,dp(7)));space(c,6);''')
replace('ScheduleActivity.java','confirmConflicts(approved,()->{int added=ScheduleDatabase.get(this).importReviewed(approved);',
        'confirmConflicts(approved,()->{ScheduleCourseColors.align(approved,ScheduleDatabase.get(this).all());int added=ScheduleDatabase.get(this).importReviewed(approved);')
# groups course list preserving actual session children
replace('ScheduleActivity.java','for(ScheduleEntry s:classes){LinearLayout c=card();c.setPadding',
'''for(Map.Entry<String,List<ScheduleEntry>> courseGroup:ScheduleCourseColors.groups(classes).entrySet()){
            List<ScheduleEntry> sessions=courseGroup.getValue();ScheduleEntry primary=sessions.get(0);
            LinearLayout banner=card();View colorBand=new View(this);colorBand.setBackground(bg(primary.color,9));banner.addView(colorBand,new LinearLayout.LayoutParams(-1,dp(7)));
            space(banner,8);banner.addView(txt(primary.course+" · "+sessions.size()+" "+(sessions.size()==1?"sesión":"sesiones"),16,INK,true));
            for(ScheduleEntry s:sessions){LinearLayout c=card();c.setPadding''')
replace('ScheduleActivity.java','r.addView(btn("✎",()->editor(s,null),false),new LinearLayout.LayoutParams(dp(48),dp(48)));c.addView(r);\n        }\n    }',
        'r.addView(btn("✎",()->editor(s,null),false),new LinearLayout.LayoutParams(dp(48),dp(48)));c.addView(r);\n        }}\n    }')
# replace swatch row with UI widget palette custom dialog
start='''        form.addView(txt("Color del curso",13,INK,true));space(form,7);LinearLayout palette=row();final int[] color={current.color};ArrayList<View> swatches=new ArrayList<>();
        for(int shade:ScheduleEntry.COLORS){View circle=new View(this);GradientDrawable oval=new GradientDrawable();oval.setColor(shade);oval.setCornerRadius(dp(99));oval.setStroke(dp(2),shade==current.color?BLUE:0xffffffff);circle.setBackground(oval);LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,dp(34),1);params.setMargins(dp(2),0,dp(2),0);palette.addView(circle,params);swatches.add(circle);circle.setOnClickListener(v->{color[0]=shade;for(View other:swatches){GradientDrawable gd=(GradientDrawable)other.getBackground();gd.setStroke(dp(2),other==circle?BLUE:0xffffffff);}});}
        form.addView(palette);space(form,12);'''
replacement='''        form.addView(txt("Color del curso · 72 tonos y espectro completo",13,INK,true));space(form,7);
        final int[] color={current.color};final boolean[] manuallyColored={false};
        View colorPreview=new View(this);colorPreview.setBackground(bg(color[0],13));
        form.addView(colorPreview,new LinearLayout.LayoutParams(-1,dp(28)));space(form,8);
        android.widget.GridLayout palette=new android.widget.GridLayout(this);palette.setColumnCount(8);
        for(int shade:ScheduleCourseColors.palette()){
            View swatch=new View(this);GradientDrawable circle=new GradientDrawable();circle.setShape(GradientDrawable.OVAL);circle.setColor(shade);
            circle.setStroke(dp(1),LINE);swatch.setBackground(circle);
            android.widget.GridLayout.LayoutParams params=new android.widget.GridLayout.LayoutParams();params.width=dp(29);params.height=dp(29);params.setMargins(dp(3),dp(3),dp(3),dp(3));palette.addView(swatch,params);
            swatch.setContentDescription("Usar color #"+String.format(Locale.ROOT,"%06X",shade&0xffffff));
            swatch.setOnClickListener(v->{color[0]=shade;manuallyColored[0]=true;colorPreview.setBackground(bg(shade,13));});
        }
        form.addView(palette);space(form,9);
        form.addView(btn("Más colores · Mezclador HSV",()->colorMixer(color,manuallyColored,colorPreview),false));
        space(form,6);form.addView(txt("El mismo curso conservará este color en todos sus días.",12,MUTED,false));space(form,12);'''
replace('ScheduleActivity.java',start,replacement)
# listener auto sets matching color if user didn't choose custom
replace('ScheduleActivity.java','        form.addView(palette);space(form,9);','''        form.addView(palette);space(form,9);
        course.addTextChangedListener(new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence s,int st,int count,int after){}
            public void onTextChanged(CharSequence s,int st,int before,int count){
                if(manuallyColored[0])return;
                Integer savedColor=ScheduleCourseColors.existingColor(s.toString(),ScheduleDatabase.get(ScheduleActivity.this).all());
                color[0]=savedColor!=null?savedColor:ScheduleCourseColors.deterministic(s.toString());
                colorPreview.setBackground(bg(color[0],13));
            }
            public void afterTextChanged(android.text.Editable e){}
        });''')
replace('ScheduleActivity.java','e.color=color[0];e.reminder=offsets',
        'e.color=color[0];e.reminder=offsets')
replace('ScheduleActivity.java','if(importing){ScheduleEntry s=additions.get(0);',
'''if(importing){ScheduleEntry s=additions.get(0);''')
# editing recognized course propagate color among OCR peers on completion
replace('ScheduleActivity.java','dialog.dismiss();if(onDone!=null)onDone.run();return;}\n            confirmConflicts',
'''dialog.dismiss();if(detected!=null){for(ScheduleEntry linked:detected.candidates)if(ScheduleCourseColors.same(current.course,linked.course))linked.color=current.color;}
                if(onDone!=null)onDone.run();return;}
            confirmConflicts''')
replace('ScheduleActivity.java','for(ScheduleEntry s:additions){if(current.id==0)s.id=0;if(db.save(s))ScheduleReminders.schedule(this,s);}dialog.dismiss();',
'''for(ScheduleEntry s:additions){if(current.id==0)s.id=0;if(db.save(s))ScheduleReminders.schedule(this,s);db.recolorSameCourse(s.course,s.color);}
                dialog.dismiss();''')
# text accessible for any chosen swatch in weekly grid
replace('ScheduleActivity.java','tile.addView(name);\n                tile.addView(txt(ScheduleEntry.clock(s.start),10,INK,false));',
'''name.setTextColor(ScheduleCourseColors.accessibleText(s.color));tile.addView(name);
                tile.addView(txt(ScheduleEntry.clock(s.start),10,ScheduleCourseColors.accessibleText(s.color),false));''')
replace('ScheduleActivity.java','tile.addView(room);}',
        'room.setTextColor(ScheduleCourseColors.accessibleText(s.color));tile.addView(room);}')
# interactive full HSV range, three sliders
replace('ScheduleActivity.java','    private void pickClock(EditText destination){', '''    private void colorMixer(int[] color,boolean[] manuallyColored,View preview){
        LinearLayout panel=col();panel.setPadding(dp(20),dp(12),dp(20),dp(8));
        TextView sample=txt("Vista previa del color",15,0xff101d43,true);sample.setGravity(Gravity.CENTER);sample.setPadding(dp(8),dp(10),dp(8),dp(10));panel.addView(sample);
        SeekBar hue=new SeekBar(this),sat=new SeekBar(this),brightness=new SeekBar(this);
        hue.setMax(359);sat.setMax(100);brightness.setMax(100);
        float[] hsv=new float[3];android.graphics.Color.colorToHSV(color[0],hsv);
        hue.setProgress((int)hsv[0]);sat.setProgress(Math.round(hsv[1]*100));brightness.setProgress(Math.round(hsv[2]*100));
        panel.addView(txt("Tono · 0–359°",13,INK,true));panel.addView(hue);
        panel.addView(txt("Saturación",13,INK,true));panel.addView(sat);
        panel.addView(txt("Brillo",13,INK,true));panel.addView(brightness);
        final int[] selected={color[0]};
        Runnable refresh=()->{selected[0]=ScheduleCourseColors.hsv(hue.getProgress(),sat.getProgress()/100f,brightness.getProgress()/100f);sample.setBackground(bg(selected[0],15));sample.setTextColor(ScheduleCourseColors.accessibleText(selected[0]));sample.setText(String.format(Locale.ROOT,"COLOR #%06X",selected[0]&0xffffff));};
        SeekBar.OnSeekBarChangeListener listener=new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar v,int p,boolean fromUser){refresh.run();}
            public void onStartTrackingTouch(SeekBar v){}public void onStopTrackingTouch(SeekBar v){}
        };
        hue.setOnSeekBarChangeListener(listener);sat.setOnSeekBarChangeListener(listener);brightness.setOnSeekBarChangeListener(listener);refresh.run();
        new AlertDialog.Builder(this).setTitle("Personalizar color del curso").setView(panel)
            .setNegativeButton("Cancelar",null).setPositiveButton("Aplicar",(d,w)->{color[0]=selected[0];manuallyColored[0]=true;preview.setBackground(bg(selected[0],13));}).show();
    }
    private void pickClock(EditText destination){''')
# Database repaint same normalized course, transaction
replace('ScheduleDatabase.java','    public synchronized void delete(long id){', '''    public synchronized int recolorSameCourse(String title,int color){
        SQLiteDatabase db=getWritableDatabase();int modified=0;
        db.beginTransaction();try{
            for(ScheduleEntry s:all())if(ScheduleCourseColors.same(title,s.course)&&s.color!=color){
                ContentValues cv=new ContentValues();cv.put("color",color);
                modified+=db.update("sessions",cv,"id=?",new String[]{Long.toString(s.id)});
            }db.setTransactionSuccessful();}finally{db.endTransaction();}return modified;
    }
    public synchronized void delete(long id){''')
# keep imports for OCR consistent and de-dupe accent variations without writing new schema
replace('ScheduleDatabase.java','for(ScheduleEntry s:items){if(!ScheduleEntry.valid(s)||!allowedReminder(s.reminder))continue;try(Cursor c=db.rawQuery(',
'''ScheduleCourseColors.align(items,all());
        for(ScheduleEntry s:items){if(!ScheduleEntry.valid(s)||!allowedReminder(s.reminder))continue;try(Cursor c=db.rawQuery(''')
# Parser stable course colors after input even repeated in diff days
replace('ScheduleParser.java','entry.color=ScheduleEntry.COLORS[output.candidates.size()%ScheduleEntry.COLORS.length];output.candidates.add(entry);',
        'entry.color=ScheduleCourseColors.deterministic(entry.course);output.candidates.add(entry);')
# grid parser colors
replace('ScheduleGridInterpreter.java','entry.color=ScheduleEntry.COLORS[result.candidates.size()%ScheduleEntry.COLORS.length];result.candidates.add(entry);',
        'entry.color=ScheduleCourseColors.deterministic(entry.course);result.candidates.add(entry);')
# schedule OCR fallback when detected rectangles fail
replace('ScheduleOcr.java','''        ScheduleParser.Result fallback=ScheduleParser.parse(recognized.getText());
        fallback.uncertain.add("No se pudo reconstruir la cuadrícula de la imagen. La lectura de texto es aproximada: verifica todas las horas antes de guardar.");
        return fallback;''',
'''        ScheduleParser.Result virtual=ScheduleVirtualGrid.parse(lines,imageWidth,imageHeight);
        if(!virtual.candidates.isEmpty())return virtual;
        ScheduleParser.Result fallback=ScheduleParser.parse(recognized.getText());
        fallback.uncertain.add("No se pudo reconstruir la cuadrícula de la imagen. La lectura de texto es aproximada: verifica todas las horas antes de guardar.");
        return fallback;''')
# version
p=Path('AgendaClara/app/build.gradle');s=p.read_text(encoding='utf-8')
assert s.count('versionCode 17')==1 and s.count("versionName '2.7.0'")==1
p.write_text(s.replace('versionCode 17','versionCode 18').replace("versionName '2.7.0'","versionName '2.8.0'"),encoding='utf-8')
print('AGENDA_2_8_APPLIED: colors, course groups, OCR virtual-grid, stable schedule import.');