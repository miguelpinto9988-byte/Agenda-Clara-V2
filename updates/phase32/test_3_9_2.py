#!/usr/bin/env python3
from pathlib import Path
S=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(S/"MainActivity.java").read_text(encoding="utf-8")
ui=(S/"UiDesign.java").read_text(encoding="utf-8")
cat=(S/"CategoryRegistry.java").read_text(encoding="utf-8")
picker=(S/"ModernPickers.java").read_text(encoding="utf-8")
nav=main[main.index("        nav=row();"):main.index("        View line=new View(this);")]
assert 'new UiDesign.OutlineIcon(' in nav and 'dp(26),dp(26)' in nav
assert 'ContentIconSizing.apply(nav)' not in main
chips=main[main.index("        for(String label:categories){"):main.index("        categoriesScroll.addView(categoryChips);")]
assert "ApprovedPng.button(chip,CategoryRegistry.icon(this,label),24)" in chips
assert "chip.setCompoundDrawablePadding(dp(11))" in chips
assert "chip.setMinHeight(dp(54))" in chips
assert "chip.setSingleLine(true)" in chips
assert "TruncateAt.END" in chips
assert "chip.setContentDescription(" in chips
style=ui[ui.index("    public static void categoryChip("):ui.index("    public static void card(")]
assert 'OutlineIcon("folder"' not in style
assert "setCompoundDrawables(" not in style
assert "iconSpace.rightMargin=dp(12)" in main
assert "detailIconSpace.rightMargin=dp(10)" in main
assert "categoryHeadingIcon.setImageDrawable" in main
assert "CategoryRegistry.icon(this,selected)" in main and "CategoryRegistry.icon(this,newName)" in main
assert "CategoryRegistry.icon(this,task.category)" in main
assert "CategoryRegistry.icon(a,chosen)" in picker
assert 'return "Notas".equalsIgnoreCase(category)?"sticky_note":"other";' in cat
assert '"folder".equalsIgnoreCase(symbol.trim())' in cat
assert 'record.optString("icon","other")' in cat
assert 'return "other";' in cat
assert 'versionCode 33' in Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
assert "versionName '3.9.2'" in Path("AgendaClara/app/build.gradle").read_text(encoding="utf-8")
print("PASS phase32: category icons reflect selection, bold chip/padding, legacy icon fallback, original bottom navigation preserved")
