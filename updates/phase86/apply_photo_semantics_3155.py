#!/usr/bin/env python3
"""Agenda Clara 3.15.5: context-aware photograph OCR and review workflow.

Applies only to reconstructed version 3.15.4. Existing saved records are
untouched; a separate explicit UI action can correct old course groups.
"""
from pathlib import Path
import hashlib
import tempfile
import os

ROOT=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
GRADLE=Path("AgendaClara/app/build.gradle")
STAGE=Path(__file__).resolve().parent
PHOTOS=[
    ROOT/"PhotoWidget.java", ROOT/"PhotoConfigActivity.java",
    ROOT/"PhotoTapActivity.java",
    Path("AgendaClara/app/src/main/res/layout/widget_photo.xml"),
    Path("AgendaClara/app/src/main/res/xml/photo_widget_info.xml")
]

def once(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise RuntimeError(f"{label}: expected one source anchor, found {count}")
    return text.replace(old,new,1)

def atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix=".phase86-",delete=False) as tmp:
        name=tmp.name
        tmp.write(data)
        tmp.flush();os.fsync(tmp.fileno())
    try:
        os.chmod(name,path.stat().st_mode & 0o777 if path.exists() else 0o644)
        os.replace(name,path)
    finally:
        Path(name).unlink(missing_ok=True)

def recognition(s):
    s=once(s,
       "public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT, SHARED_START, SHARED_WORD }",
       "public enum Relation { DIFFERENT, EXACT, TRUNCATED, OCR_VARIANT, SHARED_START, SHARED_WORD, LEVEL_UNCERTAIN }",
       "new review level")
    start=s.index("    public static Relation compare(String left,String right){")
    end=s.index("    /** Prefer the fuller spelling",start)
    method='''    public static Relation compare(String left,String right){
        if(left==null||right==null||left.trim().isEmpty()||right.trim().isEmpty())
            return Relation.DIFFERENT;
        // For imported OCR only, remove duplicated descriptor AFTER a known
        // course-code marker. Protect explicit academic groups and levels.
        String cleanedLeft=ScheduleCourseSemanticGuard.cleanOcrName(left);
        String cleanedRight=ScheduleCourseSemanticGuard.cleanOcrName(right);
        if(ScheduleCourseColors.same(cleanedLeft,cleanedRight))return Relation.EXACT;
        if(hasExplicitGroup(left)||hasExplicitGroup(right))return Relation.DIFFERENT;
        String levA=ScheduleCourseSemanticGuard.level(cleanedLeft);
        String levB=ScheduleCourseSemanticGuard.level(cleanedRight);
        if(!levA.equals(levB)){
            return ScheduleCourseSemanticGuard.ambiguousLevel(cleanedLeft,cleanedRight)?
                Relation.LEVEL_UNCERTAIN:Relation.DIFFERENT;
        }
        String a=key(cleanedLeft),b=key(cleanedRight);
        if(a.isEmpty()||b.isEmpty())return Relation.DIFFERENT;
        String shortName=a.length()<=b.length()?a:b;
        String longName=a.length()>b.length()?a:b;
        String[] sw=shortName.split(" ");
        if(shortName.length()>=3&&longName.startsWith(shortName+" ")&&
                longName.split(" ").length>sw.length){
            return shortName.length()>=6?Relation.TRUNCATED:Relation.SHARED_START;
        }
        if(ScheduleCourseSemanticGuard.strongBeginning(cleanedLeft,cleanedRight))
            return Relation.SHARED_START;
        if(ScheduleCourseSemanticGuard.meaningfulOverlap(cleanedLeft,cleanedRight))
            return Relation.SHARED_WORD;
        // A single common generic adjective ("educativa") is NEVER enough.
        int largest=Math.max(a.length(),b.length());
        if(largest<9||Math.abs(a.length()-b.length())>Math.max(3,largest*.20))
            return Relation.DIFFERENT;
        String aa=a.split(" ")[0],bb=b.split(" ")[0];
        if(aa.length()<4||bb.length()<4||distance(aa,bb)>2)return Relation.DIFFERENT;
        int max=(int)Math.floor(largest*.16);
        return distance(a,b)<=Math.max(2,max)?Relation.OCR_VARIANT:Relation.DIFFERENT;
    }
'''
    s=s[:start]+method+s[end:]
    s=once(s,
       '''        String a=key(left),b=key(right);
        if(a.length()==b.length())return left;
        return a.length()>b.length()?left:right;''',
       '''        String cleanLeft=ScheduleCourseSemanticGuard.cleanOcrName(left);
        String cleanRight=ScheduleCourseSemanticGuard.cleanOcrName(right);
        String a=key(cleanLeft),b=key(cleanRight);
        if(a.equals(b))return cleanLeft.length()<=cleanRight.length()?cleanLeft:cleanRight;
        return a.length()>=b.length()?cleanLeft:cleanRight;''',
       "prefer cleaned OCR label")
    return s

def photo_review(s):
    old='''                    rel==ScheduleCourseRecognition.Relation.SHARED_WORD?1:0;'''
    new='''                    rel==ScheduleCourseRecognition.Relation.SHARED_WORD?1:
                    rel==ScheduleCourseRecognition.Relation.LEVEL_UNCERTAIN?2:0;'''
    return once(s,old,new,"uncertain-level review ranking")

def activity(s):
    s=once(s,
        "    private Uri cameraImage;",
        "    private Uri cameraImage;\n    private android.graphics.Bitmap photoPreview;",
        "preview state")
    s=once(s,
        "    @Override protected void onDestroy(){io.shutdownNow();super.onDestroy();}",
        '''    @Override protected void onDestroy(){
        io.shutdownNow();
        if(photoPreview!=null&&!photoPreview.isRecycled())photoPreview.recycle();
        photoPreview=null;
        super.onDestroy();
    }''',
        "preview lifecycle")
    s=once(s,
        "                int imageWidth=photo.bitmap.getWidth(),imageHeight=photo.bitmap.getHeight();",
        '''                int imageWidth=photo.bitmap.getWidth(),imageHeight=photo.bitmap.getHeight();
                final android.graphics.Bitmap overlay=buildPhotoPreview(photo.bitmap,rectangles);''',
        "bounded photo overlay")
    s=once(s,
        '''                    if(isFinishing()||isDestroyed()){photo.bitmap.recycle();recognizing=false;return;}
                    TextRecognizer scanner''',
        '''                    if(isFinishing()||isDestroyed()){
                        photo.bitmap.recycle();overlay.recycle();recognizing=false;return;
                    }
                    if(photoPreview!=null&&!photoPreview.isRecycled())photoPreview.recycle();
                    photoPreview=overlay;
                    TextRecognizer scanner''',
        "save temporary preview")
    old='''                        ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all(profileId));
                        chosen.clear();
                        for(ScheduleEntry candidate:detected.candidates)
                            chosen.add(!detected.reviewOnlyKeys.contains(ScheduleOcrFusion.key(candidate)));
                        show(5);'''
    new='''                        // Preserve the unchecked state of each supplemental OCR
                        // reading BEFORE a spelling correction changes its fingerprint.
                        chosen.clear();
                        for(ScheduleEntry candidate:detected.candidates){
                            boolean optional=detected.reviewOnlyKeys.contains(
                                ScheduleOcrFusion.key(candidate));
                            chosen.add(!optional);
                            String cleaned=ScheduleCourseSemanticGuard.cleanOcrName(candidate.course);
                            if(!cleaned.equals(candidate.course)){
                                detected.uncertain.add("Corrección interna de texto OCR: «"+
                                    candidate.course+"» → «"+cleaned+
                                    "». Revisa la propuesta comparándola con la foto.");
                                candidate.course=cleaned;
                            }
                        }
                        ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all(profileId));
                        show(5);'''
    s=once(s,old,new,"OCR label cleanup and optional selections")
    s=once(s,
       '''        if(detected!=null){
            top.addView(txt(manualMode?''',
       '''        if(detected!=null){
            if(!manualMode&&photoPreview!=null&&!photoPreview.isRecycled()){
                top.addView(txt("Vista previa de la fotografía · Los contornos marcan "+
                    "áreas detectadas, no identificaciones definitivas.",12,MUTED,false));
                space(top,8);
                ImageView visual=new ImageView(this);
                visual.setImageBitmap(photoPreview);
                visual.setAdjustViewBounds(true);
                visual.setScaleType(ImageView.ScaleType.FIT_CENTER);
                visual.setMaxHeight(dp(285));
                top.addView(visual,new LinearLayout.LayoutParams(-1,-2));
                space(top,8);
                top.addView(btn("Ampliar fotografía para revisar bloques",()->
                    showPhotoPreview(),false));
                space(top,8);
            }
            top.addView(txt(manualMode?''',
       "review preview")
    s=once(s,
       '''            if(detected.reviewOnlyKeys.contains(ScheduleOcrFusion.key(s)))
                c.addView(txt("Lectura adicional · COMPRUEBA EN LA FOTO antes de seleccionar",''',
       '''            if(!chosen.get(i))
                c.addView(txt("Lectura adicional · COMPRUEBA EN LA FOTO antes de seleccionar",''',
       "option marker from stable selection")
    s=once(s,
       '''                    confirmPhotoWarnings(approved,()->confirmPhotoName(approved));''',
       '''                    confirmPhotoWarnings(approved,()->
                        confirmPhotoGroupSummary(approved,()->
                            confirmPhotoName(approved)));''',
       "final aggregate QA")
    s=once(s,
       '''            pair.relation==ScheduleCourseRecognition.Relation.SHARED_WORD?
            "Se encontró una palabra común («"+
                ScheduleCourseRecognition.sharedKeyword(
                    approved.get(pair.earlier).course,approved.get(pair.later).course)+
                "»). Confirma si representan el mismo curso; no se unirán automáticamente.":''',
       '''            pair.relation==ScheduleCourseRecognition.Relation.LEVEL_UNCERTAIN?
            "Un título incluye nivel I/II y el otro no. Podrían ser cursos distintos. "+
                "Comprueba el nivel en la fotografía; no se unirán automáticamente.":
            pair.relation==ScheduleCourseRecognition.Relation.SHARED_WORD?
            "Comparten el concepto «"+
                ScheduleCourseSemanticGuard.sharedInformative(
                    approved.get(pair.earlier).course,approved.get(pair.later).course)+
                "». Comprueba si realmente es la misma asignatura.":''',
       "contextual review reason")
    s=once(s,
       '''        List<ScheduleEntry> classes=ScheduleDatabase.get(this).all(profileId);''',
       '''        List<ScheduleEntry> classes=ScheduleDatabase.get(this).all(profileId);''',
       "existing list no change") if False else s
    old='''head(bar,"Mis cursos",classes.size()+" sesiones semanales");space(bar,10);bar.addView(btn("+ Agregar clase",()->editor(null,null),true));'''
    new='''head(bar,"Mis cursos",classes.size()+" sesiones semanales");space(bar,10);
        bar.addView(btn("+ Agregar clase",()->editor(null,null),true));
        space(bar,8);
        bar.addView(btn("Revisar nombres duplicados del OCR",this::reviewSavedCourseNames,false));'''
    s=once(s,old,new,"existing saved-course repair entry")
    anchor="    private void courseList(){"
    if s.count(anchor)!=1:raise RuntimeError("courseList insertion anchor missing")
    extras='''    /** A preview of detected regions, not an invented geometric match to every course. */
    private static android.graphics.Bitmap buildPhotoPreview(android.graphics.Bitmap source,
            List<ScheduleGridInterpreter.Tile> tiles){
        int w=source.getWidth(),h=source.getHeight();
        float scale=Math.min(1f,Math.min(850f/w,1100f/h));
        int outW=Math.max(1,Math.round(w*scale));
        int outH=Math.max(1,Math.round(h*scale));
        android.graphics.Bitmap reduced=android.graphics.Bitmap.createScaledBitmap(
            source,outW,outH,true);
        android.graphics.Bitmap output=reduced.copy(android.graphics.Bitmap.Config.ARGB_8888,true);
        if(reduced!=source&&reduced!=output)reduced.recycle();
        android.graphics.Canvas canvas=new android.graphics.Canvas(output);
        android.graphics.Paint paint=new android.graphics.Paint(3);
        paint.setStyle(android.graphics.Paint.Style.STROKE);
        paint.setStrokeWidth(Math.max(2f,3f*scale));
        paint.setColor(0xff1976d2);
        if(tiles!=null)for(ScheduleGridInterpreter.Tile tile:tiles){
            canvas.drawRect(tile.left*scale,tile.top*scale,
                tile.right*scale,tile.bottom*scale,paint);
        }
        return output;
    }
    private void showPhotoPreview(){
        if(photoPreview==null||photoPreview.isRecycled())return;
        ImageView full=new ImageView(this);
        full.setImageBitmap(photoPreview);
        full.setAdjustViewBounds(true);
        full.setScaleType(ImageView.ScaleType.FIT_CENTER);
        ScrollView scroller=new ScrollView(this);
        scroller.setFillViewport(true);
        scroller.addView(full);
        scheduleDialog().setTitle("Fotografía original y bloques aproximados")
            .setMessage("Los contornos identifican áreas candidatas. Revisa "+
                "el texto, día y hora en las tarjetas antes de guardar.")
            .setView(scroller)
            .setPositiveButton("Volver a los cursos",null).show();
    }
    /** A final contextual review: one subject may contain several weekly sessions. */
    private void confirmPhotoGroupSummary(ArrayList<ScheduleEntry> approved,Runnable proceed){
        Map<String,List<ScheduleEntry>> groups=ScheduleCourseColors.groups(approved);
        StringBuilder message=new StringBuilder("Sesiones: "+approved.size()+
            " · Cursos detectados: "+groups.size()+"\\n\\n");
        for(List<ScheduleEntry> course:groups.values()){
            ScheduleEntry first=course.get(0);
            message.append("• ").append(first.course).append(" · ")
                .append(course.size()).append(course.size()==1?" sesión":" sesiones")
                .append("\\n");
            if(message.length()>950){message.append("…\\n");break;}
        }
        List<String> alerts=ScheduleCourseSemanticGuard.audit(approved);
        if(!alerts.isEmpty()){
            message.append("\\nRevisiones adicionales: ").append(alerts.size()).append("\\n");
            for(int i=0;i<Math.min(4,alerts.size());i++)
                message.append("• ").append(alerts.get(i)).append("\\n");
        }
        scheduleDialog().setTitle("Verificación final de los cursos")
            .setMessage(message.toString())
            .setNegativeButton("Volver a la fotografía",(d,w)->show(5))
            .setPositiveButton("Confirmar agrupación",(d,w)->proceed.run())
            .show();
    }
    /** Old incorrectly separated course groups change only after an explicit user choice. */
    private void reviewSavedCourseNames(){
        List<ScheduleEntry> all=ScheduleDatabase.get(this).all(profileId);
        LinkedHashMap<String,ScheduleEntry> names=new LinkedHashMap<>();
        for(ScheduleEntry item:all)
            names.putIfAbsent(ScheduleCourseColors.identity(item.course),item);
        ArrayList<ScheduleEntry> distinct=new ArrayList<>(names.values());
        SchedulePhotoReview.Pair pair=SchedulePhotoReview.nextPair(distinct,
            new HashSet<Integer>(),new HashSet<String>());
        if(pair==null){
            scheduleDialog().setTitle("Revisión de cursos")
                .setMessage("No se encontraron nombres suficientemente similares "+
                    "para sugerir una agrupación. Puedes corregir cada curso con el lápiz.")
                .setPositiveButton("Entendido",null).show();
            return;
        }
        ScheduleEntry left=distinct.get(pair.earlier),right=distinct.get(pair.later);
        EditText canonical=new EditText(this);
        canonical.setSingleLine(true);
        canonical.setText(ScheduleCourseRecognition.preferred(left.course,right.course));
        canonical.setSelectAllOnFocus(true);
        LinearLayout panel=col();
        panel.setPadding(dp(18),dp(8),dp(18),dp(12));
        panel.addView(txt("Posibles nombres OCR del mismo curso:\\n"+
            "1. "+left.course+"\\n2. "+right.course,14,INK,true));
        space(panel,9);
        panel.addView(txt("Comprueba ambos nombres antes de unir. "+
            "Se conservarán los días, las horas y las aulas de todas las sesiones.",
            12,MUTED,false));
        space(panel,9);panel.addView(canonical);
        AlertDialog dialog=scheduleDialog().setTitle("Corregir cursos ya guardados")
            .setView(panel).setNegativeButton("Mantener separados",null)
            .setPositiveButton("Unir bajo este nombre",null).create();
        dialog.setOnShowListener(v->dialog.getButton(-1).setOnClickListener(button->{
            String name=canonical.getText().toString().trim();
            if(name.length()<2||name.length()>120){canonical.setError("Nombre inválido");return;}
            try{
                int updated=ScheduleDatabase.get(this).mergeCourseNames(
                    profileId,left.course,right.course,name);
                AcademicSchedules.syncFromSessions(this,profileId);
                ScheduleReminders.rebuild(this);
                toast("Nombre confirmado · "+updated+" sesiones conservadas");
                dialog.dismiss();show(3);
            }catch(RuntimeException error){
                toast("No se pudo unir. Los datos se mantienen sin cambios.");
            }
        }));
        dialog.show();
    }

'''
    s=s.replace(anchor,extras+anchor,1)
    return s

def database(s):
    marker="    /** Legacy caller: uses selected profile, refuses silently mixing unassigned sessions. */"
    if s.count(marker)!=1:raise RuntimeError("DB insertion anchor missing")
    insert='''    /** Explicit transaction: merges two reviewed OCR names inside ONE profile.
     * Session IDs, hours, rooms, teachers and reminders remain unchanged. */
    public synchronized int mergeCourseNames(String profileId,String first,String second,
                                              String canonical){
        if(profileId==null||profileId.trim().isEmpty()||canonical==null||
           canonical.trim().length()<2||canonical.trim().length()>120)
            throw new IllegalArgumentException("Curso u horario inválidos");
        if(ScheduleCourseRecognition.compare(first,second)==
           ScheduleCourseRecognition.Relation.DIFFERENT)
            throw new IllegalArgumentException("Cursos incompatibles");
        List<ScheduleEntry> source=all(profileId);
        int count=0;
        int color=ScheduleCourseColors.deterministic(canonical);
        for(ScheduleEntry item:source)if(ScheduleCourseColors.same(item.course,first)){
            color=item.color;break;
        }
        SQLiteDatabase db=getWritableDatabase();
        db.beginTransaction();
        try{
            for(ScheduleEntry item:source){
                if(!ScheduleCourseColors.same(item.course,first)&&
                   !ScheduleCourseColors.same(item.course,second))continue;
                ContentValues cv=new ContentValues();
                cv.put("course",canonical.trim());cv.put("color",color);
                int updated=db.update("sessions",cv,"id=? AND schedule_id=?",
                    new String[]{Long.toString(item.id),profileId});
                if(updated!=1)throw new IllegalStateException("No se guardó el grupo completo");
                count++;
            }
            if(count<2)throw new IllegalStateException("No hay sesiones para agrupar");
            db.setTransactionSuccessful();
        }finally{db.endTransaction();}
        return count;
    }
'''
    return s.replace(marker,insert+marker,1)

def main():
    gradle=GRADLE.read_text()
    if gradle.count("versionCode 72") and gradle.count("versionName '3.15.5'"):
        if (ROOT/"ScheduleCourseSemanticGuard.java").read_bytes()!=(STAGE/"ScheduleCourseSemanticGuard.java").read_bytes():
            raise RuntimeError("Version 3.15.5 sources do not match")
        print("PASS: photo semantic guard already installed");return
    if gradle.count("versionCode 71")!=1 or gradle.count("versionName '3.15.4'")!=1:
        raise RuntimeError("This migration requires 3.15.4 (versionCode 71)")
    files={
        ROOT/"ScheduleCourseRecognition.java":recognition,
        ROOT/"SchedulePhotoReview.java":photo_review,
        ROOT/"ScheduleActivity.java":activity,
        ROOT/"ScheduleDatabase.java":database
    }
    new={(ROOT/"ScheduleCourseSemanticGuard.java"):(STAGE/"ScheduleCourseSemanticGuard.java").read_bytes()}
    for p,fn in files.items():
        new[p]=fn(p.read_text()).encode("utf-8")
    new[GRADLE]=gradle.replace("versionCode 71","versionCode 72",1).replace(
        "versionName '3.15.4'","versionName '3.15.5'",1).encode("utf-8")
    photo_hash={p:hashlib.sha256(p.read_bytes()).digest() for p in PHOTOS}
    orig={p:p.read_bytes() if p.exists() else None for p in new}
    modified=[]
    try:
        for p,content in new.items():atomic(p,content);modified.append(p)
        if any(hashlib.sha256(p.read_bytes()).digest()!=digest for p,digest in photo_hash.items()):
            raise RuntimeError("PhotoWidget files unexpectedly changed")
    except BaseException:
        for p in reversed(modified):
            if orig[p] is None:p.unlink(missing_ok=True)
            else:atomic(p,orig[p])
        raise
    print("PASS: contextual photo review, preview, old-course merge and data validation")
    print("PASS: static photo widget unchanged; Agenda Clara 3.15.5 versionCode 72")

if __name__=="__main__":
    main()
