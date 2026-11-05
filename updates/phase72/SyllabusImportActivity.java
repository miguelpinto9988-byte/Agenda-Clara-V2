package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.app.TimePickerDialog;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import java.security.MessageDigest;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;

/** User-confirmed syllabus import. No external upload, no auto-save on file selection. */
public final class SyllabusImportActivity extends Activity {
    private static final int REQUEST_DOCUMENT=7402;
    private final ArrayList<Row> items=new ArrayList<>();
    private AcademicCourseMatcher.Course selectedCourse;
    private String documentTitle="";
    private LinearLayout body;
    private Spinner advance;
    private static final class Row {
        final SyllabusEventParser.Event event;
        boolean selected=true;
        LocalDate date;
        LocalTime time=LocalTime.of(23,59);
        Row(SyllabusEventParser.Event e){event=e;date=e.date;}
    }
    private int dp(int n){return UiDesign.dp(this,n);}
    private LinearLayout column(){LinearLayout x=new LinearLayout(this);x.setOrientation(1);return x;}
    private TextView label(String value,int size,boolean bold){
        TextView v=new TextView(this);v.setText(value);v.setTextSize(size);
        v.setTextColor(bold?UiDesign.INK:UiDesign.MUTED);UiDesign.text(v,bold);return v;
    }
    private Button button(String text,boolean primary){
        Button b=new Button(this);b.setText(text);UiDesign.button(b,primary);return b;
    }
    private LinearLayout card(){
        LinearLayout c=column();c.setPadding(dp(15),dp(15),dp(15),dp(15));
        c.setBackground(UiDesign.shape(this,0xffffffff,20,UiDesign.BORDER));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);
        p.bottomMargin=dp(13);body.addView(c,p);return c;
    }
    private void gap(LinearLayout root,int n){View v=new View(this);root.addView(v,new LinearLayout.LayoutParams(1,dp(n)));}
    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        getWindow().setStatusBarColor(UiDesign.BG);
        getWindow().setNavigationBarColor(UiDesign.BG);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);
        body=column();body.setPadding(dp(16),dp(16),dp(16),dp(25));
        body.setBackgroundColor(UiDesign.BG);scroll.addView(body);setContentView(scroll);
        landing();
        if(getIntent().getBooleanExtra("manual",false))chooseCourseForManual();
    }
    private void landing(){
        body.removeAllViews();
        body.addView(label("Exámenes y sílabos",24,true));
        body.addView(label("Revisa fechas y cursos antes de crear recordatorios.",13,false));
        gap(body,16);
        LinearLayout panel=card();
        Button upload=button("Subir sílabo · PDF, DOC o DOCX",true);
        upload.setOnClickListener(v->openDocument());panel.addView(upload);
        gap(panel,10);
        Button manual=button("Agregar evaluación manualmente",false);
        manual.setOnClickListener(v->chooseCourseForManual());panel.addView(manual);
        if(!documentTitle.isEmpty()){
            gap(body,8);body.addView(label("Documento: "+documentTitle,13,true));
        }
    }
    private void openDocument(){
        Intent pick=new Intent(Intent.ACTION_OPEN_DOCUMENT);
        pick.addCategory(Intent.CATEGORY_OPENABLE);
        pick.setType("*/*");
        pick.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{
                "application/pdf","application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"});
        startActivityForResult(pick,REQUEST_DOCUMENT);
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if(request!=REQUEST_DOCUMENT||result!=RESULT_OK||data==null||data.getData()==null)return;
        final Uri uri=data.getData();
        documentTitle=filename(uri);
        body.removeAllViews();
        body.addView(label("Leyendo documento localmente…",17,true));
        new Thread(()->{
            try{
                List<SyllabusEventParser.Page> pages=
                        SyllabusDocumentReader.read(this,uri,documentTitle);
                List<SyllabusEventParser.Event> extracted=SyllabusEventParser.extract(pages);
                StringBuilder lead=new StringBuilder();
                for(SyllabusEventParser.Page p:pages){
                    if(p.text.trim().isEmpty())continue;
                    lead.append(p.text.substring(0,Math.min(2500,p.text.length()))).append('\n');
                    if(lead.length()>7000)break;
                }
                runOnUiThread(()->{
                    items.clear();
                    for(SyllabusEventParser.Event event:extracted)items.add(new Row(event));
                    showEvents();
                    if(selectedCourse==null)AcademicCourseRouting.review(this,lead.toString(),
                            "General",match->{if(match!=null){selectedCourse=match;showEvents();}
                                else AcademicCourseRouting.chooseAny(this,course->{
                                    selectedCourse=course;showEvents();
                                });
                            });
                });
            }catch(Exception e){
                runOnUiThread(()->new AlertDialog.Builder(this,R.style.DialogTheme)
                        .setTitle("No se pudo leer el documento")
                        .setMessage(e.getMessage()==null?"Prueba con otro archivo o usa el registro manual."
                                :e.getMessage())
                        .setPositiveButton("Entendido",(d,w)->landing()).show());
            }
        },"syllabus-local-read").start();
    }
    private String filename(Uri uri){
        String name="";
        try(Cursor c=getContentResolver().query(uri,new String[]{OpenableColumns.DISPLAY_NAME},
                null,null,null)){
            if(c!=null&&c.moveToFirst())name=c.getString(0);
        }catch(Exception ignored){}
        if(name==null||name.isEmpty())name=uri.getLastPathSegment();
        return name==null?"documento.pdf":name;
    }
    private void chooseCourseForManual(){
        AcademicCourseRouting.chooseAny(this,course->{
            selectedCourse=course;items.clear();
            SyllabusEventParser.Event item=new SyllabusEventParser.Event(
                    "Nueva evaluación","Evaluación",null,0,"Registro manual");
            items.add(new Row(item));
            documentTitle="Registro manual";
            showEvents();
        });
    }
    private void showEvents(){
        body.removeAllViews();
        body.addView(label("Revisar evaluaciones",24,true));
        body.addView(label(documentTitle,12,false));
        gap(body,12);
        LinearLayout courseCard=card();
        courseCard.addView(label("Curso de destino",17,true));
        Button choose=button(selectedCourse==null?"Elegir curso":
                selectedCourse.name+" · "+selectedCourse.category,false);
        choose.setOnClickListener(v->AcademicCourseRouting.chooseAny(this,course->{
            selectedCourse=course;showEvents();
        }));
        courseCard.addView(choose);
        if(items.isEmpty()){
            LinearLayout empty=card();
            empty.addView(label("No se detectaron exámenes con texto legible.",15,true));
            empty.addView(label("Si el PDF es una imagen, puede requerir OCR. También puedes añadir una evaluación manual.",12,false));
        }
        LinearLayout review=card();
        review.addView(label("Eventos encontrados: "+items.size(),17,true));
        review.addView(label("Desmarca lo que no corresponda. Las fechas ausentes deben seleccionarse manualmente.",12,false));
        for(Row row:items){
            gap(review,12);
            CheckBox check=new CheckBox(this);check.setChecked(row.selected);
            check.setText(row.event.title);
            check.setTextColor(UiDesign.INK);
            check.setMinHeight(dp(48));
            check.setOnCheckedChangeListener((v,on)->row.selected=on);
            review.addView(check);
            review.addView(label(row.event.page>0?"Fuente: página "+row.event.page:
                    "Fuente: texto del documento o registro manual",12,false));
            Button date=button(row.date==null?"Elegir fecha (obligatorio)":
                    "Fecha: "+row.date,false);
            date.setOnClickListener(v->{
                LocalDate initial=row.date==null?LocalDate.now():row.date;
                new DatePickerDialog(this,(picker,y,m,d)->{
                    row.date=LocalDate.of(y,m+1,d);showEvents();
                },initial.getYear(),initial.getMonthValue()-1,initial.getDayOfMonth()).show();
            });
            review.addView(date);
            Button time=button("Hora: "+row.time+" · editar",false);
            time.setOnClickListener(v->new TimePickerDialog(this,(picker,h,m)->{
                row.time=LocalTime.of(h,m);showEvents();
            },row.time.getHour(),row.time.getMinute(),true).show());
            review.addView(time);
        }
        if(!items.isEmpty()){
            LinearLayout settings=card();
            settings.addView(label("Avisarme antes",17,true));
            advance=new Spinner(this);
            advance.setAdapter(new ArrayAdapter<String>(this,
                    android.R.layout.simple_spinner_dropdown_item,
                    new String[]{"10 días y 12 horas antes","7 días antes"}));
            settings.addView(advance);
            settings.addView(label("Se avisará cuando Android permita notificaciones. Si la anticipación ya pasó, no se generará un aviso retroactivo.",12,false));
            Button save=button("Crear tareas y recordatorios",true);
            save.setOnClickListener(v->confirmSave());
            settings.addView(save);
        }
    }
    private void confirmSave(){
        if(selectedCourse==null){
            new AlertDialog.Builder(this,R.style.DialogTheme).setMessage(
                    "Primero elige a qué curso pertenecen las evaluaciones.")
                    .setPositiveButton("Entendido",null).show();return;
        }
        int checked=0;for(Row row:items)if(row.selected){
            checked++;
            if(row.date==null){
                new AlertDialog.Builder(this,R.style.DialogTheme).setMessage(
                        "Hay evaluaciones seleccionadas sin fecha. Corrige esas fechas antes de guardarlas.")
                        .setPositiveButton("Entendido",null).show();return;
            }
        }
        if(checked==0)return;
        int count=checked;
        int offset=advance.getSelectedItemPosition()==0?15120:10080;
        new AlertDialog.Builder(this,R.style.DialogTheme)
                .setTitle("Confirmar "+count+" tareas académicas")
                .setMessage("Se utilizará la hora indicada en cada evaluación. "+
                        "El recordatorio será "+(offset==15120?"10 días y 12 horas":"7 días")+
                        " antes. Los eventos duplicados ya guardados se omitirán.")
                .setNegativeButton("Revisar",null)
                .setPositiveButton("Crear",(d,w)->saveSelected(offset)).show();
    }
    private static String sha(String value){
        try{
            byte[] hash=MessageDigest.getInstance("SHA-256").digest(value.getBytes("UTF-8"));
            StringBuilder out=new StringBuilder();
            for(int i=0;i<18;i++)out.append(String.format(java.util.Locale.ROOT,"%02x",hash[i]&255));
            return out.toString();
        }catch(Exception e){throw new IllegalStateException(e);}
    }
    private void saveSelected(int offset){
        int saved=0,duplicate=0;
        for(Row row:items){
            if(!row.selected||row.date==null)continue;
            long due=row.date.atTime(row.time).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
            String origin="syllabus:"+sha(selectedCourse.profileId+"|"+selectedCourse.name+"|"+
                    AcademicCourseMatcher.fold(row.event.title)+"|"+row.date);
            if(Store.get(this).findOrigin(origin)!=null){duplicate++;continue;}
            Task task=new Task();task.title=row.event.title;
            task.category=selectedCourse.category;
            task.notes="Curso: "+selectedCourse.name+"\n"+
                    "Documento: "+documentTitle+"\n"+
                    (row.event.page>0?"Página: "+row.event.page+"\n":"")+
                    "Fragmento: "+row.event.sourceText;
            task.source="Sílabo · Plan de estudio";task.originKey=origin;
            task.due=due;task.offsets=String.valueOf(offset);
            try{
                Store.get(this).save(task);
                AcademicTaskLinks.get(this).assign(task.id,
                        selectedCourse.profileId,selectedCourse.name);
                Reminders.schedule(this,task);
                saved++;
            }catch(Exception e){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                        .setTitle("Importación incompleta")
                        .setMessage("Se crearon "+saved+" tareas. Revisa la lista antes de repetir la importación.")
                        .setPositiveButton("Entendido",null).show();
                TaskWidget.refresh(this);return;
            }
        }
        TaskWidget.refresh(this);
        new AlertDialog.Builder(this,R.style.DialogTheme)
                .setTitle("Importación revisada")
                .setMessage(saved+" tareas creadas · "+duplicate+" duplicadas omitidas.")
                .setPositiveButton("Cerrar",(d,w)->finish()).show();
    }
}
