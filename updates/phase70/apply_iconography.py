#!/usr/bin/env python3
"""Fases 26–27: instala iconografía verificada sobre fuentes reconstruidas, sin publicar.
Ejecutar tras phase69 y antes de Gradle. Idempotente; evita sobrescribir arte diferente.
"""
from pathlib import Path
import hashlib
import re
import struct
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = Path("AgendaClara/app/src/main")
JAVA = ROOT / "java/pe/agendaclara/app"
DRAWABLE = ROOT / "res/drawable-nodpi"
SOURCES = [
    ("AgendaClara_Fase24_4_40_Cursos_PNG.zip", "07e48926071c703c353207e27f54715229b63dc89d1fb6d85743334846b33d07", 40),
    ("AgendaClara_Fase24_5_28_Complementarios_PNG.zip", "deded75b4144fc0ea50727e7a9d594412a7961323b9c9ec8a40a53873ad562be", 28),
]

JAVA_TEMPLATE = r'''package pe.agendaclara.app;

import android.content.Context;
import java.text.Normalizer;
import java.util.Locale;

/** Iconografía: resuelve curso -> recurso sin cambiar datos persistidos. */
public final class IconografiaFase26 {
    private static final String[] SUBJECTS = { @@SUBJECT_NAMES@@ };
    private IconografiaFase26() {}

    public static int drawable(Context context, String resourceName) {
        if (context == null || resourceName == null ||
                !resourceName.matches("[a-z][a-z0-9_]*")) return 0;
        return context.getResources().getIdentifier(
                resourceName, "drawable", context.getPackageName());
    }

    public static String subjectResourceName(String courseName) {
        if (courseName == null) return "ic_subject_general";
        String key = Normalizer.normalize(courseName, Normalizer.Form.NFD)
                .replaceAll("\\p{M}+", "").toLowerCase(Locale.ROOT)
                .replaceAll("[^a-z0-9]+", "_").replaceAll("^_+|_+$", "");
        if (key.equals("matematica")) key = "matematicas";
        else if (key.equals("informatica") || key.equals("computacion")) key = "programacion";
        else if (key.equals("educacion")) key = "pedagogia";
        else if (key.equals("idioma_ingles")) key = "ingles";
        for (String item : SUBJECTS) if (key.equals(item)) return "ic_subject_" + item;
        // Algunas materias personalizadas añaden nivel o unidad al nombre.
        for (String item : SUBJECTS) {
            if (!item.equals("general") && item.length() >= 6
                    && (key.startsWith(item + "_") || key.endsWith("_" + item))) {
                return "ic_subject_" + item;
            }
        }
        return "ic_subject_general";
    }

    public static int subjectDrawable(Context context, String courseName) {
        return drawable(context, subjectResourceName(courseName));
    }
}
'''

def collect():
    items = {}
    counts = []
    for filename, sha, wanted in SOURCES:
        archive = HERE / "assets" / filename
        if not archive.is_file() or hashlib.sha256(archive.read_bytes()).hexdigest() != sha:
            raise RuntimeError("Paquete de arte alterado: " + filename)
        with zipfile.ZipFile(archive) as zipped:
            if zipped.testzip() is not None:
                raise RuntimeError("ZIP dañado: " + filename)
            names = [n for n in zipped.namelist() if n.startswith("png/") and n.endswith(".png")]
            if len(names) != wanted:
                raise RuntimeError(f"{filename}: se esperaban {wanted}, encontrados {len(names)}")
            for name in names:
                basename = Path(name).name
                if not re.fullmatch(r"ic_[a-z0-9_]+\.png", basename):
                    raise RuntimeError("Nombre no válido: " + basename)
                if basename in items:
                    raise RuntimeError("PNG duplicado: " + basename)
                data = zipped.read(name)
                if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
                    raise RuntimeError("No es PNG: " + basename)
                if struct.unpack(">II", data[16:24]) != (256, 256) or data[25] != 6:
                    raise RuntimeError("Dimensión/canal RGBA inesperado: " + basename)
                items[basename] = data
            counts.append(len(names))
    if len(items) != 68 or counts != [40, 28]:
        raise RuntimeError("Catálogo incompleto")
    return items

def replace_once(source, before, after, label):
    if after in source:
        return source
    if source.count(before) != 1:
        raise RuntimeError("Anclaje cambiado, se detiene: " + label)
    return source.replace(before, after, 1)

def run():
    quick = JAVA / "MiDiaQuickActions.java"
    class_card = JAVA / "MiDiaClassCard.java"
    gradle = Path("AgendaClara/app/build.gradle")
    for file in (quick, class_card, gradle):
        if not file.is_file() or not DRAWABLE.is_dir():
            raise RuntimeError("Faltan fuentes reconstruidas o phase69: " + str(file))

    items = collect()
    for basename, data in items.items():
        dest = DRAWABLE / basename
        if dest.exists() and dest.read_bytes() != data:
            raise RuntimeError("Colisión de recurso, sin sobrescribir: " + basename)

    subjects = sorted(name[len("ic_subject_"):-4] for name in items
                      if name.startswith("ic_subject_"))
    if len(subjects) != 40 or "general" not in subjects:
        raise RuntimeError("No hay 40 materias y fallback general")
    java = JAVA_TEMPLATE.replace("@@SUBJECT_NAMES@@",
            ", ".join('"' + value + '"' for value in subjects))
    catalog = JAVA / "IconografiaFase26.java"
    if catalog.exists() and catalog.read_text(encoding="utf-8") != java:
        raise RuntimeError("Clase existente distinta, no sobrescrita")

    old_quick = quick.read_text(encoding="utf-8")
    for route in ("VoiceQuickTask.show(activity)", "activity.openEditor(-1, null, null)",
                  "StickyNotesUi.showEditor(activity, null)"):
        if route not in old_quick:
            raise RuntimeError("Ruta rápida modificada: " + route)
    quick_before = "ImageView artwork = ApprovedPng.view(activity, png, 36);"
    quick_after = '''ImageView artwork = ApprovedPng.view(activity, png, 36);
        String nuevo = "voice_microphone".equals(png) ? "ic_quick_task" :
                "save".equals(png) ? "ic_quick_new_task" :
                "sticky_note".equals(png) ? "ic_quick_new_note" : null;
        if (nuevo != null) {
            int icono = IconografiaFase26.drawable(activity, nuevo);
            if (icono != 0) artwork.setImageResource(icono);
        }'''
    new_quick = replace_once(old_quick, quick_before, quick_after, "tres accesos rápidos")

    old_class = class_card.read_text(encoding="utf-8")
    card_before = 'cap.setImageDrawable(new UiDesign.OutlineIcon("graduation", VIOLET));'
    card_after = '''int subjectIcon = selection == null ? 0 :
                IconografiaFase26.subjectDrawable(a, selection.entry.course);
        if (subjectIcon != 0) cap.setImageResource(subjectIcon);
        else cap.setImageDrawable(new UiDesign.OutlineIcon("graduation", VIOLET));'''
    new_class = replace_once(old_class, card_before, card_after, "tarjeta de próxima clase")

    old_gradle = gradle.read_text(encoding="utf-8")
    if "versionCode 58" in old_gradle and "versionName '3.13.2'" in old_gradle:
        new_gradle = old_gradle
    else:
        if old_gradle.count("versionCode 57") != 1 or old_gradle.count("versionName '3.13.1'") != 1:
            raise RuntimeError("Versiones no reconocidas, no editar")
        new_gradle = old_gradle.replace("versionCode 57", "versionCode 58", 1).replace(
                "versionName '3.13.1'", "versionName '3.13.2'", 1)
    # Escribir solamente después de validar todo; no alterar fuentes de usuario.
    for name, data in items.items():
        dest = DRAWABLE / name
        if not dest.exists():
            dest.write_bytes(data)
    if not catalog.exists():
        catalog.write_text(java, encoding="utf-8")
    if new_quick != old_quick: quick.write_text(new_quick, encoding="utf-8")
    if new_class != old_class: class_card.write_text(new_class, encoding="utf-8")
    if new_gradle != old_gradle: gradle.write_text(new_gradle, encoding="utf-8")
    print("PASS fase26: 68 PNG originales, 40 materias y 28 complementarios")
    print("PASS: iconos conectados a accesos rápidos y tarjeta de clase")
    print("PASS: conserva rutas funcionales, archivos existentes, aplicación y firma; versión 3.13.2 (58)")

if __name__ == "__main__":
    run()
