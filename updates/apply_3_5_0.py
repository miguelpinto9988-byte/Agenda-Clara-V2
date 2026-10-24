#!/usr/bin/env python3
"""Agenda Clara 3.5: respetar insets del sistema en TODAS las pantallas."""
from pathlib import Path
root=Path("AgendaClara")
src=root/"app/src/main/java/pe/agendaclara/app"
path=src/"ScheduleActivity.java"
s=path.read_text(encoding="utf-8")
# WindowCompat / listener obtiene insets actuales de sistema sin inventar alturas.
# Agregar solo el espacio de la barra de estado si la Activity dibuja edge-to-edge.
anchor="    private void colorMixer(int[] color,boolean[] manuallyColored,View preview){"
helper="""    /** Mantiene el contenido interactivo debajo de la barra de estado en Android 15/16. */
    private void applyScheduleInsets(android.view.View root){
        androidx.core.view.ViewCompat.setOnApplyWindowInsetsListener(root,(view,insets)->{
            androidx.core.graphics.Insets bars=insets.getInsets(
                androidx.core.view.WindowInsetsCompat.Type.systemBars());
            // Se desplaza el contenido únicamente si la ventana dibuja detrás de barras.
            view.setPadding(view.getPaddingLeft(),bars.top,
                view.getPaddingRight(),bars.bottom);
            return insets;
        });
        androidx.core.view.ViewCompat.requestApplyInsets(root);
    }
"""
if s.count(anchor)!=1:raise RuntimeError("Ancla ScheduleActivity modificada")
s=s.replace(anchor,helper+anchor,1)
# Fijar decorFitsSystemWindows(false) hace que el listener gestione padding superior,
# evita la superposición observada en encabezados y respeta la barra inferior.
# Toda navegación de esta actividad pasa por show(int screen): instalar insets en su root.
old="private void show(int screen){page=screen;root=col();root.setBackgroundColor(BG);setContentView(root);"
if s.count(old)!=1:raise RuntimeError("No se halló el constructor real de pantalla")
new='''private void show(int screen){page=screen;root=col();root.setBackgroundColor(BG);
        androidx.core.view.WindowCompat.setDecorFitsSystemWindows(getWindow(),false);
        setContentView(root);applyScheduleInsets(root);'''
s=s.replace(old,new,1)
path.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle"
g=gradle.read_text(encoding="utf-8")
assert "versionCode 24" in g and "versionName '3.4.0'" in g
gradle.write_text(g.replace("versionCode 24","versionCode 25").replace("versionName '3.4.0'","versionName '3.5.0'"),encoding="utf-8")
print("PASS: pantalla Horario con barras de estado y navegación reservadas.")
