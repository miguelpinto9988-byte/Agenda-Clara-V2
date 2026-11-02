#!/usr/bin/env python3
"""3.11.0: install lightweight floating task widget flow on verified 3.10.9."""
from pathlib import Path
import runpy,hashlib
ROOT=Path("AgendaClara")
SRC=ROOT/"app/src/main/java/pe/agendaclara/app"
RES=ROOT/"app/src/main/res"
STAGE=Path(__file__).resolve().parent

def one(value,old,new,label):
    if value.count(old)!=1:
        raise RuntimeError(f"phase47 {label}: expected one anchor, got {value.count(old)}")
    return value.replace(old,new,1)

gradle=ROOT/"app/build.gradle"
version=gradle.read_text(encoding="utf-8")
assert version.count("versionCode 50")==1 and version.count("versionName '3.10.9'")==1
for rel in ("WidgetTaskActivity.java",):
    if (SRC/rel).exists():raise RuntimeError("Refusing to overwrite "+rel)
for name in ("widget_list_bg.xml",):
    if (RES/"drawable"/name).exists():raise RuntimeError("Refusing to overwrite "+name)

widget=SRC/"TaskWidget.java"
w=widget.read_text(encoding="utf-8")
w=one(w,'Intent add=new Intent(c,MainActivity.class).setAction("new_task")',
      'Intent add=new Intent(c,WidgetTaskActivity.class).setAction(WidgetTaskActivity.ACTION_CREATE)',
      "widget + opens a floating chooser")
w=one(w,'v.setTextViewText(R.id.widget_header,"Mis tareas · "+all.size());',
      'v.setTextViewText(R.id.widget_subtitle,"Mis tareas de hoy · "+todayCount(all));',
      "new high-contrast subtitle")
w=one(w,"    @Override public void onUpdate",
'''    private static int todayCount(List<Task> all){
        java.time.LocalDate today=java.time.LocalDate.now();int n=0;
        for(Task task:all)if(!task.done&&task.due>0
            &&java.time.Instant.ofEpochMilli(task.due)
                .atZone(java.time.ZoneId.systemDefault()).toLocalDate().equals(today))n++;
        return n;
    }
    @Override public void onUpdate''',"today counter")

voice=SRC/"VoiceQuickTask.java"
v=voice.read_text(encoding="utf-8")
v=one(v,"import android.app.AlertDialog;",
      "import android.app.AlertDialog;\nimport android.app.Activity;\nimport android.animation.ValueAnimator;\nimport android.graphics.drawable.GradientDrawable;",
      "voice animation imports")
for before,after in (
    ("public static void show(MainActivity activity)","public static void show(Activity activity)"),
    ("public static void permissionResult(MainActivity activity,","public static void permissionResult(Activity activity,"),
    ("public static void closeFor(MainActivity activity)","public static void closeFor(Activity activity)"),
    ("        final MainActivity activity;","        final Activity activity;"),
    ("        Session(MainActivity a){","        Session(Activity a){")
):
    v=one(v,before,after,"reuse offline voice from widget Activity")
v=one(v,"        Button finish;",'''        Button finish;
        final View[] visualWave=new View[9];
        ValueAnimator waveAnimator;
        float voiceActivity=.12f;''',"voice bar state")
v=one(v,'            icon(content,"voice_waveform",92);gap(content,8);',
'''            LinearLayout spectrum=new LinearLayout(activity);spectrum.setGravity(Gravity.CENTER);
            for(int i=0;i<visualWave.length;i++){
                View bar=new View(activity);
                GradientDrawable gradient=new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                    new int[]{0xff33d8ff,i%2==0?0xff2263fa:0xff9154fc});
                gradient.setCornerRadius(dp(8));bar.setBackground(gradient);
                LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(dp(7),dp(22));
                params.setMargins(dp(4),0,dp(4),0);spectrum.addView(bar,params);
                visualWave[i]=bar;
            }
            content.addView(spectrum,new LinearLayout.LayoutParams(-1,dp(65)));gap(content,5);''',"animated waveform")
v=one(v,'            capture.show();WindowLayout.boundDialog(activity,capture);',
'''            ApprovedPng.button(cancel,"widget_cancel",22);
            capture.show();WindowLayout.boundDialog(activity,capture);
            waveAnimator=ValueAnimator.ofFloat(0f,1f);waveAnimator.setDuration(780);
            waveAnimator.setRepeatCount(ValueAnimator.INFINITE);
            waveAnimator.setRepeatMode(ValueAnimator.REVERSE);
            waveAnimator.addUpdateListener(anim->{
                float phase=(float)anim.getAnimatedValue();
                for(int i=0;i<visualWave.length;i++){
                    View bar=visualWave[i];if(bar==null)continue;
                    float pattern=(float)(.5+.5*Math.sin(phase*6.28+i*.72));
                    float height=14f+(22f+voiceActivity*28f)*pattern;
                    bar.setScaleY(height/22f);bar.setAlpha(recording?.92f:.45f);
                }
                voiceActivity=Math.max(.12f,voiceActivity*.975f);
            });
            waveAnimator.start();''',"start listening animation")
v=one(v,'String current=jsonText(hypothesis,"partial");partial.setText(transcript.toString()+(current.isEmpty()?"":" "+current));}}',
'''String current=jsonText(hypothesis,"partial");partial.setText(transcript.toString()+(current.isEmpty()?"":" "+current));
            if(!current.isEmpty())voiceActivity=Math.min(1f,.45f+current.length()/35f);}}''',
      "wave reacts to partial speech recognition")
v=one(v,'view.setOnClickListener(v->{success.dismiss();success=null;activity.page=0;activity.render();close();});',
'''view.setOnClickListener(v->{
                success.dismiss();success=null;
                if(activity instanceof MainActivity){
                    ((MainActivity)activity).page=0;((MainActivity)activity).render();
                }else{
                    activity.startActivity(new android.content.Intent(activity,MainActivity.class).setAction("tasks"));
                }
                close();
            });''',"navigate to tasks after widget voice save")
v=one(v,'void close(){if(closed)return;closed=true;generation++;recording=false;releaseAudio();transcript.setLength(0);',
'''void close(){if(closed)return;closed=true;generation++;recording=false;
            if(waveAnimator!=null){waveAnimator.cancel();waveAnimator=null;}
            releaseAudio();transcript.setLength(0);''',"release voice animation and mic")
v=one(v,'            if(active==this)active=null;',
'''            if(active==this)active=null;
            if(activity instanceof WidgetTaskActivity)((WidgetTaskActivity)activity).voiceFinished();''',
      "finish widget Activity after voice window exits")

manifest=RES.parent/"AndroidManifest.xml"
m=manifest.read_text(encoding="utf-8")
m=one(m,'        <activity android:name=".PhotoConfigActivity"',
'''        <activity android:name=".WidgetTaskActivity" android:exported="false"
            android:excludeFromRecents="true" android:taskAffinity=""
            android:launchMode="singleTop" android:theme="@style/WidgetFloatingTheme"
            android:windowSoftInputMode="adjustResize|stateAlwaysHidden" />
        <activity android:name=".PhotoConfigActivity"''',"register private floating widget Activity")
styles=RES/"values/styles.xml"
s=styles.read_text(encoding="utf-8")
s=one(s,'    <style name="PhotoTapTheme"',
'''    <style name="WidgetFloatingTheme" parent="android:style/Theme.Material.Light.Dialog.Alert">
        <item name="android:windowBackground">@android:color/transparent</item>
        <item name="android:backgroundDimEnabled">true</item>
        <item name="android:windowIsFloating">true</item>
        <item name="android:windowSoftInputMode">adjustResize</item>
        <item name="android:windowMinWidthMajor">0dp</item>
        <item name="android:windowMinWidthMinor">0dp</item>
        <item name="android:colorAccent">#2666FF</item>
    </style>
    <style name="PhotoTapTheme"''',"dialog-like overlay theme")

# Write only after every anchor has been checked, minimizing partial application.
widget.write_text(w,encoding="utf-8")
voice.write_text(v,encoding="utf-8")
manifest.write_text(m,encoding="utf-8")
styles.write_text(s,encoding="utf-8")
(SRC/"WidgetTaskActivity.java").write_bytes((STAGE/"WidgetTaskActivity.java").read_bytes())
for name in ("widget_tasks.xml","widget_bg.xml","widget_list_bg.xml"):
    target=RES/("layout" if name=="widget_tasks.xml" else "drawable")/name
    target.write_bytes((STAGE/name).read_bytes())
gradle.write_text(version.replace("versionCode 50","versionCode 51")
    .replace("versionName '3.10.9'","versionName '3.11.0'"),encoding="utf-8")
runpy.run_path(str(STAGE/"generate_widget_icons.py"),run_name="__main__")
print("PASS 3.11.0: widget + chooser; floating voice and normal task editors; animated listening")
