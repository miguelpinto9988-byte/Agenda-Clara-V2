from pathlib import Path
import shutil
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=src/"MainActivity.java"
s=main.read_text(encoding="utf8")
import re
shutil.copyfile("updates/plus37/TopPlusMotion.java",src/"TopPlusMotion.java")
print("FAB MATCHES:",repr([s[max(0,m.start()-100):m.end()+180] for m in list(re.finditer(r'openQuickActions|new_task_button|setOnTouchListener|dynamicAddButton|quickActions|setOnClickListener',s))[:30]]),flush=True)
# Attach animation to the native quick action entry point without relying on exact whitespace.
# No changes to the existing button geometry or action callbacks.
needle='void openQuickActions(){'
if needle not in s:
    needle='void openQuickActions() {'
assert needle in s,"Quick-action method not found"
s=s.replace(needle,needle+'''
        if(addButton!=null){
            View target=addButton;
            target.animate().cancel();
            target.setPivotX(target.getWidth()/2f);target.setPivotY(target.getHeight()/2f);
            target.animate().rotation(45f).scaleX(.92f).scaleY(.92f).setDuration(125)
                .withEndAction(()->target.animate().rotation(0f).scaleX(1f).scaleY(1f)
                    .setDuration(280).setInterpolator(new android.view.animation.OvershootInterpolator(1.2f)).start()).start();
        }
''',1)
main.write_text(s,encoding="utf8")
gradle=Path("AgendaClara/app/build.gradle")
g=gradle.read_text(encoding="utf8")
assert "versionCode 27" in g and "versionName '3.7.0'" in g
gradle.write_text(g.replace("versionCode 27","versionCode 28").replace("versionName '3.7.0'","versionName '3.7.1'"),encoding="utf8")
print("PASS: centered top plus motion installed over 3.7, version 3.7.1")
