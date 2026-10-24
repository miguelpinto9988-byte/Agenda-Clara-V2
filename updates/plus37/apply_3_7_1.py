from pathlib import Path
import shutil
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=src/"MainActivity.java"
s=main.read_text(encoding="utf8")
print("DEBUG 3.7 FAB source:",s[s.find("dynamicAddButton"):s.find("dynamicAddButton")+1600],flush=True)
shutil.copyfile("updates/plus37/TopPlusMotion.java",src/"TopPlusMotion.java")
s=s.replace('Button plus=button("+",()->openQuickActions());','Button plus=button("+",()->openQuickActions());',1)
needle='plus.setOnTouchListener((v,e)->{'
assert needle in s
s=s.replace(needle,'''plus.setOnClickListener(v->{
            v.animate().cancel();
            v.setPivotX(v.getWidth()/2f);v.setPivotY(v.getHeight()/2f);
            v.animate().rotation(45f).scaleX(.92f).scaleY(.92f).setDuration(125)
                .withEndAction(()->v.animate().rotation(0f).scaleX(1f).scaleY(1f)
                    .setDuration(280).setInterpolator(new android.view.animation.OvershootInterpolator(1.2f)).start()).start();
            openQuickActions();
        });
        plus.setOnTouchListener((v,e)->{''',1)
needle='trackDialog(menu);menu.show();'
assert needle in s
s=s.replace(needle,'''trackDialog(menu);menu.show();
        panel.setAlpha(0f);panel.setTranslationY(-dp(14));
        panel.setPivotX(panel.getWidth()/2f);panel.setPivotY(0f);
        panel.animate().alpha(1f).translationY(0f).setDuration(260)
            .setInterpolator(new android.view.animation.DecelerateInterpolator()).start();''',1)
main.write_text(s,encoding="utf8")
gradle=Path("AgendaClara/app/build.gradle")
g=gradle.read_text(encoding="utf8")
assert "versionCode 27" in g and "versionName '3.7.0'" in g
gradle.write_text(g.replace("versionCode 27","versionCode 28").replace("versionName '3.7.0'","versionName '3.7.1'"),encoding="utf8")
print("PASS: centered top plus motion installed over 3.7, version 3.7.1")
