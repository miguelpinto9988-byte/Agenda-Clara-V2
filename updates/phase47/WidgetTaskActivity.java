package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.text.InputType;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

/** Companion window opened only by the widget. Not a background overlay or service. */
public final class WidgetTaskActivity extends Activity {
    public static final String ACTION_CREATE="pe.agendaclara.app.WIDGET_CREATE";
    private final int INK=0xff102457, MUTED=0xff5d719e, BLUE=0xff2458fb;
    private final Locale ES=new Locale("es","PE");
    private LinearLayout content;
    private ScrollView scroll;
    private int lastIme=-1;
    private int dp(int n){return UiDesign.dp(this,n);}

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE
            |WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        WindowManager.LayoutParams p=getWindow().getAttributes();p.dimAmount=.42f;getWindow().setAttributes(p);
        if(!ACTION_CREATE.equals(getIntent().getAction())){finish();return;}
        renderSelector();
    }
    @Override protected void onDestroy(){VoiceQuickTask.closeFor(this);super.onDestroy();}
    @Override public void onRequestPermissionsResult(int request,String[] permissions,int[] grants){
        super.onRequestPermissionsResult(request,permissions,grants);
        VoiceQuickTask.permissionResult(this,request,permissions,grants);
    }
    void voiceFinished(){if(!isFinishing())finish();}
    private GradientDrawable background(int color,int radius,int border){
        GradientDrawable b=new GradientDrawable();b.setColor(color);b.setCornerRadius(dp(radius));
        if(border!=0)b.setStroke(dp(1),border);
        return b;
    }
    private TextView text(String value,int size,int color,boolean bold){
        TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);
        if(bold)t.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);
        return t;
    }
    private LinearLayout column(){LinearLayout c=new LinearLayout(this);c.setOrientation(1);return c;}
    private void gap(LinearLayout c,int n){c.addView(new View(this),new LinearLayout.LayoutParams(1,dp(n)));}
    private LinearLayout row(){LinearLayout c=new LinearLayout(this);c.setOrientation(0);c.setGravity(Gravity.CENTER_VERTICAL);return c;}
    private void putIcon(LinearLayout r,String icon,int size){
        ImageView image=ApprovedPng.view(this,icon,size);
        r.addView(image,new LinearLayout.LayoutParams(dp(size),dp(size)));
    }
    private Button button(String value,boolean primary){
        Button b=new Button(this);b.setText(value);b.setAllCaps(false);b.setTextSize(15);
        b.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);
        b.setTextColor(primary?Color.WHITE:BLUE);
        b.setBackground(background(primary?BLUE:0xffedf2ff,17,primary?0:0xffd6e2ff));
        b.setMinHeight(dp(52));return b;
    }
    private void mount(){
        scroll=new ScrollView(this);scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(false);
        scroll.setClipToPadding(false);scroll.setPadding(dp(18),dp(18),dp(18),dp(20));
        content=column();content.setPadding(dp(18),dp(20),dp(18),dp(22));
        content.setBackground(background(0xfffafdff,26,0xffcfdcff));
        scroll.addView(content);setContentView(scroll);
        getWindow().setGravity(Gravity.CENTER);applyWindowSize();
        scroll.setOnApplyWindowInsetsListener((v,insets)->{
            int ime=Build.VERSION.SDK_INT>=30 && insets.isVisible(WindowInsets.Type.ime())?1:0;
            if(ime!=lastIme){lastIme=ime;scroll.post(()->{
                if(!isFinishing()){applyWindowSize();scroll.requestLayout();}
            });}
            return insets;
        });
        scroll.getViewTreeObserver().addOnGlobalLayoutListener(()->{
            if(!isFinishing()&&scroll!=null&&scroll.getParent()!=null){
                WindowManager.LayoutParams p=getWindow().getAttributes();
                if(p.height!=WindowManager.LayoutParams.WRAP_CONTENT)
                    getWindow().setLayout(p.width,WindowManager.LayoutParams.WRAP_CONTENT);
            }
        });
    }
    private void applyWindowSize(){
        int screen=getResources().getDisplayMetrics().widthPixels;
        int width=Math.min(screen-dp(22),dp(440));
        getWindow().setLayout(width,WindowManager.LayoutParams.WRAP_CONTENT);
    }
    private void header(String heading,String subtitle){
        LinearLayout top=row();putIcon(top,"widget_brand",54);
        LinearLayout titles=column();titles.setPadding(dp(11),0,0,0);
        titles.addView(text(heading,23,INK,true));titles.addView(text(subtitle,13,MUTED,false));
        top.addView(titles,new LinearLayout.LayoutParams(0,-2,1));
        TextView x=text("×",31,INK,true);x.setGravity(Gravity.CENTER);
        x.setBackground(background(0xffedf3ff,15,0xffd9e5ff));x.setContentDescription("Cerrar ventana flotante");
        top.addView(x,new LinearLayout.LayoutParams(dp(42),dp(42)));
        x.setOnClickListener(v->finish());content.addView(top);
    }
    private void renderSelector(){
        mount();header("Nueva tarea","Elige cómo quieres agregarla");gap(content,18);
        choice("widget_voice","Tarea rápida por voz","Dicta tu tarea y la interpretaré",true,()->{
            scroll.setVisibility(View.INVISIBLE);
            VoiceQuickTask.show(this);
        });gap(content,13);
        choice("widget_manual","Tarea normal","Completa los detalles manualmente",false,this::renderNormal);
    }
    private void choice(String icon,String name,String hint,boolean primary,Runnable action){
        LinearLayout item=row();item.setPadding(dp(12),dp(13),dp(12),dp(13));
        item.setBackground(background(primary?0xfff1efff:Color.WHITE,20,primary?0xff9363ff:0xffd6e2f6));
        putIcon(item,icon,62);
        LinearLayout labels=column();labels.setPadding(dp(12),0,0,0);
        labels.addView(text(name,18,INK,true));labels.addView(text(hint,12,MUTED,false));
        if(primary)labels.addView(text("⚡ Más rápida",12,0xff7940df,true));
        item.addView(labels,new LinearLayout.LayoutParams(0,-2,1));
        TextView arrow=text("›",31,BLUE,true);arrow.setGravity(Gravity.CENTER);item.addView(arrow);
        item.setContentDescription(name+". "+hint);item.setOnClickListener(v->action.run());
        content.addView(item);
    }
    private EditText input(String hint,boolean multiline){
        EditText e=new EditText(this);e.setTextSize(15);e.setTextColor(INK);e.setHint(hint);
        e.setBackground(background(Color.WHITE,12,0xffd8e3ff));
        e.setPadding(dp(13),dp(9),dp(13),dp(9));
        if(multiline){
            e.setMinLines(2);e.setMaxLines(4);
            e.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_MULTI_LINE|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        }else{
            e.setSingleLine(true);e.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        }
        return e;
    }
    private void label(String icon,String title){
        LinearLayout r=row();putIcon(r,icon,29);
        TextView t=text(title,15,INK,true);t.setPadding(dp(10),0,0,0);r.addView(t);
        content.addView(r);gap(content,5);
    }
    private void renderNormal(){
        mount();header("Tarea normal","Formulario rápido sobre tu pantalla");gap(content,15);
        label("widget_manual","Título");
        EditText title=input("¿Qué necesitas hacer?",false);content.addView(title);gap(content,12);
        label("voice_notes","Detalles (opcional)");
        EditText notes=input("Información adicional",true);content.addView(notes);gap(content,12);
        final LocalDate[] date={LocalDate.now()};final LocalTime[] time={LocalTime.of(23,59)};
        label("voice_calendar","Fecha límite");
        Button dateBtn=button("Hoy",false);content.addView(dateBtn);gap(content,12);
        label("voice_clock","Hora límite");
        Button timeBtn=button("11:59 p. m.",false);content.addView(timeBtn);gap(content,10);
        DateTimeFormatter dateFmt=DateTimeFormatter.ofPattern("EEEE d MMM yyyy",ES);
        DateTimeFormatter timeFmt=DateTimeFormatter.ofPattern("h:mm a",ES);
        dateBtn.setText(date[0].format(dateFmt));
        dateBtn.setOnClickListener(v->ModernPickers.showDate(this,date[0],chosen->{
            date[0]=chosen;dateBtn.setText(chosen.format(dateFmt));
        }));
        timeBtn.setOnClickListener(v->ModernPickers.showTime(this,time[0],chosen->{
            time[0]=chosen;timeBtn.setText(chosen.format(timeFmt));
        }));
        CheckBox reminder=new CheckBox(this);
        reminder.setText("Recordatorios: 1 día y 1 hora antes");
        reminder.setTextColor(INK);reminder.setTextSize(14);reminder.setChecked(true);
        reminder.setButtonTintList(ColorStateList.valueOf(BLUE));
        content.addView(reminder);gap(content,15);
        LinearLayout buttons=row();Button back=button("Volver",false),save=button("Guardar tarea",true);
        LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,dp(54),1);a.rightMargin=dp(8);
        buttons.addView(back,a);buttons.addView(save,new LinearLayout.LayoutParams(0,dp(54),1));
        content.addView(buttons);back.setOnClickListener(v->renderSelector());
        save.setOnClickListener(v->{
            String name=title.getText().toString().trim();
            if(name.isEmpty()){title.setError("Escribe un título");title.requestFocus();return;}
            long due=date[0].atTime(time[0]).atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
            if(due<=System.currentTimeMillis()){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setMessage("Elige una fecha y hora posteriores al momento actual.")
                    .setPositiveButton("Entendido",null).show();return;
            }
            Task task=new Task();task.title=name;task.notes=notes.getText().toString().trim();
            task.category="General";task.source="Widget · Tarea normal";task.due=due;
            task.offsets=reminder.isChecked()?"1440,60,0":"0";
            try{
                Store.get(this).save(task);Reminders.schedule(this,task);TaskWidget.refresh(this);finish();
            }catch(Exception ex){
                new AlertDialog.Builder(this,R.style.DialogTheme)
                    .setMessage("No se pudo guardar la tarea. Intenta nuevamente.")
                    .setPositiveButton("Entendido",null).show();
            }
        });
    }
}
