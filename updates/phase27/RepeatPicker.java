package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.graphics.Typeface;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.function.Consumer;

/** User-facing repeat of NOTIFICATIONS, never a repeat of the task itself. */
public final class RepeatPicker {
    private RepeatPicker(){}
    public static String label(int minutes){
        if(minutes==0)return "No se repite";
        if(minutes==-1)return "Cada mes";
        if(minutes==1440)return "Cada día";
        if(minutes==10080)return "Cada semana";
        if(minutes==43200)return "Cada 30 días";
        if(minutes%10080==0)return "Cada "+(minutes/10080)+" semanas";
        if(minutes%1440==0)return "Cada "+(minutes/1440)+" días";
        if(minutes%60==0)return "Cada "+(minutes/60)+" horas";
        return "Cada "+minutes+" minutos";
    }
    static int dp(Activity a,int n){return UiDesign.dp(a,n);}
    static TextView text(Activity a,String s,int size){
        TextView t=new TextView(a);t.setText(s);t.setTextSize(size);t.setTextColor(UiDesign.INK);
        t.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));return t;
    }
    static LinearLayout content(Activity a){
        LinearLayout box=new LinearLayout(a);box.setOrientation(1);box.setPadding(dp(a,18),dp(a,14),dp(a,18),dp(a,18));return box;
    }
    public static void show(Activity a,int current,Consumer<Integer> chosen){
        LinearLayout box=content(a);
        box.addView(text(a,"¿Cada cuánto repetir los avisos?",15));
        TextView tip=text(a,"Los avisos se detienen al completar o vencer la tarea.",12);tip.setTextColor(UiDesign.MUTED);
        tip.setPadding(0,dp(a,7),0,dp(a,12));box.addView(tip);
        final int[] values={0,1440,10080,-1};
        final String[] names={"No se repite","Diariamente","Semanalmente","Mensualmente"};
        final String[] icons={"check","repeat","date","calendar"};
        final int[] selected={current};
        for(int index=0;index<values.length;index++){
            final int value=values[index];
            LinearLayout card=new LinearLayout(a);card.setGravity(Gravity.CENTER_VERTICAL);
            card.setPadding(dp(a,12),dp(a,10),dp(a,12),dp(a,10));
            boolean active=current==value;
            card.setBackground(UiDesign.tintedBackground(a,
                active?UiDesign.BLUE:0xffc7d7ed,15,active?22:9));
            ImageView icon=PngIcons.view(a,icons[index],26);
            card.addView(icon,new LinearLayout.LayoutParams(dp(a,30),dp(a,30)));
            TextView name=text(a,"  "+names[index],14);
            card.addView(name,new LinearLayout.LayoutParams(0,-2,1));
            if(active){TextView mark=text(a,"✓",19);mark.setTextColor(UiDesign.BLUE);card.addView(mark);}
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,57));
            lp.bottomMargin=dp(a,9);box.addView(card,lp);
            card.setOnClickListener(v->{selected[0]=value;chosen.accept(value);});
        }
        Button custom=new Button(a);custom.setAllCaps(false);custom.setText("Personalizada  ›");
        UiDesign.button(custom,false);PngIcons.button(custom,"settings",22);
        box.addView(custom,new LinearLayout.LayoutParams(-1,dp(a,52)));
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);scroll.addView(box);
        AlertDialog dialog=new AlertDialog.Builder(a,R.style.DialogTheme).setTitle("Repetición del aviso")
            .setView(scroll).setNegativeButton("Cancelar",null).create();
        for(int i=0;i<box.getChildCount();i++){
            View child=box.getChildAt(i);
            if(child instanceof LinearLayout&&child.hasOnClickListeners()){
                final int choice=values[i-2];
                child.setOnClickListener(v->{chosen.accept(choice);dialog.dismiss();});
            }
        }
        custom.setOnClickListener(v->{dialog.dismiss();custom(a,current,chosen);});
        dialog.show();WindowLayout.boundDialog(a,dialog);
    }
    public static void custom(Activity a,int current,Consumer<Integer> callback){
        LinearLayout box=content(a);
        box.addView(text(a,"Repetir los avisos cada",15));
        EditText amount=new EditText(a);amount.setSingleLine(true);amount.setInputType(InputType.TYPE_CLASS_NUMBER);
        amount.setText("1");UiDesign.input(amount);
        LinearLayout.LayoutParams amountLp=new LinearLayout.LayoutParams(-1,dp(a,54));
        amountLp.topMargin=dp(a,12);box.addView(amount,amountLp);
        final int[] units={1,60,1440,10080};
        final String[] labels={"Minutos","Horas","Días","Semanas"};
        final int[] unit={2};
        LinearLayout unitRow=new LinearLayout(a);unitRow.setOrientation(1);
        for(int n=0;n<labels.length;n++){
            final int selected=n;
            Button b=new Button(a);b.setAllCaps(false);b.setText(labels[n]);
            UiDesign.button(b,false);
            b.setOnClickListener(v->{unit[0]=selected;
                for(int j=0;j<unitRow.getChildCount();j++){
                    View button=unitRow.getChildAt(j);
                    if(button instanceof Button)((Button)button).setText((j==selected?"✓  ":"")+labels[j]);
                }
            });
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,49));lp.topMargin=dp(a,6);
            unitRow.addView(b,lp);
        }
        ((Button)unitRow.getChildAt(unit[0])).setText("✓  Días");
        box.addView(unitRow);
        TextView tip=text(a,"Se repetirá desde el primer aviso seleccionado hasta la hora límite.",12);
        tip.setTextColor(UiDesign.MUTED);tip.setPadding(0,dp(a,9),0,0);box.addView(tip);
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);scroll.addView(box);
        AlertDialog dlg=new AlertDialog.Builder(a,R.style.DialogTheme)
            .setTitle("Repetición personalizada").setView(scroll)
            .setNegativeButton("Cancelar",null).setPositiveButton("Listo",null).create();
        dlg.setOnShowListener(x->dlg.getButton(-1).setOnClickListener(v->{
            try{
                long n=Long.parseLong(amount.getText().toString().trim());
                long interval=n*units[unit[0]];
                if(n<1||interval>5256000||interval<1)throw new NumberFormatException();
                callback.accept((int)interval);dlg.dismiss();
            }catch(NumberFormatException ex){amount.setError("Introduce un intervalo válido de hasta 10 años.");}
        }));
        dlg.show();WindowLayout.boundDialog(a,dlg);
    }
}
