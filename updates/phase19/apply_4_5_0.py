from pathlib import Path
import shutil
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
for name in ("AgendaIcons.java","AgendaFinish.java"):
    shutil.copyfile("updates/phase19/"+name,root/name)
p=root/"MainActivity.java"
s=p.read_text()
# Replace Unicode glyphs in the existing quick-action menu with a consistent vector icon family.
needle='''TextView circle=text(glyphs[i],24,accents[i],true);circle.setGravity(Gravity.CENTER);
            circle.setBackground(rounded(0xffeef3ff,30));'''
replacement='''TextView circle=text("",24,accents[i],true);circle.setGravity(Gravity.CENTER);
            circle.setBackground(rounded(0xffeef3ff,30));
            android.graphics.drawable.Drawable vector=AgendaIcons.create(i,accents[i]);
            vector.setBounds(0,0,dp(22),dp(22));
            circle.setCompoundDrawables(null,null,vector,null);
            circle.setCompoundDrawablePadding(0);
            circle.setContentDescription(labels[i]);'''
assert needle in s, "quick action icon insertion point missing"
s=s.replace(needle,replacement,1)
# Preserve semantics and touch targets; apply visual finishing to existing community cards.
anchor="parent.setElevation(dp(3));"
if anchor in s:
    s=s.replace(anchor,"AgendaFinish.elevate(parent,3f);",1)
p.write_text(s)
g=Path("AgendaClara/app/build.gradle")
z=g.read_text()
assert "versionCode 34" in z and "versionName '4.4.0'" in z
g.write_text(z.replace("versionCode 34","versionCode 35").replace("versionName '4.4.0'","versionName '4.5.0'"))
print("Phase 5: custom vector icons and visual finishing integrated")
