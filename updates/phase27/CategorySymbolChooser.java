package pe.agendaclara.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.function.Consumer;

/** One category editor with two independent stages: symbol and colour.
 * It never changes the user's saved category until Guardar is selected.
 */
public final class CategorySymbolChooser {
    public static final String[] SYMBOLS={"study","health","projects","work","personal","travel",
        "finance","sport","leisure","food","family","other"};
    public static final String[] LABELS={"Estudios","Salud","Proyectos","Trabajo","Personal","Viajes",
        "Finanzas","Deporte","Ocio","Comida","Familia","Otro"};
    private CategorySymbolChooser(){}
    private static int dp(Activity a,int n){return UiDesign.dp(a,n);}
    private static TextView text(Activity a,String label,int size,int color){
        TextView t=new TextView(a);t.setText(label);t.setTextColor(color);t.setTextSize(size);
        t.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));t.setGravity(Gravity.CENTER_VERTICAL);
        return t;
    }
    private static LinearLayout linear(Activity a,boolean horizontal){
        LinearLayout v=new LinearLayout(a);v.setOrientation(horizontal?0:1);return v;
    }
    private static void gap(Activity a,LinearLayout layout,int n){
        layout.addView(new View(a),new LinearLayout.LayoutParams(1,dp(a,n)));
    }
    public static void show(Activity a,String existing,Consumer<String> onSaved){
        int initial=existing==null?CategoryRegistry.COLORS[0]:CategoryRegistry.color(a,existing);
        final int[] color={initial};
        final String[] icon={existing==null?"study":CategoryRegistry.icon(a,existing)};
        LinearLayout content=linear(a,false);
        content.setPadding(dp(a,18),dp(a,12),dp(a,18),dp(a,28));
        content.addView(text(a,"Nombre de categoría",15,UiDesign.INK));gap(a,content,9);
        EditText name=new EditText(a);name.setSingleLine(true);name.setText(existing==null?"":existing);
        name.setHint("Ej. Estudios, Salud, Proyectos");name.setTextSize(15);
        name.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(28)});
        UiDesign.input(name);content.addView(name);gap(a,content,18);

        content.addView(text(a,"1. Elige un símbolo",16,UiDesign.INK));gap(a,content,9);
        LinearLayout symbols=linear(a,false);content.addView(symbols);
        final Runnable[] refresh={null};
        java.util.ArrayList<LinearLayout> symbolCards=new java.util.ArrayList<>();
        for(int i=0;i<SYMBOLS.length;i++){
            if(i%3==0)symbols.addView(linear(a,true));
            final String symbol=SYMBOLS[i];LinearLayout card=linear(a,false);
            card.setPadding(dp(a,4),dp(a,9),dp(a,4),dp(a,9));card.setGravity(Gravity.CENTER);
            ImageView image=ApprovedPng.view(a,symbol,38);
            card.addView(image,new LinearLayout.LayoutParams(dp(a,42),dp(a,42)));
            TextView label=text(a,LABELS[i],12,UiDesign.INK);label.setGravity(Gravity.CENTER);
            card.addView(label);
            LinearLayout row=(LinearLayout)symbols.getChildAt(symbols.getChildCount()-1);
            LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,dp(a,90),1);
            params.setMargins(dp(a,3),dp(a,3),dp(a,3),dp(a,3));row.addView(card,params);
            card.setContentDescription("Símbolo "+LABELS[i]);card.setOnClickListener(v->{icon[0]=symbol;refresh[0].run();});
            symbolCards.add(card);
        }

        gap(a,content,17);content.addView(text(a,"2. Elige un color",16,UiDesign.INK));
        gap(a,content,9);
        LinearLayout palette=linear(a,false);content.addView(palette);
        java.util.ArrayList<View> colorDots=new java.util.ArrayList<>();
        for(int i=0;i<CategoryRegistry.COLORS.length;i++){
            if(i%4==0)palette.addView(linear(a,true));
            int shade=CategoryRegistry.COLORS[i];Button dot=new Button(a);
            dot.setAllCaps(false);dot.setText("●");dot.setTextSize(25);dot.setTextColor(shade);
            dot.setContentDescription("Color "+CategoryRegistry.COLOR_NAMES[i]);
            LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,dp(a,58),1);
            params.setMargins(dp(a,3),dp(a,4),dp(a,3),dp(a,4));
            LinearLayout row=(LinearLayout)palette.getChildAt(palette.getChildCount()-1);
            row.addView(dot,params);dot.setOnClickListener(v->{color[0]=shade;refresh[0].run();});
            colorDots.add(dot);
        }

        gap(a,content,15);content.addView(text(a,"Vista previa",14,UiDesign.INK));gap(a,content,8);
        LinearLayout preview=linear(a,true);preview.setPadding(dp(a,14),dp(a,13),dp(a,14),dp(a,13));
        preview.setGravity(Gravity.CENTER_VERTICAL);
        ImageView previewIcon=ApprovedPng.view(a,icon[0],43);
        preview.addView(previewIcon,new LinearLayout.LayoutParams(dp(a,50),dp(a,50)));
        LinearLayout previewText=linear(a,false);
        TextView previewName=text(a,"Categoría",16,UiDesign.INK);
        previewText.addView(previewName);
        previewText.addView(text(a,"Así se verán sus tareas.",12,UiDesign.MUTED));
        LinearLayout.LayoutParams pp=new LinearLayout.LayoutParams(0,-2,1);pp.leftMargin=dp(a,10);
        preview.addView(previewText,pp);content.addView(preview);
        refresh[0]=()->{
            for(int i=0;i<symbolCards.size();i++){
                LinearLayout card=symbolCards.get(i);
                boolean active=SYMBOLS[i].equals(icon[0]);
                card.setBackground(UiDesign.tintedBackground(a,active?color[0]:UiDesign.BORDER,14,active?25:10));
                card.setElevation(active?dp(a,2):0);
                card.setSelected(active);
            }
            for(int i=0;i<colorDots.size();i++){
                Button dot=(Button)colorDots.get(i);
                boolean selected=CategoryRegistry.COLORS[i]==color[0];
                dot.setBackground(UiDesign.tintedBackground(a,selected?color[0]:UiDesign.BORDER,24,selected?25:6));
                dot.setText(selected?"✓":"●");dot.setTextColor(selected?UiDesign.accentInk(color[0]):CategoryRegistry.COLORS[i]);
            }
            preview.setBackground(UiDesign.tintedBackground(a,color[0],18,18));
            previewIcon.setImageDrawable(ApprovedPng.drawable(a,icon[0]));
            previewName.setText(name.getText().toString().trim().isEmpty()?"Nueva categoría":name.getText().toString().trim());
            previewName.setTextColor(UiDesign.accentInk(color[0]));
        };
        name.addTextChangedListener(new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            public void onTextChanged(CharSequence s,int start,int before,int count){refresh[0].run();}
            public void afterTextChanged(android.text.Editable e){}
        });
        refresh[0].run();
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);
        scroll.addView(content);
        AlertDialog dialog=new AlertDialog.Builder(a,R.style.DialogTheme)
            .setTitle(existing==null?"Crear categoría":"Editar categoría")
            .setView(scroll).setNegativeButton("Cancelar",null).setPositiveButton("Guardar",null).create();
        dialog.setOnShowListener(d->{
            WindowLayout.boundDialog(a,dialog);
            dialog.getButton(-1).setOnClickListener(v->{
                String desired=name.getText().toString().trim();
                if(desired.isEmpty()){name.setError("Escribe un nombre.");return;}
                if(!CategoryRegistry.save(a,existing,desired,color[0],icon[0])){
                    name.setError("Ya existe o el nombre no es válido.");return;
                }
                dialog.dismiss();if(onSaved!=null)onSaved.accept(desired);
            });
            scroll.requestFocus();scroll.post(()->scroll.scrollTo(0,0));
        });
        dialog.show();
    }
}
