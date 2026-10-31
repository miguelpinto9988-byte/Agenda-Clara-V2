package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import android.widget.TextView;
import java.util.function.IntConsumer;

/** Recurrence of notifications only, never a second copy of a task.
 * The existing scheduler still stops reminders at due time or task completion.
 */
public final class ModernRepeat {
    private ModernRepeat(){}
    private static final int[] MINUTES={0,1440,10080,43200};
    private static final String[] LABELS={"No se repite","Diariamente","Semanalmente","Cada 30 días"};
    private static int dp(Activity a,int n){return UiDesign.dp(a,n);}
    private static LinearLayout column(Activity a){
        LinearLayout v=new LinearLayout(a);v.setOrientation(1);return v;
    }
    private static TextView label(Activity a,String title,int size){
        TextView t=new TextView(a);t.setText(title);t.setTextSize(size);t.setTextColor(UiDesign.INK);
        t.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));return t;
    }
    public static String title(int minutes){
        if(minutes==0)return "No se repite";
        for(int i=1;i<MINUTES.length;i++)if(MINUTES[i]==minutes)return LABELS[i];
        if(minutes%10080==0)return "Cada "+(minutes/10080)+" semanas";
        if(minutes%1440==0)return "Cada "+(minutes/1440)+" días";
        if(minutes%60==0)return "Cada "+(minutes/60)+" horas";
        return "Cada "+minutes+" minutos";
    }
    public static void show(Activity a,int current,IntConsumer selected){
        LinearLayout layout=column(a);
        layout.setPadding(dp(a,16),dp(a,10),dp(a,16),dp(a,20));
        layout.addView(label(a,"¿Cada cuánto repetir el aviso?",15));
        final AlertDialog[] ref={null};
        for(int i=0;i<MINUTES.length;i++){
            final int minutes=MINUTES[i];final String title=LABELS[i];
            LinearLayout line=new LinearLayout(a);line.setGravity(Gravity.CENTER_VERTICAL);
            line.setOrientation(0);line.setPadding(dp(a,12),dp(a,6),dp(a,12),dp(a,6));
            line.setBackground(UiDesign.tintedBackground(a,minutes==current?ModernGlyph.BLUE:UiDesign.BORDER,14,minutes==current?17:7));
            android.widget.ImageView symbol=ApprovedPng.view(a,i==0?"notes":i==1?"repeat":"date",26);
            line.addView(symbol,new LinearLayout.LayoutParams(dp(a,36),dp(a,36)));
            TextView text=label(a,title,15);
            LinearLayout.LayoutParams nameParams=new LinearLayout.LayoutParams(0,-2,1);
            nameParams.leftMargin=dp(a,12);line.addView(text,nameParams);
            if(minutes==current)line.addView(label(a,"✓",22));
            line.setContentDescription(title);
            line.setOnClickListener(v->{selected.accept(minutes);ref[0].dismiss();});
            LinearLayout.LayoutParams itemParams=new LinearLayout.LayoutParams(-1,dp(a,56));
            itemParams.bottomMargin=dp(a,8);layout.addView(line,itemParams);
        }
        Button custom=new Button(a);custom.setAllCaps(false);
        custom.setText("Personalizada  ›");custom.setTextSize(15);
        UiDesign.button(custom,false);ApprovedPng.button(custom,"settings",23);
        layout.addView(custom,new LinearLayout.LayoutParams(-1,dp(a,54)));
        TextView guide=label(a,"Los avisos terminan al vencer la tarea o al marcarla como completada.",12);
        guide.setTextColor(UiDesign.MUTED);
        LinearLayout.LayoutParams guideParams=new LinearLayout.LayoutParams(-1,-2);guideParams.topMargin=dp(a,12);
        layout.addView(guide,guideParams);
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);
        scroll.addView(layout);
        AlertDialog d=new AlertDialog.Builder(a,R.style.DialogTheme).setTitle("Repetición del aviso")
            .setView(scroll).setNegativeButton("Cancelar",null).create();
        ref[0]=d;d.setOnShowListener(v->WindowLayout.boundDialog(a,d));
        custom.setOnClickListener(v->{
            d.dismiss();showCustom(a,current,selected);
        });
        d.show();
    }
    public static void showCustom(Activity a,int current,IntConsumer selected){
        LinearLayout layout=column(a);
        layout.setPadding(dp(a,16),dp(a,12),dp(a,16),dp(a,24));
        layout.addView(label(a,"Repetir cada",16));
        EditText quantity=new EditText(a);quantity.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        quantity.setSingleLine(true);quantity.setText(String.valueOf(Math.max(1,current>0?current/1440:1)));
        UiDesign.input(quantity);
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,54));lp.topMargin=dp(a,10);
        layout.addView(quantity,lp);
        Spinner unit=new Spinner(a);
        String[] units={"Minutos","Horas","Días","Semanas"};
        unit.setAdapter(new ArrayAdapter<String>(a,android.R.layout.simple_spinner_dropdown_item,units));
        unit.setSelection(current>=10080&&current%10080==0?3:current>=1440&&current%1440==0?2:current>=60&&current%60==0?1:0);
        LinearLayout.LayoutParams unitLp=new LinearLayout.LayoutParams(-1,dp(a,55));
        unitLp.topMargin=dp(a,10);layout.addView(unit,unitLp);
        layout.addView(label(a,"La repetición termina en la fecha límite de la tarea.",13));
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);scroll.addView(layout);
        AlertDialog d=new AlertDialog.Builder(a,R.style.DialogTheme).setTitle("Repetición personalizada")
            .setView(scroll).setNegativeButton("Cancelar",null).setPositiveButton("Listo",null).create();
        d.setOnShowListener(v->{
            WindowLayout.boundDialog(a,d);
            d.getButton(-1).setOnClickListener(view->{
                try{
                    long number=Long.parseLong(quantity.getText().toString());
                    long value=number*new int[]{1,60,1440,10080}[unit.getSelectedItemPosition()];
                    if(number<=0||value>5256000||value>Integer.MAX_VALUE)throw new NumberFormatException();
                    selected.accept((int)value);d.dismiss();
                }catch(NumberFormatException ex){quantity.setError("Introduce un intervalo entre 1 minuto y 10 años.");}
            });
        });
        d.show();
    }
}
