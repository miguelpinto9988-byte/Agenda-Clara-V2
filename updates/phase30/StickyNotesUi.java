package pe.agendaclara.app;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.graphics.Color;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.HorizontalScrollView;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;

/** Real sticky notes: PNG paper/pin/fold, editable bold text and local date only. */
public final class StickyNotesUi {
    public static final int[] COLORS={0xffffec7f,0xffffc9db,0xff95e0f5,0xffafe3c9,0xffd1bafd,0xffffd3b7};
    public static final String[] COLOR_LABELS={"Amarillo","Rosa","Azul","Verde","Morado","Durazno"};
    private static final Locale ES=new Locale("es","PE");
    private StickyNotesUi(){}
    private static int dp(MainActivity a,int value){return a.dp(value);}
    private static TextView text(MainActivity a,String content,int sp,int ink){
        TextView v=a.text(content,sp,ink,true);v.setEllipsize(android.text.TextUtils.TruncateAt.END);
        return v;
    }
    private static int asset(int color){
        switch(Math.max(0,Math.min(5,color))){
            case 1:return R.drawable.sticky_pink;
            case 2:return R.drawable.sticky_blue;
            case 3:return R.drawable.sticky_green;
            case 4:return R.drawable.sticky_purple;
            case 5:return R.drawable.sticky_peach;
            default:return R.drawable.sticky_yellow;
        }
    }
    private static void ensureDefaultCategory(MainActivity a){
        for(CategoryRegistry.Entry e:CategoryRegistry.all(a))if(e.name.equalsIgnoreCase("Notas"))return;
        CategoryRegistry.save(a,"","Notas",0xffd99d2b,"sticky_note");
    }
    /** Paper is an editable overlay on a color-specific PNG; the text is never rasterized. */
    public static FrameLayout card(MainActivity a,StickyNotesStore.Note note,boolean large,boolean interactive){
        FrameLayout frame=new FrameLayout(a);
        frame.setMinimumHeight(dp(a,large?235:185));
        ImageView artwork=new ImageView(a);
        artwork.setImageResource(asset(note.color));artwork.setScaleType(ImageView.ScaleType.FIT_XY);
        frame.addView(artwork,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout content=a.column();content.setOrientation(1);
        content.setPadding(dp(a,29),dp(a,large?51:40),dp(a,37),dp(a,29));
        FrameLayout.LayoutParams contentLayout=new FrameLayout.LayoutParams(-1,-1);
        frame.addView(content,contentLayout);
        TextView title=text(a,note.title.isEmpty()?"Título de la nota":note.title,large?19:16,0xff15254b);
        title.setMaxLines(large?2:2);content.addView(title);
        a.gap(content,large?10:6);
        TextView body=text(a,note.body.isEmpty()?"Escribe aquí tu nota...":note.body,large?14:13,0xff21385b);
        body.setMaxLines(large?4:2);content.addView(body,new LinearLayout.LayoutParams(-1,0,1));
        TextView date=text(a,"▦  "+note.day.format(DateTimeFormatter.ofPattern("dd MMM yyyy",ES)),12,0xff344c68);
        date.setSingleLine(true);content.addView(date);
        frame.setContentDescription("Nota adhesiva: "+note.title+". "+note.day.toString());
        if(interactive){frame.setFocusable(true);frame.setOnClickListener(v->showEditor(a,note));}
        return frame;
    }
    private static void attach(LinearLayout parent,FrameLayout card,MainActivity a){
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(a,185));
        lp.bottomMargin=dp(a,12);parent.addView(card,lp);
    }
    public static void agenda(MainActivity a,LinearLayout container,String category,String query){
        List<StickyNotesStore.Note> all=StickyNotesStore.get(a).inCategory(category);
        if(all.isEmpty()){
            if("Notas".equalsIgnoreCase(category)){
                a.subtitle(container,"Mis notas adhesivas");
                LinearLayout c=a.card(container);
                c.addView(text(a,"Guarda notas con una fecha, sin convertirlas en tareas.",14,UiDesign.MUTED));
                c.addView(a.button("＋  Nueva nota",()->showEditor(a,null)));
            }
            return;
        }
        String target=query==null?"":query.trim().toLowerCase(ES);
        int shown=0;
        for(StickyNotesStore.Note n:all)
            if(target.isEmpty()||(n.title+" "+n.body).toLowerCase(ES).contains(target))shown++;
        if(shown==0)return;
        a.subtitle(container,"Notas adhesivas · "+shown);
        LinearLayout cards=a.column();container.addView(cards);
        for(StickyNotesStore.Note n:all){
            if(!target.isEmpty()&&!(n.title+" "+n.body).toLowerCase(ES).contains(target))continue;
            attach(cards,card(a,n,false,true),a);
        }
    }
    public static void calendar(MainActivity a,LinearLayout container,LocalDate date){
        List<StickyNotesStore.Note> notes=StickyNotesStore.get(a).onDay(date);
        if(notes.isEmpty())return;
        a.subtitle(container,"Notas adhesivas de este día · "+notes.size());
        LinearLayout cards=a.column();container.addView(cards);
        for(StickyNotesStore.Note note:notes)attach(cards,card(a,note,false,true),a);
    }
    public static void showEditor(MainActivity a,StickyNotesStore.Note original){
        ensureDefaultCategory(a);
        StickyNotesStore.Note note=new StickyNotesStore.Note();
        if(original!=null){note.id=original.id;note.title=original.title;note.body=original.body;
            note.day=original.day;note.category=original.category;note.color=original.color;}
        else{note.day=a.page==1?a.selectedDay:LocalDate.now();note.category="Notas";}
        LinearLayout form=a.column();form.setPadding(dp(a,18),dp(a,12),dp(a,18),dp(a,20));
        LinearLayout heading=a.row();heading.setGravity(Gravity.CENTER_VERTICAL);
        heading.addView(ApprovedPng.view(a,"sticky_note",42),new LinearLayout.LayoutParams(dp(a,46),dp(a,46)));
        TextView header=text(a,original==null?"Nueva nota adhesiva":"Editar nota adhesiva",19,UiDesign.INK);
        LinearLayout.LayoutParams headingText=new LinearLayout.LayoutParams(0,-2,1);headingText.leftMargin=dp(a,10);
        heading.addView(header,headingText);form.addView(heading);a.gap(form,14);
        form.addView(text(a,"Título de la nota",14,UiDesign.INK));a.gap(form,6);
        EditText title=a.input("Ej. Se acabó el gas",note.title,android.text.InputType.TYPE_CLASS_TEXT|
            android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        title.setSingleLine(true);
        title.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(90)});
        UiDesign.text(title,true);form.addView(title);a.gap(form,14);
        form.addView(text(a,"Contenido (opcional)",14,UiDesign.INK));a.gap(form,6);
        EditText body=a.input("Escribe aquí tu nota...",note.body,android.text.InputType.TYPE_CLASS_TEXT|
            android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE|
            android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        body.setSingleLine(false);body.setMinLines(2);body.setMaxLines(5);
        body.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(2000)});
        UiDesign.text(body,true);form.addView(body);a.gap(form,14);
        form.addView(text(a,"Fecha de la nota · sin hora límite",14,UiDesign.INK));a.gap(form,7);
        final LocalDate[] day={note.day};
        final Runnable[] refreshPreview={null};
        Button chooseDate=a.button("",()->{});ApprovedPng.button(chooseDate,"date",26);
        chooseDate.setContentDescription("Elegir fecha de la nota adhesiva");
        Runnable showDate=()->chooseDate.setText(day[0].format(DateTimeFormatter.ofPattern("EEEE d MMM yyyy",ES))+"   ›");
        chooseDate.setOnClickListener(v->ModernPickers.showDateForNote(a,day[0],picked->{day[0]=picked;showDate.run();refreshPreview[0].run();}));
        form.addView(chooseDate,new LinearLayout.LayoutParams(-1,dp(a,58)));showDate.run();a.gap(form,14);
        form.addView(text(a,"Categoría",14,UiDesign.INK));a.gap(form,7);
        final String[] category={note.category};
        Button chooseCategory=a.button(category[0]+"  ›",()->{});
        ApprovedPng.button(chooseCategory,"sticky_note",26);
        chooseCategory.setOnClickListener(v->ModernPickers.showCategory(a,category[0],chosen->{
            category[0]=chosen;chooseCategory.setText(chosen+"  ›");refreshPreview[0].run();}));
        form.addView(chooseCategory,new LinearLayout.LayoutParams(-1,dp(a,58)));a.gap(form,6);
        form.addView(a.button("＋  Nueva categoría",()->a.showCategoryEditor(null,created->{
            category[0]=created;chooseCategory.setText(created+"  ›");refreshPreview[0].run();})));
        a.gap(form,14);form.addView(text(a,"Color de la nota",14,UiDesign.INK));a.gap(form,7);
        final int[] color={note.color};
        HorizontalScrollView swatches=new HorizontalScrollView(a);swatches.setHorizontalScrollBarEnabled(false);
        LinearLayout palette=a.row();swatches.addView(palette);
        final Button[] colorButtons=new Button[COLORS.length];
        for(int i=0;i<COLORS.length;i++){
            final int idx=i;Button swatch=new Button(a);swatch.setText(" ");swatch.setMinimumWidth(0);
            swatch.setContentDescription("Color "+COLOR_LABELS[i]);
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(dp(a,42),dp(a,42));lp.rightMargin=dp(a,8);
            palette.addView(swatch,lp);colorButtons[i]=swatch;
            swatch.setOnClickListener(v->{color[0]=idx;refreshPreview[0].run();});
        }
        form.addView(swatches);a.gap(form,13);
        form.addView(text(a,"Vista previa",16,UiDesign.INK));a.gap(form,8);
        FrameLayout preview=new FrameLayout(a);
        form.addView(preview,new LinearLayout.LayoutParams(-1,dp(a,238)));
        refreshPreview[0]=()->{
            StickyNotesStore.Note draft=new StickyNotesStore.Note();
            draft.title=title.getText().toString();draft.body=body.getText().toString();
            draft.day=day[0];draft.category=category[0];draft.color=color[0];
            preview.removeAllViews();preview.addView(card(a,draft,true,false),new FrameLayout.LayoutParams(-1,-1));
            for(int i=0;i<colorButtons.length;i++){
                android.graphics.drawable.GradientDrawable bg=UiDesign.shape(a,COLORS[i],12,
                    i==color[0]?UiDesign.BLUE:UiDesign.BORDER);
                if(i==color[0])bg.setStroke(dp(a,3),UiDesign.BLUE);
                colorButtons[i].setBackground(bg);
            }
        };
        TextWatcher watch=new TextWatcher(){public void beforeTextChanged(CharSequence s,int st,int c,int af){}
            public void onTextChanged(CharSequence s,int st,int before,int count){refreshPreview[0].run();}
            public void afterTextChanged(Editable value){}
        };
        title.addTextChangedListener(watch);body.addTextChangedListener(watch);
        refreshPreview[0].run();
        ScrollView sc=new WindowLayout.DialogScroll(a);sc.setFillViewport(false);sc.addView(form);
        AlertDialog dialog=a.dialogBuilder().setTitle(original==null?"Crear nota":"Editar nota")
            .setView(sc).setNegativeButton("Cancelar",null).setPositiveButton("Guardar",null)
            .setNeutralButton(original!=null?"Eliminar":null,null).create();
        dialog.setOnShowListener(d->{
            if(original!=null)dialog.getButton(DialogInterface.BUTTON_NEUTRAL).setOnClickListener(v->{
                a.dialogBuilder().setTitle("Eliminar nota adhesiva")
                    .setMessage("Esta nota se borrará. No afectará las tareas ni los avisos.")
                    .setNegativeButton("Cancelar",null).setPositiveButton("Eliminar",(confirm,which)->{
                        StickyNotesStore.get(a).delete(original.id);dialog.dismiss();a.forceRefresh=true;a.render();
                    }).show();
            });
            dialog.getButton(DialogInterface.BUTTON_POSITIVE).setOnClickListener(v->{
                String name=title.getText().toString().trim();
                if(name.isEmpty()){title.setError("Escribe un título para tu nota.");return;}
                note.title=name;note.body=body.getText().toString().trim();
                note.day=day[0];note.category=category[0];note.color=color[0];
                try{StickyNotesStore.get(a).save(note);}catch(RuntimeException e){a.toast("No se pudo guardar la nota.");return;}
                dialog.dismiss();a.forceRefresh=true;
                if(a.page==0)a.selectedCategory=note.category;
                a.render();a.toast("Nota adhesiva guardada para el "+note.day.format(DateTimeFormatter.ofPattern("d MMM yyyy",ES))+".");
            });
        });
        dialog.show();
        dialog.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE|
                android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
    }
}
