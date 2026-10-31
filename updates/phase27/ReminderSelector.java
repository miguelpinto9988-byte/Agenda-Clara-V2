package pe.agendaclara.app;
import android.app.*;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.text.InputType;
import android.view.*;
import android.widget.*;
import java.util.*;
import java.util.function.Consumer;

/** Accessible selectable notification offsets; never changes task recurrence. */
public final class ReminderSelector {
    private ReminderSelector(){}
    static int dp(Activity a,int v){return UiDesign.dp(a,v);}
    static TextView title(Activity a,String s,int sp){
        TextView t=new TextView(a);t.setText(s);t.setTextColor(UiDesign.INK);
        t.setTextSize(sp);t.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));return t;
    }
    static void space(Activity a,LinearLayout l,int gap){
        l.addView(new View(a),new LinearLayout.LayoutParams(1,dp(a,gap)));
    }
    public static void show(Activity a,SortedSet<Integer> original,Consumer<SortedSet<Integer>> done){
        SortedSet<Integer> pending=new TreeSet<>(Collections.reverseOrder());pending.addAll(original);
        int[] values={0,15,30,60,180,720,1440,2880,10080,20160,43200};
        LinearLayout pane=new LinearLayout(a);pane.setOrientation(1);pane.setPadding(dp(a,16),dp(a,12),dp(a,16),dp(a,16));
        pane.addView(title(a,"Selecciona cuándo quieres recibir un aviso.",13));
        space(a,pane,12);
        for(int offset:values){
            LinearLayout card=new LinearLayout(a);card.setGravity(Gravity.CENTER_VERTICAL);
            card.setPadding(dp(a,12),dp(a,7),dp(a,12),dp(a,7));
            card.setBackground(UiDesign.shape(a,0xfff5f8ff,14,UiDesign.BORDER));
            ImageView icon=PngIcons.view(a,offset==0?"bell":offset<1440?"clock":"date",24);
            card.addView(icon,new LinearLayout.LayoutParams(dp(a,27),dp(a,27)));
            TextView label=title(a,"   "+TaskLogic.offsetName(offset),14);
            card.addView(label,new LinearLayout.LayoutParams(0,-2,1));
            CheckBox checked=new CheckBox(a);checked.setButtonTintList(ColorStateList.valueOf(UiDesign.BLUE));
            checked.setChecked(pending.contains(offset));checked.setContentDescription(TaskLogic.offsetName(offset));
            card.addView(checked);
            View.OnClickListener flip=v->checked.setChecked(!checked.isChecked());
            card.setOnClickListener(flip);
            checked.setOnCheckedChangeListener((button,isChecked)->{
                if(isChecked)pending.add(offset);else pending.remove(offset);
            });
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,51));
            lp.bottomMargin=dp(a,7);pane.addView(card,lp);
        }
        Button custom=new Button(a);custom.setText("Personalizar aviso  ›");custom.setAllCaps(false);
        UiDesign.button(custom,false);PngIcons.button(custom,"settings",22);
        LinearLayout.LayoutParams customLp=new LinearLayout.LayoutParams(-1,dp(a,52));
        customLp.topMargin=dp(a,8);pane.addView(custom,customLp);
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);scroll.addView(pane);
        AlertDialog d=new AlertDialog.Builder(a,R.style.DialogTheme).setTitle("¿Cuándo te aviso?")
            .setView(scroll).setNegativeButton("Cancelar",null)
            .setPositiveButton("Listo",(dialog,which)->done.accept(pending)).create();
        custom.setOnClickListener(v->custom(a,pending,newSet->{
            done.accept(newSet);d.dismiss();
        }));
        d.show();WindowLayout.boundDialog(a,d);
    }
    public static void custom(Activity a,SortedSet<Integer> original,Consumer<SortedSet<Integer>> done){
        LinearLayout pane=new LinearLayout(a);pane.setOrientation(1);pane.setPadding(dp(a,18),dp(a,14),dp(a,18),dp(a,18));
        pane.addView(title(a,"Avisar con esta anticipación",14));space(a,pane,10);
        EditText number=new EditText(a);number.setInputType(InputType.TYPE_CLASS_NUMBER);
        number.setSingleLine(true);number.setText("3");UiDesign.input(number);
        pane.addView(number,new LinearLayout.LayoutParams(-1,dp(a,55)));space(a,pane,10);
        final int[] unit={1440};
        LinearLayout buttons=new LinearLayout(a);buttons.setOrientation(1);
        int[] choices={1,60,1440,10080};String[] labels={"Minutos","Horas","Días","Semanas"};
        for(int j=0;j<choices.length;j++){
            final int n=j;
            Button b=new Button(a);b.setAllCaps(false);
            b.setText((unit[0]==choices[j]?"✓  ":"")+labels[j]);UiDesign.button(b,false);
            b.setOnClickListener(v->{
                unit[0]=choices[n];
                for(int k=0;k<buttons.getChildCount();k++)
                    ((Button)buttons.getChildAt(k)).setText((k==n?"✓  ":"")+labels[k]);
            });
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,50));
            lp.bottomMargin=dp(a,7);buttons.addView(b,lp);
        }
        pane.addView(buttons);
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);scroll.addView(pane);
        AlertDialog dialog=new AlertDialog.Builder(a,R.style.DialogTheme).setTitle("Aviso personalizado")
            .setView(scroll).setNegativeButton("Cancelar",null).setPositiveButton("Añadir",null).create();
        dialog.setOnShowListener(x->dialog.getButton(-1).setOnClickListener(v->{
            try{
                long value=Long.parseLong(number.getText().toString().trim())*unit[0];
                if(value<0||value>5256000)throw new NumberFormatException();
                SortedSet<Integer> chosen=new TreeSet<>(Collections.reverseOrder());chosen.addAll(original);
                chosen.add((int)value);done.accept(chosen);dialog.dismiss();
            }catch(NumberFormatException ex){number.setError("Máximo 10 años de anticipación.");}
        }));
        dialog.show();WindowLayout.boundDialog(a,dialog);
    }
}
