from pathlib import Path
import shutil
src=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=src/"MainActivity.java"
s=main.read_text(encoding="utf8")
assert "View dynamicAddButton()" in s and "void openQuickActions()" in s
shutil.copyfile("updates/plus37/TopPlusMotion.java",src/"TopPlusMotion.java")
# Preserve the 3.7 FAB click and geometry; animate only the glyph around its true center.
anchor="plus.setOnClickListener(v->openQuickActions());"
assert anchor in s, "Missing 3.7 plus-button click anchor"
s=s.replace(anchor,'''plus.setOnClickListener(v->{
            plus.setPivotX(plus.getWidth()/2f);plus.setPivotY(plus.getHeight()/2f);
            plus.animate().cancel();
            plus.animate().rotation(45f).scaleX(.91f).scaleY(.91f).setDuration(140)
                .withEndAction(()->plus.animate().rotation(0f).scaleX(1f).scaleY(1f)
                    .setDuration(280).setInterpolator(new android.view.animation.OvershootInterpolator(1.2f)).start()).start();
            openQuickActions();
        });''',1)
# Native staggered menu entrance; layout bounds and gravity unchanged.
needle="menu.setAlpha(0f);menu.setTranslationY(-dp(18));menu.animate().alpha(1f).translationY(0f).setDuration(240).start();"
assert needle in s, "Missing 3.7 menu animation anchor"
s=s.replace(needle,'''menu.setPivotX(menu.getWidth()/2f);menu.setPivotY(0f);
        menu.setAlpha(0f);menu.setTranslationY(-dp(14));
        menu.animate().alpha(1f).translationY(0f).setDuration(260)
            .setInterpolator(new android.view.animation.DecelerateInterpolator()).start();''',1)
# Preserve all existing quick-action callbacks and labels.
main.write_text(s,encoding="utf8")
gradle=Path("AgendaClara/app/build.gradle")
g=gradle.read_text(encoding="utf8")
assert "versionCode 27" in g and "versionName '3.7.0'" in g
gradle.write_text(g.replace("versionCode 27","versionCode 28").replace("versionName '3.7.0'","versionName '3.7.1'"),encoding="utf8")
print("PASS: centered top plus motion installed over 3.7, version 3.7.1")
