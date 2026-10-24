from pathlib import Path
import shutil
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
shutil.copyfile("updates/phase18/AgendaSparkleView.java",root/"AgendaSparkleView.java")
p=root/"MainActivity.java"
s=p.read_text()
# Add decorative sparkles to the existing native FAB container without changing click handling.
anchor="plus.setStateListAnimator(null);"
if anchor in s:
    s=s.replace(anchor,'''plus.setStateListAnimator(null);
        AgendaSparkleView sparkles=new AgendaSparkleView(this);
        sparkles.setClickable(false);sparkles.setFocusable(false);
        if(frame instanceof android.widget.FrameLayout){
            android.widget.FrameLayout f=(android.widget.FrameLayout)frame;
            f.addView(sparkles,0,new android.widget.FrameLayout.LayoutParams(-1,-1));
        }
        ''',1)
else:
    print("FAB anchor unavailable; sparkle view is installed for subsequent screen integration")
# Unify card appearance while keeping original interaction and padding.
anchor="parent.setBackground(outlined(0xffffffff,22,0xffdbe7ff));"
if anchor in s:
    s=s.replace(anchor,"parent.setBackground(AgendaDraw.gradientCard(22,this));",1)
p.write_text(s)
g=Path("AgendaClara/app/build.gradle")
z=g.read_text()
assert "versionCode 33" in z and "versionName '4.3.0'" in z
g.write_text(z.replace("versionCode 33","versionCode 34").replace("versionName '4.3.0'","versionName '4.4.0'"))
print("Phase 4 visual detail integration installed")
