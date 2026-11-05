#!/usr/bin/env python3
"""Agenda Clara 3.13.7: improve photo recognition without silent course creation.

Based on the verified 3.13.6 source ZIP. This only patches source.
"""
from pathlib import Path
import shutil

JAVA=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
HERE=Path(__file__).resolve().parent

def patch(text,old,new,label):
    count=text.count(old)
    if count!=1:raise RuntimeError(f"{label}: expected one anchor, got {count}")
    return text.replace(old,new,1)

def parser(text):
    return patch(text,
        "public final ArrayList<String> uncertain=new ArrayList<>();}",
        "public final ArrayList<String> uncertain=new ArrayList<>();"
        "public final LinkedHashSet<String> reviewOnlyKeys=new LinkedHashSet<>();}",
        "OCR result selection state")

def ocr(text):
    old='''        if(!table.candidates.isEmpty()){
            // A partial image may leave some empty/illegible cells; explicitly warn.
            int failures=tiles==null?0:Math.max(0,tiles.size()-table.candidates.size());
            if(failures>0)table.uncertain.add("Se detectaron "+failures+" bloques sin curso u hora verificable. Revisa la fotografía y completa esos cursos manualmente.");
            return corroboration(table,glance);
        }
        ScheduleParser.Result virtual=ScheduleVirtualGrid.parse(lines,imageWidth,imageHeight);
        if(!virtual.candidates.isEmpty())return corroboration(virtual,glance);
        ScheduleParser.Result fallback=ScheduleParser.parse(recognized.getText());
        fallback.uncertain.add("No se pudo reconstruir la cuadrícula de la imagen. La lectura de texto es aproximada: verifica todas las horas antes de guardar.");
        return corroboration(fallback,glance);'''
    new='''        // Always run complementary readers: even one detected rectangle previously
        // caused all other recognized course text to be silently discarded.
        ScheduleParser.Result virtual=ScheduleVirtualGrid.parse(lines,imageWidth,imageHeight);
        ScheduleParser.Result fallback=ScheduleParser.parse(recognized.getText());
        ScheduleParser.Result combined=ScheduleOcrFusion.reconcile(table,virtual,fallback);
        if(table.candidates.isEmpty()&&virtual.candidates.isEmpty())
            combined.uncertain.add("No se pudo reconstruir una cuadrícula fiable. "+
                "Revisa con especial cuidado los días y las horas del texto.");
        if(!combined.reviewOnlyKeys.isEmpty())
            combined.uncertain.add("Las clases recuperadas de lecturas complementarias "+
                "aparecen desmarcadas. Selecciona solo las que veas en la fotografía.");
        return corroboration(combined,glance);'''
    return patch(text,old,new,"combine 3 independent OCR readers")

def photo(text):
    text=patch(text,"options.inPreferredConfig=Bitmap.Config.RGB_565;",
                      "options.inPreferredConfig=Bitmap.Config.ARGB_8888;",
                      "preserve 8-bit OCR image channels")
    text=patch(text,"bounds.outHeight)/sample>2048",
                      "bounds.outHeight)/sample>2560",
                      "preserve small timetable text")
    return text

def colored_tiles(text):
    return patch(text,
        '''            }
        }finally{if(small!=bitmap)small.recycle();}''',
        '''            }
            // Timetable blocks can be blue/green/pink rather than white.
            // Keep the old white detector; add independent pastel rectangles
            // only when not already represented by a matching white tile.
            if(output.size()<100)
                for(ScheduleGridInterpreter.Tile candidate:
                        ScheduleColorTileDetector.detect(pixels,width,height)){
                    int left=(int)Math.round(candidate.left/scale);
                    int top=(int)Math.round(candidate.top/scale);
                    int right=(int)Math.round(candidate.right/scale);
                    int bottom=(int)Math.round(candidate.bottom/scale);
                    int area=Math.max(1,(right-left)*(bottom-top));
                    boolean represented=false;
                    for(ScheduleGridInterpreter.Tile old:output){
                        int ix=Math.max(0,Math.min(right,old.right)-
                            Math.max(left,old.left));
                        int iy=Math.max(0,Math.min(bottom,old.bottom)-
                            Math.max(top,old.top));
                        int oldArea=Math.max(1,(old.right-old.left)*
                            (old.bottom-old.top));
                        if((double)ix*iy/Math.min(area,oldArea)>.65){
                            represented=true;break;
                        }
                    }
                    if(!represented&&output.size()<100)
                        output.add(new ScheduleGridInterpreter.Tile(
                            left,top,right,bottom));
                }
        }finally{if(small!=bitmap)small.recycle();}''',
        "detect pastel tiles without breaking white detector")

def grid(text):
    text=patch(text,"if(columns.size()<2||periods.size()<2)return result;",
                    "if(columns.isEmpty()||periods.isEmpty())return result;",
                    "support one day/one time row in printed timetables")
    text=patch(text,
        '''if(intersection>=lineArea*.53f&&line.y()>=tile.top-5&&line.y()<=tile.bottom+5){''',
        '''if(intersection>=lineArea*.42f&&line.y()>=tile.top-7&&line.y()<=tile.bottom+7){''',
        "allow wrapped text at tile edge")
    return text

def virtual(text):
    text=patch(text,"if(headers.size()<2||periods.size()<2)return out;",
                    "if(headers.isEmpty()||periods.isEmpty())return out;",
                    "support partial photo with one recognized day/time")
    text=patch(text,
        "int rowHeight=Math.max(18,sum/Math.max(1,periods.size()-1));",
        "int rowHeight=periods.size()<2?Math.max(36,height/15):"
        "Math.max(18,sum/(periods.size()-1));",
        "fallback slot size with one period")
    return text

def matching(text):
    return patch(text,
        '''        if(hasExplicitGroup(left)||hasExplicitGroup(right))return Relation.DIFFERENT;
        if(!suffix(left).equals(suffix(right)))return Relation.DIFFERENT;
        if(ScheduleCourseColors.same(left,right))return Relation.EXACT;''',
        '''        // Identical explicit groups across different days are the SAME label,
        // while different levels and group numbers must remain distinct.
        if(ScheduleCourseColors.same(left,right))return Relation.EXACT;
        if(hasExplicitGroup(left)||hasExplicitGroup(right))return Relation.DIFFERENT;
        if(!suffix(left).equals(suffix(right)))return Relation.DIFFERENT;''',
        "same group/course across days")

def review(text):
    old='''    /** Combine COURSE identity only. All day/time/room/teacher fields remain unchanged. */
    public static void accept(List<ScheduleEntry> entries,Pair pair){
        ScheduleEntry first=entries.get(pair.earlier),second=entries.get(pair.later);
        String oldName=first.course;
        String best=ScheduleCourseRecognition.preferred(oldName,second.course);
        // A previously confirmed same-name group also receives the complete name.
        for(int i=0;i<entries.size();i++){
            ScheduleEntry e=entries.get(i);
            if(i==pair.later||i==pair.earlier||ScheduleCourseColors.same(e.course,oldName)){
                e.course=best;e.color=first.color;
            }
        }
    }'''
    new='''    /** User-chosen canonical spelling; keeps all sessions and their times. */
    public static void acceptWithName(List<ScheduleEntry> entries,Pair pair,String confirmedName){
        if(confirmedName==null||confirmedName.trim().length()<2||
                confirmedName.trim().length()>120)
            throw new IllegalArgumentException("Especifica un nombre de curso válido");
        ScheduleEntry first=entries.get(pair.earlier),second=entries.get(pair.later);
        String leftName=first.course,rightName=second.course;
        int color=first.color;
        // Update all sessions for BOTH OCR spellings, not just the selected row.
        for(ScheduleEntry e:entries){
            if(ScheduleCourseColors.same(e.course,leftName)||
                    ScheduleCourseColors.same(e.course,rightName)){
                e.course=confirmedName.trim();e.color=color;
            }
        }
    }
    /** Backward-compatible helper for unambiguous exact-name confirmation. */
    public static void accept(List<ScheduleEntry> entries,Pair pair){
        acceptWithName(entries,pair,ScheduleCourseRecognition.preferred(
            entries.get(pair.earlier).course,entries.get(pair.later).course));
    }'''
    return patch(text,old,new,"user-selected canonical name")

def activity(text):
    text=patch(text,
        '''ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all(profileId));chosen.clear();for(int n=0;n<detected.candidates.size();n++)chosen.add(true);show(5);''',
        '''ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all(profileId));
                        chosen.clear();
                        for(ScheduleEntry candidate:detected.candidates)
                            chosen.add(!detected.reviewOnlyKeys.contains(ScheduleOcrFusion.key(candidate)));
                        show(5);''',
        "alternative OCR candidates must start unselected")
    text=patch(text,
        '''            CheckBox ok=new CheckBox(this);ok.setText(s.course);''',
        '''            if(detected.reviewOnlyKeys.contains(ScheduleOcrFusion.key(s)))
                c.addView(txt("Lectura adicional · COMPRUEBA EN LA FOTO antes de seleccionar",
                    12,BLUE,true));
            CheckBox ok=new CheckBox(this);ok.setText(s.course);''',
        "mark candidate source clearly")
    text=patch(text,
        '''if(!detected.uncertain.isEmpty()){LinearLayout warning=card();head(warning,"Datos no confirmados","No se importaron "+detected.uncertain.size()+" líneas porque les faltaba información clara.");for(int i=0;i<Math.min(8,detected.uncertain.size());i++){space(warning,6);warning.addView(txt("• "+detected.uncertain.get(i),12,RED,false));}}''',
        '''if(!detected.uncertain.isEmpty()){
            LinearLayout warning=card();
            head(warning,"Lecturas y anomalías por corroborar",
                "Algunas son sugerencias sin seleccionar; otras requieren corrección manual.");
            for(int i=0;i<Math.min(12,detected.uncertain.size());i++){
                space(warning,6);
                warning.addView(txt("• "+detected.uncertain.get(i),12,RED,false));
            }
            if(detected.uncertain.size()>12)
                warning.addView(txt("Y "+(detected.uncertain.size()-12)+" avisos más.",12,MUTED,false));
        }''',
        "make all review warnings understandable")
    text=patch(text,
        '''if(key.contains("sin curso")||key.contains("curso ambiguo")||
                    key.contains("ocr duplicado")||key.contains("repetición ocr"))''',
        '''if(key.contains("sin curso")||key.contains("curso ambiguo")||
                    key.contains("ocr duplicado")||key.contains("repetición ocr")||
                    key.contains("lectura complementaria")||key.contains("no se reconoció")||
                    key.contains("sin día")||key.contains("sin hora"))''',
        "include complementary OCR uncertainty in final popup")
    text=patch(text,
        '''        together.setOnClickListener(v->{
            SchedulePhotoReview.accept(approved,pair);
            confirmed.add(pair.later);popup.dismiss();
            confirmPhotoPairs(approved,confirmed,rejected,onComplete);
        });''',
        '''        together.setOnClickListener(v->{
            if(pair.exact){
                SchedulePhotoReview.accept(approved,pair);
                confirmed.add(pair.later);popup.dismiss();
                confirmPhotoPairs(approved,confirmed,rejected,onComplete);
            }else{
                popup.dismiss();
                chooseFinalCourseName(approved,pair,confirmed,rejected,onComplete);
            }
        });''',
        "ask canonical spelling after accepting a nonidentical match")
    anchor='''    private void courseList(){'''
    helper='''    /** A shared first word never dictates the final name of a course. */
    private void chooseFinalCourseName(ArrayList<ScheduleEntry> approved,
            SchedulePhotoReview.Pair pair,Set<Integer> confirmed,
            Set<String> rejected,Runnable onComplete){
        ScheduleEntry first=approved.get(pair.earlier),second=approved.get(pair.later);
        String firstName=first.course,secondName=second.course;
        LinearLayout content=col();
        content.setPadding(dp(18),dp(10),dp(18),dp(12));
        content.addView(txt("Elige el nombre completo y correcto que tendrá "+
            "la asignatura. Los días y las horas no cambiarán.",13,MUTED,false));
        space(content,12);
        Button useFirst=btn("Conservar: "+firstName,()->{},false);
        Button useSecond=btn("Conservar: "+secondName,()->{},false);
        Button custom=btn("Escribir otro nombre",()->{},false);
        content.addView(useFirst);space(content,7);
        content.addView(useSecond);space(content,7);content.addView(custom);
        AlertDialog choice=scheduleDialog().setTitle("Confirmar nombre del curso")
            .setView(content).setNegativeButton("Volver a la revisión",null).create();
        java.util.function.Consumer<String> apply=title->{
            try{
                SchedulePhotoReview.acceptWithName(approved,pair,title);
                confirmed.add(pair.later);
                choice.dismiss();
                confirmPhotoPairs(approved,confirmed,rejected,onComplete);
            }catch(IllegalArgumentException error){toast(error.getMessage());}
        };
        useFirst.setOnClickListener(v->apply.accept(firstName));
        useSecond.setOnClickListener(v->apply.accept(secondName));
        custom.setOnClickListener(v->{
            EditText entry=new EditText(this);
            entry.setSingleLine(true);entry.setText(
                ScheduleCourseRecognition.preferred(firstName,secondName));
            entry.setSelectAllOnFocus(true);
            AlertDialog editor=scheduleDialog().setTitle("Nombre correcto del curso")
                .setView(entry).setNegativeButton("Cancelar",null)
                .setPositiveButton("Confirmar",null).create();
            editor.setOnShowListener(x->editor.getButton(-1).setOnClickListener(b->{
                String title=entry.getText().toString().trim();
                if(title.length()<2||title.length()>120){
                    entry.setError("Escribe entre 2 y 120 caracteres");return;
                }
                editor.dismiss();apply.accept(title);
            }));
            editor.show();
        });
        choice.show();
    }

'''
    text=patch(text,anchor,helper+anchor,"insert user name choice")
    return text

def run():
    files={
        "ScheduleParser.java":parser,
        "ScheduleOcr.java":ocr,
        "SchedulePhotoLoader.java":photo,
        "ScheduleImageBlocks.java":colored_tiles,
        "ScheduleGridInterpreter.java":grid,
        "ScheduleVirtualGrid.java":virtual,
        "ScheduleCourseRecognition.java":matching,
        "SchedulePhotoReview.java":review,
        "ScheduleActivity.java":activity
    }
    staged={}
    for filename,transform in files.items():
        path=JAVA/filename
        staged[path]=transform(path.read_text(encoding="utf-8"))
    fusion_path=JAVA/"ScheduleOcrFusion.java"
    colored_path=JAVA/"ScheduleColorTileDetector.java"
    if fusion_path.exists() or colored_path.exists():
        raise RuntimeError("Fusion or color tile component already installed")
    for library in ("ScheduleOcrFusion.java","ScheduleColorTileDetector.java"):
        if not (HERE/library).is_file():raise RuntimeError("Missing component "+library)
    gradle=GRADLE.read_text(encoding="utf-8")
    if gradle.count("versionCode 62")!=1 or gradle.count("versionName '3.13.6'")!=1:
        raise RuntimeError("Expected version 3.13.6 (62). Stop before modifying.")
    staged[GRADLE]=gradle.replace("versionCode 62","versionCode 63",1).replace(
        "versionName '3.13.6'","versionName '3.13.7'",1)
    for path,content in staged.items():path.write_text(content,encoding="utf-8")
    shutil.copyfile(HERE/"ScheduleOcrFusion.java",fusion_path)
    shutil.copyfile(HERE/"ScheduleColorTileDetector.java",colored_path)
    print("PASS: OCR 3.13.7 source installed: three interpretations, optional alternatives")
    print("PASS: detects solid pastel course tiles as well as white tiles")
    print("PASS: user-confirmed course names, one-day photos, improved image color depth")
    print("PASS: no auto-save of ambiguous readings; old schedules and tasks untouched")

if __name__=="__main__":run()
