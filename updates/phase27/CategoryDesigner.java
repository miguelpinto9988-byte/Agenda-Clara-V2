package pe.agendaclara.app;

import android.app.AlertDialog;
import android.graphics.Color;
import android.graphics.Typeface;
import android.text.InputType;
import android.text.InputFilter;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import java.util.ArrayList;
import java.util.function.Consumer;

/** Icon and colour are separately editable; both persist with a category. */
public final class CategoryDesigner {
    private CategoryDesigner(){}
    static int dp(MainActivity a,int size){return UiDesign.dp(a,size);}
    static LinearLayout col(MainActivity a){LinearLayout x=new LinearLayout(a);x.setOrientation(1);return x;}
    static LinearLayout row(MainActivity a){LinearLayout x=new LinearLayout(a);x.setOrientation(0);x.setGravity(Gravity.CENTER_VERTICAL);return x;}
    static TextView text(MainActivity a,String s,int size){
        TextView t=new TextView(a);t.setText(s);t.setTextSize(size);t.setTextColor(UiDesign.INK);
        t.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));return t;
    }
    static void gap(MainActivity a,LinearLayout parent,int height){
        parent.addView(new View(a),new LinearLayout.LayoutParams(1,dp(a,height)));
    }
    static void tileState(MainActivity a,LinearLayout box,int color,boolean active){
        box.setBackground(UiDesign.tintedBackground(a,color,15,active?25:9));
        box.setElevation(active?dp(a,3):0);
    }
    public static void show(MainActivity a,String existing,Consumer<String> onSaved){
        final int[] selectedColor={CategoryRegistry.color(a,existing)};
        final String[] selectedIcon={CategoryRegistry.icon(a,existing)};
        LinearLayout pane=col(a);pane.setPadding(dp(a,16),dp(a,14),dp(a,16),dp(a,22));
        TextView intro=text(a,"Nombre de categoría",15);pane.addView(intro);gap(a,pane,8);
        EditText name=new EditText(a);name.setSingleLine(true);
        name.setText(existing==null?"":existing);name.setHint("Ej. Estudios, Salud, Proyectos");
        name.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        name.setFilters(new InputFilter[]{new InputFilter.LengthFilter(28)});UiDesign.input(name);
        pane.addView(name,new LinearLayout.LayoutParams(-1,dp(a,56)));gap(a,pane,18);
        pane.addView(text(a,"1 · Elige un símbolo",16));gap(a,pane,11);
        LinearLayout symbols=col(a);
        ArrayList<LinearLayout> symbolCards=new ArrayList<>();
        Runnable[] repaintSymbol={null};
        for(int k=0;k<PngIcons.CATEGORY_SYMBOLS.length;k++){
            final int index=k;
            if(k%4==0){LinearLayout r=row(a);symbols.addView(r,new LinearLayout.LayoutParams(-1,-2));}
            LinearLayout r=(LinearLayout)symbols.getChildAt(symbols.getChildCount()-1);
            LinearLayout tile=col(a);tile.setGravity(Gravity.CENTER);tile.setPadding(dp(a,3),dp(a,6),dp(a,3),dp(a,6));
            ImageView icon=PngIcons.view(a,PngIcons.CATEGORY_SYMBOLS[k],31);
            tile.addView(icon,new LinearLayout.LayoutParams(dp(a,35),dp(a,35)));
            TextView label=text(a,PngIcons.CATEGORY_LABELS[k],10);label.setGravity(Gravity.CENTER);
            label.setMaxLines(1);tile.addView(label);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(a,76),1);
            lp.setMargins(dp(a,3),dp(a,3),dp(a,3),dp(a,3));r.addView(tile,lp);
            symbolCards.add(tile);
            tile.setContentDescription("Símbolo "+PngIcons.CATEGORY_LABELS[k]);
            tile.setOnClickListener(v->{selectedIcon[0]=PngIcons.CATEGORY_SYMBOLS[index];repaintSymbol[0].run();});
        }
        repaintSymbol[0]=()->{
            for(int k=0;k<symbolCards.size();k++)
                tileState(a,symbolCards.get(k),selectedColor[0],
                    selectedIcon[0].equals(PngIcons.CATEGORY_SYMBOLS[k]));
        };
        pane.addView(symbols);gap(a,pane,18);
        pane.addView(text(a,"2 · Elige un color",16));gap(a,pane,10);
        LinearLayout colors=col(a);ArrayList<LinearLayout> swatches=new ArrayList<>();
        Runnable[] repaintColors={null};
        for(int k=0;k<CategoryRegistry.COLORS.length;k++){
            final int index=k,accent=CategoryRegistry.COLORS[k];
            if(k%4==0){LinearLayout r=row(a);colors.addView(r);}
            LinearLayout r=(LinearLayout)colors.getChildAt(colors.getChildCount()-1);
            LinearLayout tile=col(a);tile.setGravity(Gravity.CENTER);
            View swatch=new View(a);
            swatch.setBackground(UiDesign.shape(a,accent,22,0));
            tile.addView(swatch,new LinearLayout.LayoutParams(dp(a,37),dp(a,37)));
            TextView label=text(a,CategoryRegistry.COLOR_NAMES[k],10);label.setGravity(Gravity.CENTER);
            tile.addView(label);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(a,78),1);
            lp.setMargins(dp(a,3),dp(a,3),dp(a,3),dp(a,3));
            r.addView(tile,lp);swatches.add(tile);
            tile.setOnClickListener(v->{selectedColor[0]=accent;repaintColors[0].run();repaintSymbol[0].run();});
        }
        repaintColors[0]=()->{
            for(int j=0;j<swatches.size();j++){
                int tone=CategoryRegistry.COLORS[j];
                tileState(a,swatches.get(j),tone,selectedColor[0]==tone);
            }
        };
        pane.addView(colors);gap(a,pane,20);
        pane.addView(text(a,"Vista previa",15));gap(a,pane,10);
        LinearLayout preview=row(a);preview.setPadding(dp(a,13),dp(a,12),dp(a,13),dp(a,12));
        ImageView previewIcon=PngIcons.view(a,selectedIcon[0],40);
        preview.addView(previewIcon,new LinearLayout.LayoutParams(dp(a,43),dp(a,43)));
        TextView previewText=text(a,"  "+(existing==null?"Mi categoría":existing),16);
        preview.addView(previewText);pane.addView(preview);
        Runnable[] updatePreview={null};
        updatePreview[0]=()->{
            preview.setBackground(UiDesign.tintedBackground(a,selectedColor[0],16,18));
            previewIcon.setImageResource(PngIcons.id(a,selectedIcon[0]));
            previewText.setText("  "+(name.getText().toString().trim().isEmpty()?"Mi categoría":name.getText().toString().trim()));
            previewText.setTextColor(UiDesign.accentInk(selectedColor[0]));
        };
        name.addTextChangedListener(new android.text.TextWatcher(){
            public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            public void onTextChanged(CharSequence s,int start,int before,int count){updatePreview[0].run();}
            public void afterTextChanged(android.text.Editable e){}
        });
        // Repaint the preview after either independent choice.
        for(LinearLayout t:symbolCards)t.setOnTouchListener((v,event)->{
            if(event.getAction()==android.view.MotionEvent.ACTION_UP)v.post(updatePreview[0]);
            return false;
        });
        for(LinearLayout t:swatches)t.setOnTouchListener((v,event)->{
            if(event.getAction()==android.view.MotionEvent.ACTION_UP)v.post(updatePreview[0]);
            return false;
        });
        repaintSymbol[0].run();repaintColors[0].run();updatePreview[0].run();
        WindowLayout.DialogScroll scroll=new WindowLayout.DialogScroll(a);scroll.addView(pane);
        AlertDialog d=a.dialogBuilder().setTitle(existing==null?"Crear categoría":"Editar categoría")
            .setView(scroll).setNegativeButton("Cancelar",null).setPositiveButton("Guardar",null).create();
        d.setOnShowListener(x->d.getButton(-1).setOnClickListener(v->{
            String desired=name.getText().toString().trim();
            if(desired.isEmpty()){name.setError("Escribe el nombre de la categoría.");return;}
            if(!CategoryRegistry.save(a,existing,desired,selectedColor[0],selectedIcon[0])){
                name.setError("Nombre duplicado o no válido.");return;
            }
            if(existing!=null&&a.selectedCategory.equalsIgnoreCase(existing))a.selectedCategory=desired;
            d.dismiss();a.render();if(onSaved!=null)onSaved.accept(desired);
        }));
        d.show();d.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN|
                android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
    }
}
