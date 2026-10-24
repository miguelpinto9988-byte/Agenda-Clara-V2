from pathlib import Path
p=Path('AgendaClara/app/src/main/java/pe/agendaclara/app/MainActivity.java')
s=p.read_text()
assert 'void openQuickActions()' in s and 'View dynamicAddButton()' in s
# Animate page transitions only for navigation; avoid re-animation on background refresh.
s=s.replace('if(!samePage)UiMotion.reveal(body);','if(!samePage)UiMotion.slideReveal(body,page>=renderedPage?1:-1);')
# Improve dynamic FAB: continuous restrained breathing + touch motion
s=s.replace('halo.animate().alpha(.55f).setDuration(650).start();return frame;', '''halo.animate().alpha(.42f).scaleX(1.10f).scaleY(1.10f).setDuration(1150)
            .setInterpolator(new android.view.animation.AccelerateDecelerateInterpolator())
            .withEndAction(()->{if(halo.isAttachedToWindow())halo.animate().alpha(.80f).scaleX(.97f).scaleY(.97f).setDuration(1150).start();}).start();
        plus.setStateListAnimator(null);return frame;''')
# stagger quick action menu: individual rows enter sequentially; reduced motion respected
s=s.replace('menu.addView(line,new LinearLayout.LayoutParams(dp(278),dp(57)));','''line.setAlpha(0f);line.setTranslationX(dp(28));
            menu.addView(line,new LinearLayout.LayoutParams(dp(278),dp(57)));''')
s=s.replace('menu.setAlpha(0f);menu.setTranslationY(-dp(18));menu.animate().alpha(1f).translationY(0f).setDuration(240).start();', '''menu.setAlpha(0f);menu.setTranslationY(-dp(14));
        menu.animate().alpha(1f).translationY(0f).setDuration(240).start();
        if(android.animation.ValueAnimator.areAnimatorsEnabled())for(int n=0;n<5;n++){
            View item=menu.getChildAt(n);item.animate().alpha(1f).translationX(0f)
                .setStartDelay(45L+n*48L).setDuration(240).setInterpolator(new android.view.animation.DecelerateInterpolator()).start();
        }else for(int n=0;n<5;n++){View item=menu.getChildAt(n);item.setAlpha(1f);item.setTranslationX(0f);}''')
# Make filter dropdown animate vertically and preserve clicks
s=s.replace('filterPanel.setAlpha(0f);filterPanel.setVisibility(View.VISIBLE);filterPanel.animate().alpha(1f).setDuration(180).start();','''filterPanel.setAlpha(0f);filterPanel.setTranslationY(-dp(10));filterPanel.setVisibility(View.VISIBLE);
                filterPanel.animate().alpha(1f).translationY(0f).setDuration(240).setInterpolator(new android.view.animation.DecelerateInterpolator()).start();''')
s=s.replace('else filterPanel.setVisibility(View.GONE);filterPill.setText(','''else {filterPanel.animate().cancel();filterPanel.setVisibility(View.GONE);}
            filterPill.setText(''')
# Improve accordion animation and avoid the jump when collapsing
s=s.replace('inner.setVisibility(expanded?View.VISIBLE:View.GONE);\n                    if(expanded){inner.setAlpha(0f);inner.setTranslationY(-dp(10));inner.animate().alpha(1f).translationY(0f).setDuration(190).start();}', '''inner.animate().cancel();
                    if(expanded){inner.setAlpha(0f);inner.setTranslationY(-dp(16));inner.setVisibility(View.VISIBLE);
                        inner.animate().alpha(1f).translationY(0f).setDuration(280)
                            .setInterpolator(new android.view.animation.DecelerateInterpolator()).start();}
                    else {inner.animate().alpha(0f).translationY(-dp(10)).setDuration(170)
                        .withEndAction(()->{inner.setVisibility(View.GONE);inner.setAlpha(1f);inner.setTranslationY(0f);}).start();}''')
# Distinct visual hierarchy for community cards
s=s.replace('LinearLayout parent=card(list);parent.setTag("chat:"+chat.key);','''LinearLayout parent=card(list);parent.setTag("chat:"+chat.key);
                parent.setBackground(outlined(0xffffffff,22,0xffdbe7ff));parent.setElevation(dp(3));''')
# More polished calendar surface; fade in on dialog display
s=s.replace('dialog.show();\n    }\n\n    void openEditor(','''dialog.show();
        if(dialog.getWindow()!=null){dialog.getWindow().setBackgroundDrawableResource(android.R.color.transparent);
            dialog.getWindow().setLayout(getResources().getDisplayMetrics().widthPixels-dp(24),-2);}
        panel.setAlpha(0f);panel.setTranslationY(dp(18));panel.animate().alpha(1f).translationY(0f)
            .setDuration(260).setInterpolator(new android.view.animation.DecelerateInterpolator()).start();
    }

    void openEditor(''')
# Form entrance transition; retain dialog behavior
s=s.replace('});editor.show();editor.getWindow().setSoftInputMode(','''});editor.show();
        if(editor.getWindow()!=null&&android.animation.ValueAnimator.areAnimatorsEnabled()){
            android.view.View decor=editor.getWindow().getDecorView();decor.setAlpha(0f);decor.setTranslationY(dp(22));
            decor.animate().alpha(1f).translationY(0f).setDuration(280).start();}
        editor.getWindow().setSoftInputMode(''')
p.write_text(s)
q=Path('AgendaClara/app/src/main/java/pe/agendaclara/app/UiMotion.java')
u=q.read_text();u=u.replace('    public static void reveal(View view){','''    public static void slideReveal(View view,int direction){
        if(view==null)return;
        view.animate().cancel();
        if(!ValueAnimator.areAnimatorsEnabled()){view.setAlpha(1f);view.setTranslationX(0f);return;}
        float distance=20f*view.getResources().getDisplayMetrics().density;
        view.setAlpha(0.78f);view.setTranslationX(direction>=0?distance:-distance);
        view.animate().alpha(1f).translationX(0f).setDuration(250)
            .setInterpolator(new android.view.animation.DecelerateInterpolator()).start();
    }
    public static void reveal(View view){''');q.write_text(u)
g=Path('AgendaClara/app/build.gradle');z=g.read_text();assert 'versionCode 29' in z and "versionName '3.9.0'" in z;g.write_text(z.replace('versionCode 29','versionCode 30').replace("versionName '3.9.0'","versionName '4.0.0'"))
print('UI 4.0 motion patch applied',len(s))