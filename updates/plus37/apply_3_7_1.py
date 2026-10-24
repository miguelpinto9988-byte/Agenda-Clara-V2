from pathlib import Path
import shutil
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=src/"MainActivity.java"
s=main.read_text(encoding="utf8")
import re
shutil.copyfile("updates/plus37/TopPlusMotion.java",src/"TopPlusMotion.java")
# Actual 3.7 upper button: U+FF0B and openEditor, not openQuickActions.
needle='Button add=button("＋",()->openEditor(-1,null,null));add.setTag("new_task_button");'
assert s.count(needle)==1,"Upper plus button anchor missing"
s=s.replace(needle,'''Button add=button("＋",()->openEditor(-1,null,null));add.setTag("new_task_button");
        add.setOnClickListener(v->{
            v.animate().cancel();
            v.setPivotX(v.getWidth()/2f);v.setPivotY(v.getHeight()/2f);
            v.animate().rotation(45f).scaleX(.92f).scaleY(.92f).setDuration(125)
                .withEndAction(()->v.animate().rotation(0f).scaleX(1f).scaleY(1f)
                    .setDuration(280).setInterpolator(new android.view.animation.OvershootInterpolator(1.2f)).start()).start();
            openEditor(-1,null,null);
        });''',1)
main.write_text(s,encoding="utf8")
gradle=Path("AgendaClara/app/build.gradle")
g=gradle.read_text(encoding="utf8")
assert "versionCode 27" in g and "versionName '3.7.0'" in g
gradle.write_text(g.replace("versionCode 27","versionCode 28").replace("versionName '3.7.0'","versionName '3.7.1'"),encoding="utf8")
print("PASS: centered top plus motion installed over 3.7, version 3.7.1")
