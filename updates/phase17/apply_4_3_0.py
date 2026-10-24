from pathlib import Path
import shutil
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
shutil.copyfile("updates/phase17/AgendaDraw.java",root/"AgendaDraw.java")
(root/"graphics").mkdir(exist_ok=True)
shutil.copyfile("updates/phase17/AgendaGraphics.kt",root/"graphics/AgendaGraphics.kt")
p=root/"MainActivity.java"
s=p.read_text()
old='parent.setBackground(outlined(0xffffffff,22,0xffdbe7ff));parent.setElevation(dp(3));'
if old in s:
    s=s.replace(old,'parent.setBackground(AgendaDraw.gradientCard(22,this));parent.setElevation(dp(3));',1)
else:
    print('Community-card anchor absent; retain existing style and integrate graphics primitives only')
p.write_text(s)
g=Path("AgendaClara/app/build.gradle")
z=g.read_text()
assert "versionCode 32" in z and "versionName '4.2.0'" in z
g.write_text(z.replace("versionCode 32","versionCode 33").replace("versionName '4.2.0'","versionName '4.3.0'"))
print("Phase 3 drawing library installed: native cards + Compose Canvas components")
