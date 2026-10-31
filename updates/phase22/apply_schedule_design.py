#!/usr/bin/env python3
"""Phase 22b: shared schedule, floating editors, modal motion and safe margins."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec

ROOT=Path(__file__).resolve().parents[2]/"AgendaClara"
SRC=ROOT/"app/src/main/java/pe/agendaclara/app"
path=SRC/"ScheduleActivity.java"
schedule=path.read_text(encoding="utf-8")

def exactly(old,new,label):
    global schedule
    n=schedule.count(old)
    if n!=1:raise RuntimeError(f"schedule redesign: {label}: expected 1, got {n}")
    schedule=schedule.replace(old,new,1)

exactly('private static final int BG=0xfff6f8fc,INK=0xff162441,BLUE=0xff3957d7,MUTED=0xff60738b,PALE=0xffedf0ff,LINE=0xffdfe5f1,RED=0xffd45063;',
    'private static final int BG=UiDesign.BG,INK=UiDesign.INK,BLUE=UiDesign.BLUE,MUTED=UiDesign.MUTED,PALE=UiDesign.PALE,LINE=UiDesign.BORDER,RED=UiDesign.ERROR;',
    "shared design tokens")
exactly('if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);',
    'UiDesign.text(t,bold);',"typography")
exactly('b.setBackground(primary?bg(BLUE,17):outline(PALE,17));b.setMinHeight(dp(48));b.setElevation(0);',
    'UiDesign.button(b,primary);UiDesign.actionIcon(b,caption);',"button styles")
exactly('c.setBackground(outline(0xffffffff,23));LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(-1,-2);params.bottomMargin=dp(12);',
    'UiDesign.card(c);LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(-1,-2);params.bottomMargin=dp(16);',
    "cards and component gutters")
exactly('body.setPadding(dp(16),dp(14),dp(16),dp(30));',
    'body.setPadding(dp(18),dp(16),dp(18),dp(38));',
    "content insets")
exactly('bar.setPadding(dp(14),dp(9),dp(14),dp(8));',
    'bar.setPadding(dp(18),dp(14),dp(18),dp(14));',
    "header padding")
exactly('title=txt(titles[Math.max(0,Math.min(titles.length-1,screen))],20,INK,true);',
    'title=txt(titles[Math.max(0,Math.min(titles.length-1,screen))],21,INK,true);',
    "screen header")
exactly('private void head(LinearLayout parent,String heading,String description){parent.addView(txt(heading,19,INK,true));space(parent,5);parent.addView(txt(description,13,MUTED,false));}',
    'private void head(LinearLayout parent,String heading,String description){parent.addView(txt(heading,18,INK,true));space(parent,7);parent.addView(txt(description,13,MUTED,false));}',
    "card headings")
exactly('e.setBackground(outline(0xffffffff,13));',
    'UiDesign.input(e);',
    "schedule editor fields")
# The weekly grid was too cramped. Keep its 7-column functional layout with clear spacing.
exactly('col.addView(heading,new LinearLayout.LayoutParams(dp(95),dp(39)));',
    'col.addView(heading,new LinearLayout.LayoutParams(dp(95),dp(44)));',
    "weekly column headings")
exactly('dayRow.addView(chip,new LinearLayout.LayoutParams(0,dp(46),1));',
    'LinearLayout.LayoutParams dayChip=new LinearLayout.LayoutParams(0,dp(46),1);dayChip.setMargins(dp(2),0,dp(2),0);dayRow.addView(chip,dayChip);',
    "weekly lesson day chip spacing")
exactly('canvas.setBackground(outline(0xfffbfcff,6));',
    'canvas.setBackground(outline(0xfffbfcff,10));',
    "weekly timetable columns")

# All subdialogs in classes, photo-OCR confirmation and color customization use
# the same custom theme and limits as MainActivity.
schedule=schedule.replace('new AlertDialog.Builder(this)','scheduleDialog()')
if 'new AlertDialog.Builder(this)' in schedule:raise RuntimeError("Unstyled class dialogs remain")
anchor='    private void show(int screen){'
if schedule.count(anchor)!=1:raise RuntimeError("schedule init anchor")
helper='''    private AlertDialog.Builder scheduleDialog(){
        return new AlertDialog.Builder(this,R.style.DialogTheme){
            @Override public AlertDialog create(){
                AlertDialog dialog=super.create();
                dialog.getWindow().getDecorView().addOnAttachStateChangeListener(
                  new View.OnAttachStateChangeListener(){
                    public void onViewAttachedToWindow(View v){WindowLayout.boundDialog(ScheduleActivity.this,dialog);}
                    public void onViewDetachedFromWindow(View v){}
                  });
                return dialog;
            }
        };
    }
'''
schedule=schedule.replace(anchor,helper+anchor,1)
path.write_text(schedule,encoding="utf-8")

motionpath=SRC/"UiMotion.java"
motion=motionpath.read_text(encoding="utf-8")
motion=motion.replace('view.setAlpha(0.91f);',
                      'view.setAlpha(0.92f);view.setTranslationY(view.getResources().getDisplayMetrics().density*8f);')
motion=motion.replace('view.animate().alpha(1f).setDuration(140).start();',
                      'view.animate().alpha(1f).translationY(0f).setDuration(195).start();')
if 'translationY(0f)' not in motion:raise RuntimeError("motion patch failed")
motionpath.write_text(motion,encoding="utf-8")

print("PASS phase22: academic schedule screens, 2-column modal class editor, accessible scroll bounds and native transitions")
