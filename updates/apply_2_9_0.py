#!/usr/bin/env python3
"""Agenda Clara 2.9.0 | Etapa 1: espectro amplio para los horarios (offline)."""
from pathlib import Path
import textwrap

root=Path("AgendaClara")
source=root/"app/src/main/java/pe/agendaclara/app"
def save_java(filename, java):
    (source/filename).write_text(textwrap.dedent(java).lstrip(),encoding="utf-8")
def replace(path, before, after):
    p=source/path
    old=p.read_text(encoding="utf-8")
    if old.count(before)!=1:
        raise RuntimeError(f"ETAPA 1: ancla inesperada en {path}: {before[:70]}")
    p.write_text(old.replace(before,after,1),encoding="utf-8")

save_java("ScheduleColorSpectrum.java",r'''
package pe.agendaclara.app;
/** Catálogo determinista: 30 matices × 12 variaciones = 360 colores, sin red. */
public final class ScheduleColorSpectrum {
    private ScheduleColorSpectrum() {}
    public static final int PER_FAMILY=90;
    public static final int FAMILY_COUNT=4;
    private static final float[][] OPTIONS={
       {.32f,.98f},{.42f,.97f},{.52f,.96f},  // pasteles
       {.92f,.96f},{.78f,.94f},{.68f,.98f},  // vivos
       {.78f,.58f},{.68f,.70f},{.85f,.45f},  // profundos
       {.24f,.86f},{.35f,.79f},{.45f,.83f}   // suaves
    };
    public static int[] palette(){
        int[] out=new int[360];int index=0;
        for(float[] variant:OPTIONS)
            for(int h=0;h<360;h+=12)
                out[index++]=ScheduleCourseColors.hsv(h,variant[0],variant[1]);
        return out;
    }
    public static String familyTitle(int family){
        switch(family){
            case 0:return "Pasteles · 90";
            case 1:return "Vivos · 90";
            case 2:return "Profundos · 90";
            default:return "Suaves · 90";
        }
    }
    public static int parseHex(String value){
        String hex=value==null?"":value.trim();
        if(!hex.matches("#?[0-9a-fA-F]{6}"))throw new IllegalArgumentException("Color hexadecimal inválido");
        if(hex.startsWith("#"))hex=hex.substring(1);
        return 0xff000000 | Integer.parseInt(hex,16);
    }
}
''')

replace("ScheduleActivity.java",
    'form.addView(txt("Color del curso · 72 tonos y espectro completo",13,INK,true));',
    'form.addView(txt("Color del curso · 72 tonos rápidos + 360 tonos en catálogo",13,INK,true));')
target='form.addView(btn("Más colores · Mezclador HSV",()->colorMixer(color,manuallyColored,colorPreview),false));'
replace("ScheduleActivity.java",target,target+
    '\n        space(form,7);form.addView(btn("Explorar 360 colores · Pasteles, vivos, profundos y suaves",()->colorCatalog(color,manuallyColored,colorPreview),false));')
method=r'''    private void colorCatalog(int[] color,boolean[] manuallyColored,View preview){
        LinearLayout panel=col();panel.setPadding(dp(14),dp(8),dp(14),dp(10));
        panel.addView(txt("Catálogo completo sin conexión · 360 combinaciones",14,INK,true));
        panel.addView(txt("Selecciona un tono o escribe el HEX exacto.",12,MUTED,false));
        space(panel,10);
        EditText hex=new EditText(this);hex.setSingleLine(true);
        hex.setText(String.format(Locale.ROOT,"#%06X",color[0]&0xffffff));
        hex.setHint("#RRGGBB");panel.addView(hex);
        TextView sample=txt("Vista previa",14,ScheduleCourseColors.accessibleText(color[0]),true);
        sample.setGravity(Gravity.CENTER);sample.setPadding(dp(10),dp(10),dp(10),dp(10));
        sample.setBackground(bg(color[0],11));panel.addView(sample);
        int[] selected={color[0]};
        android.widget.ScrollView scroll=new android.widget.ScrollView(this);
        LinearLayout content=col();int[] spectrum=ScheduleColorSpectrum.palette();
        for(int family=0;family<ScheduleColorSpectrum.FAMILY_COUNT;family++){
            space(content,10);
            content.addView(txt(ScheduleColorSpectrum.familyTitle(family),14,INK,true));
            android.widget.GridLayout swatches=new android.widget.GridLayout(this);swatches.setColumnCount(8);
            for(int ix=family*ScheduleColorSpectrum.PER_FAMILY;ix<(family+1)*ScheduleColorSpectrum.PER_FAMILY;ix++){
                final int swatchColor=spectrum[ix];
                View chip=new View(this);
                GradientDrawable oval=new GradientDrawable();
                oval.setShape(GradientDrawable.OVAL);oval.setColor(swatchColor);
                oval.setStroke(dp(1),LINE);chip.setBackground(oval);
                android.widget.GridLayout.LayoutParams lp=new android.widget.GridLayout.LayoutParams();
                lp.width=dp(27);lp.height=dp(27);
                lp.setMargins(dp(3),dp(3),dp(3),dp(3));swatches.addView(chip,lp);
                chip.setContentDescription(String.format(Locale.ROOT,"Seleccionar #%06X",swatchColor&0xffffff));
                chip.setOnClickListener(v->{
                    selected[0]=swatchColor;
                    hex.setText(String.format(Locale.ROOT,"#%06X",swatchColor&0xffffff));
                    sample.setBackground(bg(swatchColor,11));
                    sample.setTextColor(ScheduleCourseColors.accessibleText(swatchColor));
                    sample.setText(String.format(Locale.ROOT,"#%06X",swatchColor&0xffffff));
                });
            }
            content.addView(swatches);
        }
        scroll.addView(content);
        panel.addView(scroll,new LinearLayout.LayoutParams(-1,dp(310)));
        AlertDialog dialog=new AlertDialog.Builder(this)
            .setTitle("Colores del horario")
            .setView(panel).setNegativeButton("Cancelar",null)
            .setPositiveButton("Aplicar",null).create();
        dialog.setOnShowListener(unused->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            try{selected[0]=ScheduleColorSpectrum.parseHex(hex.getText().toString());}
            catch(IllegalArgumentException ex){hex.setError("Usa #RRGGBB");return;}
            color[0]=selected[0];manuallyColored[0]=true;
            preview.setBackground(bg(color[0],13));dialog.dismiss();
        }));
        dialog.show();
    }
'''
replace("ScheduleActivity.java",'    private void colorMixer(int[] color,boolean[] manuallyColored,View preview){',
        method+'    private void colorMixer(int[] color,boolean[] manuallyColored,View preview){')
gradle=root/"app/build.gradle"
data=gradle.read_text(encoding="utf-8")
if data.count("versionCode 18")!=1 or data.count("versionName '2.8.0'")!=1:
    raise RuntimeError("ETAPA 1: requiere la versión 2.8.0")
gradle.write_text(data.replace("versionCode 18","versionCode 19").replace("versionName '2.8.0'","versionName '2.9.0'"),encoding="utf-8")
print("ETAPA_1_COMPLETADA: 72 tonos favoritos + 360 tonos adicionales + HEX + HSV offline.")
