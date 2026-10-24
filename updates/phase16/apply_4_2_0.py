from pathlib import Path
import shutil
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
shutil.copyfile("updates/phase16/MotionKit.java",root/"MotionKit.java")
p=root/"MainActivity.java"
s=p.read_text()
# Replace the duplicated per-screen choreography with a shared, tested native motion API.
old='''line.setAlpha(0f);line.setTranslationX(dp(28));
            menu.addView(line,new LinearLayout.LayoutParams(dp(278),dp(57)));'''
new='''menu.addView(line,new LinearLayout.LayoutParams(dp(278),dp(57)));'''
assert old in s
s=s.replace(old,new,1)
start='''if(android.animation.ValueAnimator.areAnimatorsEnabled())for(int n=0;n<5;n++){
            View item=menu.getChildAt(n);item.animate().alpha(1f).translationX(0f)
                .setStartDelay(45L+n*48L).setDuration(240).setInterpolator(new android.view.animation.DecelerateInterpolator()).start();
        }else for(int n=0;n<5;n++){View item=menu.getChildAt(n);item.setAlpha(1f);item.setTranslationX(0f);}'''
assert start in s
s=s.replace(start,'''for(int n=0;n<5;n++)MotionKit.enter(menu.getChildAt(n),n);''',1)
old='''filterPanel.setAlpha(0f);filterPanel.setTranslationY(-dp(10));filterPanel.setVisibility(View.VISIBLE);
                filterPanel.animate().alpha(1f).translationY(0f).setDuration(240).setInterpolator(new android.view.animation.DecelerateInterpolator()).start();'''
assert old in s
s=s.replace(old,'''MotionKit.expand(filterPanel);''',1)
old='''else {filterPanel.animate().cancel();filterPanel.setVisibility(View.GONE);}'''
assert old in s
s=s.replace(old,'''else MotionKit.collapse(filterPanel);''',1)
old='''if(expanded){inner.setAlpha(0f);inner.setTranslationY(-dp(16));inner.setVisibility(View.VISIBLE);
                        inner.animate().alpha(1f).translationY(0f).setDuration(280)
                            .setInterpolator(new android.view.animation.DecelerateInterpolator()).start();}
                    else {inner.animate().alpha(0f).translationY(-dp(10)).setDuration(170)
                        .withEndAction(()->{inner.setVisibility(View.GONE);inner.setAlpha(1f);inner.setTranslationY(0f);}).start();}'''
assert old in s
s=s.replace(old,'''if(expanded)MotionKit.expand(inner);
                    else MotionKit.collapse(inner);''',1)
# Make the blue plus react to touch without interfering with its existing click action.
old='''plus.setStateListAnimator(null);return frame;'''
assert old in s
s=s.replace(old,'''plus.setStateListAnimator(null);
        frame.setOnTouchListener((v,event)->{
            if(event.getActionMasked()==android.view.MotionEvent.ACTION_DOWN)MotionKit.press(plus);
            return false;
        });return frame;''',1)
p.write_text(s)
gradle=Path("AgendaClara/app/build.gradle")
g=gradle.read_text()
assert "versionCode 31" in g and "versionName '4.1.0'" in g
gradle.write_text(g.replace("versionCode 31","versionCode 32").replace("versionName '4.1.0'","versionName '4.2.0'"))
print("Phase 2 native motion integrated",len(s))
