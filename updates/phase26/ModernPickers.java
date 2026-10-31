package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.GridLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.NumberPicker;
import android.widget.ScrollView;
import android.widget.TextView;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.util.Locale;
import java.util.function.Consumer;

/** Branded, accessible, bounded native pickers replacing platform popups/spinners. */
public final class ModernPickers {
    private static final int INK=UiDesign.INK,BLUE=UiDesign.BLUE,MUTED=UiDesign.MUTED;
    private static final Locale ES=new Locale("es","PE");
    private ModernPickers(){}
    private static int dp(Activity a,int n){return UiDesign.dp(a,n);}
    private static LinearLayout column(Activity a){LinearLayout l=new LinearLayout(a);l.setOrientation(1);return l;}
    private static LinearLayout row(Activity a){LinearLayout l=new LinearLayout(a);l.setOrientation(0);l.setGravity(Gravity.CENTER_VERTICAL);return l;}
    private static TextView label(Activity a,String value,int size,int color){
        TextView t=new TextView(a);t.setText(value);t.setTextSize(size);t.setTextColor(color);
        t.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));t.setGravity(Gravity.CENTER_VERTICAL);
        t.setIncludeFontPadding(true);return t;
    }
    private static void gap(Activity a,LinearLayout parent,int height){
        parent.addView(new View(a),new LinearLayout.LayoutParams(1,dp(a,height)));
    }
    private static LinearLayout pane(Activity a){
        LinearLayout p=column(a);p.setPadding(dp(a,18),dp(a,16),dp(a,18),dp(a,18));
        return p;
    }
    private static ScrollView scroll(Activity a,LinearLayout content){
        WindowLayout.DialogScroll sc=new WindowLayout.DialogScroll(a);
        sc.setFillViewport(false);sc.addView(content);return sc;
    }
    private static AlertDialog dialog(Activity a,String title,LinearLayout content,
                                      String positive,Runnable accepted){
        AlertDialog result=new AlertDialog.Builder(a,R.style.DialogTheme)
            .setTitle(title).setView(scroll(a,content))
            .setNegativeButton("Cancelar",null)
            .setPositiveButton(positive,(dialog,which)->accepted.run()).create();
        result.setOnShowListener(d->{
            WindowLayout.boundDialog(a,result);
            View root=result.getWindow().getDecorView();
            root.post(()->UiDesign.polishTree(root));
        });
        result.show();
        return result;
    }
    private static Button chip(Activity a,String text,boolean selected){
        Button b=new Button(a);
        b.setAllCaps(false);b.setText(text);b.setTextSize(13);
        b.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));
        b.setTextColor(selected?BLUE:INK);
        b.setBackground(ModernGlyph.rounded(a,selected?0xffe9efff:0xfff8faff,
                    selected?BLUE:UiDesign.BORDER,14));
        b.setMinimumHeight(dp(a,48));return b;
    }
    /** Replaces the operating-system date picker with the approved month grid. */
    public static void showDate(Activity a,LocalDate initial,Consumer<LocalDate> callback){
        final LocalDate[] chosen={initial==null?LocalDate.now():initial};
        final YearMonth[] month={YearMonth.from(chosen[0])};
        LinearLayout content=pane(a);
        content.addView(label(a,"Elige la fecha límite de entrega",13,MUTED));gap(a,content,16);
        LinearLayout quick=row(a);
        Button today=chip(a,"Hoy",false),tomorrow=chip(a,"Mañana",false),choose=chip(a,"Calendario",true);
        for(Button b:new Button[]{today,tomorrow,choose}){
            LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(a,48),1);
            p.setMargins(dp(a,3),0,dp(a,3),0);quick.addView(b,p);
        }
        content.addView(quick);gap(a,content,16);
        LinearLayout monthBar=row(a);
        Button prev=chip(a,"‹",false),next=chip(a,"›",false);
        prev.setTextSize(24);next.setTextSize(24);
        TextView monthName=label(a,"",17,INK);monthName.setGravity(Gravity.CENTER);
        monthBar.addView(prev,new LinearLayout.LayoutParams(dp(a,44),dp(a,48)));
        monthBar.addView(monthName,new LinearLayout.LayoutParams(0,dp(a,48),1));
        monthBar.addView(next,new LinearLayout.LayoutParams(dp(a,44),dp(a,48)));
        content.addView(monthBar);gap(a,content,8);
        GridLayout grid=new GridLayout(a);grid.setColumnCount(7);
        content.addView(grid,new LinearLayout.LayoutParams(-1,-2));
        gap(a,content,14);
        LinearLayout selectedRow=row(a);selectedRow.setPadding(dp(a,12),dp(a,12),dp(a,12),dp(a,12));
        selectedRow.setBackground(ModernGlyph.rounded(a,0xffeef3ff,UiDesign.BORDER,14));
        selectedRow.addView(ModernGlyph.view(a,"date",BLUE,24),new LinearLayout.LayoutParams(dp(a,28),dp(a,28)));
        TextView chosenText=label(a,"",13,INK);
        LinearLayout.LayoutParams chosenParams=new LinearLayout.LayoutParams(0,-2,1);
        chosenParams.leftMargin=dp(a,10);selectedRow.addView(chosenText,chosenParams);
        content.addView(selectedRow);
        final Runnable[] render={null};
        render[0]=()->{
            monthName.setText(month[0].format(DateTimeFormatter.ofPattern("MMMM yyyy",ES)));
            chosenText.setText(chosen[0].format(DateTimeFormatter.ofPattern("EEEE, d 'de' MMMM 'de' yyyy",ES)));
            grid.removeAllViews();String[] weekdays={"L","M","M","J","V","S","D"};
            for(int i=0;i<7;i++){
                TextView day=label(a,weekdays[i],11,MUTED);day.setGravity(Gravity.CENTER);
                GridLayout.LayoutParams lp=new GridLayout.LayoutParams(GridLayout.spec(0),GridLayout.spec(i,1f));
                lp.width=0;lp.height=dp(a,35);grid.addView(day,lp);
            }
            int offset=month[0].atDay(1).getDayOfWeek().getValue()-1;
            int days=month[0].lengthOfMonth();
            int slots=(int)(Math.ceil((offset+days)/7.0)*7);
            for(int slot=0;slot<slots;slot++){
                int day=slot-offset+1;int col=slot%7,row=1+slot/7;
                TextView cell=label(a,day>=1&&day<=days?String.valueOf(day):"",13,INK);
                cell.setGravity(Gravity.CENTER);
                if(day>=1&&day<=days){
                    LocalDate selectedDate=month[0].atDay(day);
                    boolean selected=selectedDate.equals(chosen[0]);
                    if(selected){
                        cell.setTextColor(0xffffffff);
                        cell.setBackground(ModernGlyph.rounded(a,BLUE,0,22));
                    }else if(selectedDate.equals(LocalDate.now())){
                        cell.setBackground(ModernGlyph.rounded(a,0xffe8efff,UiDesign.BORDER,22));
                    }
                    cell.setContentDescription(selectedDate.format(DateTimeFormatter.ofPattern("EEEE d 'de' MMMM",ES)));
                    cell.setOnClickListener(v->{chosen[0]=selectedDate;render[0].run();});
                }
                GridLayout.LayoutParams lp=new GridLayout.LayoutParams(GridLayout.spec(row),GridLayout.spec(col,1f));
                lp.width=0;lp.height=dp(a,43);lp.setMargins(dp(a,1),dp(a,1),dp(a,1),dp(a,1));
                grid.addView(cell,lp);
            }
        };
        prev.setOnClickListener(v->{month[0]=month[0].minusMonths(1);render[0].run();});
        next.setOnClickListener(v->{month[0]=month[0].plusMonths(1);render[0].run();});
        today.setOnClickListener(v->{chosen[0]=LocalDate.now();month[0]=YearMonth.from(chosen[0]);render[0].run();});
        tomorrow.setOnClickListener(v->{chosen[0]=LocalDate.now().plusDays(1);month[0]=YearMonth.from(chosen[0]);render[0].run();});
        choose.setOnClickListener(v->grid.requestFocus());
        render[0].run();dialog(a,"Seleccionar fecha",content,"Aceptar",()->callback.accept(chosen[0]));
    }
    /** 12h clock dial and editable hour/minute numeric controls. */
    public static void showTime(Activity a,LocalTime initial,Consumer<LocalTime> callback){
        LocalTime start=initial==null?LocalTime.of(23,59):initial;
        final int[] hour={start.getHour()%12==0?12:start.getHour()%12};
        final int[] minute={start.getMinute()};
        final boolean[] pm={start.getHour()>=12};
        LinearLayout content=pane(a);content.addView(label(a,"Hora límite de entrega",13,MUTED));gap(a,content,12);
        LinearLayout mode=row(a);
        Button clock=chip(a,"◷  Reloj",true),keyboard=chip(a,"⌨  Teclado",false);
        for(Button b:new Button[]{clock,keyboard}){
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(a,44),1);lp.rightMargin=dp(a,6);mode.addView(b,lp);
        }
        content.addView(mode);gap(a,content,12);
        LinearLayout timeRow=row(a);timeRow.setGravity(Gravity.CENTER);
        TextView big=label(a,"",36,BLUE);big.setGravity(Gravity.CENTER);
        timeRow.addView(big,new LinearLayout.LayoutParams(0,dp(a,80),1));
        LinearLayout period=column(a);
        Button am=chip(a,"A. M.",!pm[0]),pmButton=chip(a,"P. M.",pm[0]);
        period.addView(am,new LinearLayout.LayoutParams(dp(a,68),dp(a,39)));
        gap(a,period,4);period.addView(pmButton,new LinearLayout.LayoutParams(dp(a,68),dp(a,39)));
        timeRow.addView(period);
        timeRow.setPadding(dp(a,12),dp(a,10),dp(a,12),dp(a,10));
        timeRow.setBackground(ModernGlyph.rounded(a,0xffedf3ff,UiDesign.BORDER,15));
        content.addView(timeRow);gap(a,content,16);
        FrameLayout dial=new FrameLayout(a);
        dial.setBackground(ModernGlyph.rounded(a,0xfff0f3f8,0,130));
        LinearLayout dialWrap=row(a);dialWrap.setGravity(Gravity.CENTER);
        dialWrap.addView(dial,new LinearLayout.LayoutParams(dp(a,244),dp(a,244)));
        content.addView(dialWrap);
        LinearLayout numeric=row(a);numeric.setGravity(Gravity.CENTER);
        NumberPicker hours=new NumberPicker(a);hours.setMinValue(1);hours.setMaxValue(12);
        hours.setWrapSelectorWheel(true);hours.setValue(hour[0]);
        NumberPicker minutes=new NumberPicker(a);minutes.setMinValue(0);minutes.setMaxValue(59);
        minutes.setWrapSelectorWheel(true);minutes.setValue(minute[0]);
        minutes.setFormatter(v->String.format(ES,"%02d",v));
        numeric.addView(label(a,"Hora",14,INK));
        numeric.addView(hours,new LinearLayout.LayoutParams(dp(a,82),dp(a,120)));
        numeric.addView(label(a,"Min",14,INK));
        numeric.addView(minutes,new LinearLayout.LayoutParams(dp(a,82),dp(a,120)));
        content.addView(numeric);gap(a,content,12);
        final Runnable[] redraw={null};
        redraw[0]=()->{
            big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));
            am.setBackground(ModernGlyph.rounded(a,!pm[0]?BLUE:0xffffffff,UiDesign.BORDER,10));
            pmButton.setBackground(ModernGlyph.rounded(a,pm[0]?BLUE:0xffffffff,UiDesign.BORDER,10));
            am.setTextColor(!pm[0]?0xffffffff:BLUE);
            pmButton.setTextColor(pm[0]?0xffffffff:BLUE);
            dial.removeAllViews();
            for(int j=1;j<=12;j++){
                final int value=j;double theta=2*Math.PI*j/12.0-Math.PI/2;
                TextView cell=label(a,String.valueOf(j),15,j==hour[0]?0xffffffff:INK);
                cell.setGravity(Gravity.CENTER);
                if(j==hour[0])cell.setBackground(ModernGlyph.rounded(a,BLUE,0,24));
                FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(dp(a,38),dp(a,38));
                lp.leftMargin=dp(a,122-19+(int)Math.round(91*Math.cos(theta)));
                lp.topMargin=dp(a,122-19+(int)Math.round(91*Math.sin(theta)));
                dial.addView(cell,lp);
                cell.setOnClickListener(v->{hour[0]=value;hours.setValue(value);redraw[0].run();});
            }
        };
        am.setOnClickListener(v->{pm[0]=false;redraw[0].run();});
        pmButton.setOnClickListener(v->{pm[0]=true;redraw[0].run();});
        hours.setOnValueChangedListener((picker,oldValue,newValue)->{hour[0]=newValue;redraw[0].run();});
        minutes.setOnValueChangedListener((picker,oldValue,newValue)->{minute[0]=newValue;redraw[0].run();});
        clock.setOnClickListener(v->{dialWrap.setVisibility(View.VISIBLE);numeric.setVisibility(View.GONE);});
        keyboard.setOnClickListener(v->{dialWrap.setVisibility(View.GONE);numeric.setVisibility(View.VISIBLE);});
        numeric.setVisibility(View.GONE);
        redraw[0].run();
        dialog(a,"Seleccionar hora",content,"Aceptar",()->{
            int h=hour[0]%12+(pm[0]?12:0);
            callback.accept(LocalTime.of(h,minute[0]));
        });
    }
    /** Pick persisted user-created categories with their full card color. */
    public static void showCategory(Activity a,String current,Consumer<String> callback){
        LinearLayout content=pane(a);
        content.addView(label(a,"Selecciona una categoría",13,MUTED));gap(a,content,12);
        for(CategoryRegistry.Entry entry:CategoryRegistry.all(a)){
            final String chosen=entry.name;int color=entry.color;
            LinearLayout card=row(a);card.setPadding(dp(a,12),dp(a,9),dp(a,12),dp(a,9));
            card.setMinimumHeight(dp(a,58));
            card.setBackground(UiDesign.tintedBackground(a,color,15,17));
            card.addView(ModernGlyph.view(a,"folder",color,28),new LinearLayout.LayoutParams(dp(a,32),dp(a,32)));
            TextView text=label(a,"   "+chosen,15,UiDesign.accentInk(color));
            card.addView(text,new LinearLayout.LayoutParams(0,-2,1));
            boolean selected=chosen.equalsIgnoreCase(current);
            if(selected){
                TextView check=label(a,"✓",22,UiDesign.accentInk(color));
                card.addView(check);card.setContentDescription(chosen+", seleccionada");
            }else card.setContentDescription(chosen);
            card.setOnClickListener(v->{callback.accept(chosen);});
            content.addView(card);gap(a,content,9);
        }
        final AlertDialog[] ref={null};
        // Own the category selection as a dismissible modal, not a spinner popup.
        ref[0]=dialog(a,"Elegir categoría",content,"Cerrar",()->{});
        for(int i=0;i<content.getChildCount();i++){
            View item=content.getChildAt(i);
            if(item instanceof LinearLayout && item.hasOnClickListeners()){
                final View.OnClickListener old=v->{};
                final String selection=item.getContentDescription()==null?"":item.getContentDescription().toString().replace(", seleccionada","");
                item.setOnClickListener(v->{callback.accept(selection);ref[0].dismiss();});
            }
        }
    }
}
