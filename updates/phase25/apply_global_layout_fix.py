#!/usr/bin/env python3
"""Phase25: global bold typography and safe spacing for all native screens and dialogs.

Explicitly keeps the approved top-right + element unchanged. Runs after phase24.
No database, category, reminder, or task-alarm code is modified.
"""
from pathlib import Path
SRC=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/java/pe/agendaclara/app"
RES=Path(__file__).resolve().parents[2]/"AgendaClara/app/src/main/res"

def once(value,old,new,label):
    occurrences=value.count(old)
    if occurrences!=1:
        raise RuntimeError(f"phase25 {label}: expected one match, found {occurrences}")
    return value.replace(old,new,1)

def apply():
    ui_file=SRC/"UiDesign.java"
    main_file=SRC/"MainActivity.java"
    class_file=SRC/"ScheduleActivity.java"
    window_file=SRC/"WindowLayout.java"
    photo_file=SRC/"PhotoConfigActivity.java"
    ui=ui_file.read_text(encoding="utf-8")
    main=main_file.read_text(encoding="utf-8")
    classes=class_file.read_text(encoding="utf-8")
    window=window_file.read_text(encoding="utf-8")
    photo=photo_file.read_text(encoding="utf-8")
    plus=next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)
    if plus is None or "TopPlusButtonMotion.install(this)" not in main:
        raise RuntimeError("Approved top plus missing")

    # All screens/dialogs inherit bold rendering, including labels created by
    # Android (spinners, checkboxes and AlertDialog action buttons).
    ui=once(ui,
      't.setTypeface(Typeface.create(heavy?"sans-serif":"sans-serif-medium",heavy?Typeface.BOLD:Typeface.NORMAL));',
      't.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));',
      "global bold typeface")
    anchor='    public static void actionIcon(Button b,String caption) {'
    methods='''    /** Apply bold to Android-created labels and safe vertical spacing recursively. */
    public static void polishTree(View root){
        if(root==null)return;
        if(root instanceof TextView && !"new_task_button".equals(root.getTag())){
            TextView label=(TextView)root;
            label.setTypeface(Typeface.create("sans-serif",Typeface.BOLD));
            label.setIncludeFontPadding(true);
            label.setLineSpacing(dp(label.getContext(),2),1.02f);
        }
        if(!(root instanceof android.view.ViewGroup))return;
        android.view.ViewGroup group=(android.view.ViewGroup)root;
        if(root instanceof android.widget.LinearLayout
                && ((android.widget.LinearLayout)root).getOrientation()==android.widget.LinearLayout.VERTICAL){
            for(int i=1;i<group.getChildCount();i++){
                View previous=group.getChildAt(i-1),current=group.getChildAt(i);
                if("new_task_button".equals(current.getTag()))continue;
                boolean beforeInteractive=previous instanceof Button
                    ||previous instanceof android.widget.Spinner
                    ||previous instanceof android.widget.EditText
                    ||previous instanceof android.widget.CheckBox;
                boolean afterInteractive=current instanceof Button
                    ||current instanceof android.widget.Spinner
                    ||current instanceof android.widget.EditText
                    ||current instanceof android.widget.CheckBox;
                boolean afterText=current instanceof TextView;
                if(!(beforeInteractive&&(afterInteractive||afterText)
                    ||afterInteractive&&previous instanceof TextView))continue;
                android.view.ViewGroup.LayoutParams base=current.getLayoutParams();
                if(!(base instanceof android.widget.LinearLayout.LayoutParams))continue;
                android.widget.LinearLayout.LayoutParams params=(android.widget.LinearLayout.LayoutParams)base;
                int minGap=dp(root.getContext(),beforeInteractive?12:8);
                if(params.topMargin<minGap){
                    params.topMargin=minGap;
                    current.setLayoutParams(params);
                }
            }
        }
        if(root instanceof android.widget.LinearLayout
                && ((android.widget.LinearLayout)root).getOrientation()==android.widget.LinearLayout.HORIZONTAL){
            for(int i=0;i<group.getChildCount();i++){
                View child=group.getChildAt(i);
                if(!(child instanceof Button)||"new_task_button".equals(child.getTag()))continue;
                boolean left=i>0&&group.getChildAt(i-1) instanceof Button;
                boolean right=i+1<group.getChildCount()&&group.getChildAt(i+1) instanceof Button;
                if(!left&&!right)continue;
                android.view.ViewGroup.LayoutParams base=child.getLayoutParams();
                if(!(base instanceof android.widget.LinearLayout.LayoutParams))continue;
                android.widget.LinearLayout.LayoutParams params=(android.widget.LinearLayout.LayoutParams)base;
                int gutter=dp(root.getContext(),4);
                boolean changed=false;
                if(left&&params.leftMargin<gutter){params.leftMargin=gutter;changed=true;}
                if(right&&params.rightMargin<gutter){params.rightMargin=gutter;changed=true;}
                if(changed)child.setLayoutParams(params);
            }
        }
        for(int i=0;i<group.getChildCount();i++)polishTree(group.getChildAt(i));
    }
'''
    ui=once(ui,anchor,methods+anchor,"bold and spacing renderer")

    # Do not rely on a single page's manual padding; all body views and
    # all modal views receive the same layout pass after they are built.
    main=once(main,
       '        lastRefresh=SystemClock.uptimeMillis();lastDataSignature=dataSignature();',
       '        UiDesign.polishTree(body);UiDesign.polishTree(nav);\n'
       '        lastRefresh=SystemClock.uptimeMillis();lastDataSignature=dataSignature();',
       "all main page layout pass")
    main=once(main,
       'body.setPadding(dp(18),dp(12),dp(18),dp(32));',
       'body.setPadding(dp(22),dp(18),dp(22),dp(40));',
       "outer content safe spacing")
    main=once(main,
       'c.setPadding(dp(18),dp(18),dp(18),dp(18));UiDesign.card(c);',
       'c.setPadding(dp(20),dp(20),dp(20),dp(20));UiDesign.card(c);',
       "card inner spacing")
    main=once(main,
       'lp.bottomMargin=dp(16);parent.addView(c,lp);return c;',
       'lp.bottomMargin=dp(20);parent.addView(c,lp);return c;',
       "card outer spacing")
    main=once(main,
       'contentScroll.setFillViewport(true);contentScroll.setClipToPadding(false);',
       'contentScroll.setFillViewport(true);contentScroll.setClipToPadding(true);'
       'contentScroll.setVerticalFadingEdgeEnabled(true);contentScroll.setFadingEdgeLength(dp(18));',
       "visually intentional screen scrolling")
    main=once(main,
       'tabs.addView(b,new LinearLayout.LayoutParams(0,dp(50),1));',
       'tabs.addView(b,new LinearLayout.LayoutParams(0,dp(64),1));',
       "connections tab labels fit when bold")

    # Dialogs must start at the beginning of their content, rather than
    # focusing an EditText and placing its label behind the dialog title.
    main=once(main,
       'ScrollView scroll=new WindowLayout.DialogScroll(this);scroll.addView(box);',
       'ScrollView scroll=new WindowLayout.DialogScroll(this);'
       'scroll.setFocusableInTouchMode(true);'
       'scroll.setDescendantFocusability(ViewGroup.FOCUS_BEFORE_DESCENDANTS);'
       'scroll.addView(box);',
       "new-task dialog scroll focus")
    main=once(main,
       '        });editor.show();editor.getWindow().setSoftInputMode(',
       '        });editor.show();'
       'scroll.requestFocus();scroll.post(()->scroll.scrollTo(0,0));'
       'editor.getWindow().setSoftInputMode(',
       "open task editor at top")
    # The bottom part of the form should be reachable even with large type.
    main=once(main,
       'box.setPadding(dp(18),dp(12),dp(18),dp(24));ScrollView scroll=',
       'box.setPadding(dp(20),dp(16),dp(20),dp(32));ScrollView scroll=',
       "task form inner insets")
    main=once(main,
       'void trackDialog(AlertDialog d){dialogs.add(d);d.getWindow().getDecorView().addOnAttachStateChangeListener(new View.OnAttachStateChangeListener(){public void onViewAttachedToWindow(View v){WindowLayout.boundDialog(MainActivity.this,d);}',
       'void trackDialog(AlertDialog d){dialogs.add(d);d.getWindow().getDecorView().addOnAttachStateChangeListener(new View.OnAttachStateChangeListener(){public void onViewAttachedToWindow(View v){WindowLayout.boundDialog(MainActivity.this,d);v.post(()->UiDesign.polishTree(v));}',
       "all main dialogs polished")
    # Wrap arbitrary custom dialog content in a measured ScrollView.
    main=once(main,
       'AlertDialog.Builder dialogBuilder(){return new AlertDialog.Builder(this,R.style.DialogTheme){@Override public AlertDialog create(){AlertDialog d=super.create();trackDialog(d);return d;}};}',
       '''AlertDialog.Builder dialogBuilder(){return new AlertDialog.Builder(this,R.style.DialogTheme){
            @Override public AlertDialog.Builder setView(View view){
                if(view instanceof ScrollView)return super.setView(view);
                if(view.getParent()!=null)return super.setView(view);
                WindowLayout.DialogScroll wrapper=new WindowLayout.DialogScroll(MainActivity.this);
                wrapper.addView(view);return super.setView(wrapper);
            }
            @Override public AlertDialog create(){AlertDialog d=super.create();trackDialog(d);return d;}
        };}''',
       "all modal panels scroll instead of clipping")
    # Style the normally unbold navigation items on every render.
    main=once(main,
       'label.setTypeface(Typeface.DEFAULT,page==n?Typeface.BOLD:Typeface.NORMAL);',
       'UiDesign.text(label,true);',
       "navigation label weights")

    # Schedule uses the same main interface primitives and dialog scrolling.
    classes=once(classes,
       'private LinearLayout card(){LinearLayout c=col();c.setPadding(dp(16),dp(16),dp(16),dp(16));UiDesign.card(c);LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(-1,-2);params.bottomMargin=dp(16);body.addView(c,params);return c;}',
       'private LinearLayout card(){LinearLayout c=col();c.setPadding(dp(20),dp(20),dp(20),dp(20));UiDesign.card(c);LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(-1,-2);params.bottomMargin=dp(20);body.addView(c,params);return c;}',
       "schedule cards")
    classes=once(classes,
       'private AlertDialog.Builder scheduleDialog(){\n        return new AlertDialog.Builder(this,R.style.DialogTheme){',
       '''private AlertDialog.Builder scheduleDialog(){
        return new AlertDialog.Builder(this,R.style.DialogTheme){
            @Override public AlertDialog.Builder setView(View view){
                if(view instanceof ScrollView)return super.setView(view);
                if(view.getParent()!=null)return super.setView(view);
                WindowLayout.DialogScroll wrapper=new WindowLayout.DialogScroll(ScheduleActivity.this);
                wrapper.addView(view);return super.setView(wrapper);
            }''',
       "schedule dialog custom views scroll")
    classes=once(classes,
       'public void onViewAttachedToWindow(View v){WindowLayout.boundDialog(ScheduleActivity.this,dialog);}',
       'public void onViewAttachedToWindow(View v){WindowLayout.boundDialog(ScheduleActivity.this,dialog);v.post(()->UiDesign.polishTree(v));}',
       "schedule dialog font and spacing")
    classes=once(classes,
       'scroll.setFillViewport(false);scroll.setClipToPadding(false);',
       'scroll.setFillViewport(false);scroll.setClipToPadding(true);'
       'scroll.setVerticalFadingEdgeEnabled(true);scroll.setFadingEdgeLength(dp(18));',
       "schedule scroll clipping")
    classes=once(classes,
       'private void space(LinearLayout parent,int height){View s=new View(this);parent.addView(s,new LinearLayout.LayoutParams(1,dp(height)));}',
       'private void space(LinearLayout parent,int height){View s=new View(this);parent.addView(s,new LinearLayout.LayoutParams(1,dp(Math.max(8,height))));}',
       "minimum spacing around academic components")
    # Schedule screen always draws a single new root via show(screen). Polish
    # once after rendering its contents using a layout-pass callback.
    classes=once(classes,
       '        setContentView(root);applyScheduleInsets(root);',
       '        setContentView(root);applyScheduleInsets(root);'
       'root.post(()->UiDesign.polishTree(root));',
       "polish academic screen")

    # Window bounds must account for both the status/navigation bars and
    # the keyboard. Leave space for AlertDialog title/action buttons.
    window=once(window,
       'w.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE|WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);w.setDimAmount(.32f);',
       'w.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE|WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);w.setDimAmount(.32f);'
       'w.addFlags(WindowManager.LayoutParams.FLAG_DIM_BEHIND);',
       "dialog keyboard handling")
    window=once(window,
       'static final class DialogScroll extends ScrollView{\n        final Activity a;DialogScroll(Activity a){super(a);this.a=a;setClipToPadding(false);}',
       '''static final class DialogScroll extends ScrollView{
        final Activity a;DialogScroll(Activity a){
            super(a);this.a=a;setClipToPadding(true);setFillViewport(false);
            setFocusableInTouchMode(true);
            setDescendantFocusability(FOCUS_BEFORE_DESCENDANTS);
            setPadding(dp(a,4),dp(a,10),dp(a,4),dp(a,16));
        }''',
       "scrollable dialog with safe top and bottom insets")
    window=once(window,
       'int max=Math.max(dp(a,96),available(a,a.getWindow().getDecorView()).height()-dp(a,180));',
       'int max=Math.max(dp(a,96),available(a,a.getWindow().getDecorView()).height()-dp(a,196));',
       "space for modal title/action bar")

    photo=once(photo,
       '        File f=new File(getFilesDir(),PhotoWidget.filename(id));',
       '        body.post(()->UiDesign.polishTree(body));'+chr(10)+'        File f=new File(getFilesDir(),PhotoWidget.filename(id));',
       "all photo widget controls are bold and spaced")

    if next((line for line in main.splitlines() if 'setTag("new_task_button")' in line),None)!=plus:
        raise RuntimeError("Approved header + button changed")
    ui_file.write_text(ui,encoding="utf-8")
    main_file.write_text(main,encoding="utf-8")
    class_file.write_text(classes,encoding="utf-8")
    window_file.write_text(window,encoding="utf-8")
    photo_file.write_text(photo,encoding="utf-8")
    print("PASS phase25: global bold, non-touching controls, safe scrolling dialogs, all page layout pass; + preserved")

if __name__=="__main__":
    apply()
