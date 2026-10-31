#!/usr/bin/env python3
"""3.9.3: six polished PNG sticky papers, date PNG in all notes and widget."""
from pathlib import Path
from generate_sticky_assets import generate

ROOT=Path("AgendaClara/app/src/main")
SRC=ROOT/"java/pe/agendaclara/app"
STAGE=Path(__file__).resolve().parent
GRADLE=Path("AgendaClara/app/build.gradle")

def one(text,old,new,label):
    count=text.count(old)
    if count!=1:raise RuntimeError("phase33 "+label+": expected 1 matching anchor, got "+str(count))
    return text.replace(old,new,1)

def apply():
    paths={
        "ui":SRC/"StickyNotesUi.java",
        "widget":SRC/"StickyNotesWidget.java",
        "row":ROOT/"res/layout/widget_sticky_row.xml",
        "gradle":GRADLE
    }
    old={name:path.read_text(encoding="utf-8") for name,path in paths.items()}
    ui=old["ui"]
    ui=one(ui,
        '''        TextView date=text(a,"▦  "+note.day.format(DateTimeFormatter.ofPattern("dd MMM yyyy",ES)),12,0xff344c68);
        date.setSingleLine(true);content.addView(date);''',
        '''        // Use the existing date PNG, not a Unicode grid that changes with device fonts.
        LinearLayout dateRow=a.row();
        dateRow.setGravity(Gravity.CENTER_VERTICAL);
        ImageView dateIcon=ApprovedPng.view(a,"date",20);
        LinearLayout.LayoutParams dateIconSpace=new LinearLayout.LayoutParams(dp(a,22),dp(a,22));
        dateIconSpace.rightMargin=dp(a,8);
        dateRow.addView(dateIcon,dateIconSpace);
        TextView date=text(a,note.day.format(DateTimeFormatter.ofPattern("dd MMM yyyy",ES)),12,0xff344c68);
        date.setSingleLine(true);
        dateRow.addView(date,new LinearLayout.LayoutParams(0,-2,1));
        content.addView(dateRow);''',
        "existing PNG calendar in agenda/calendar/editor preview")
    widget=one(old["widget"],
        'view.setTextViewText(R.id.sticky_widget_date,"▦  "+DATE.format(note.day));',
        'view.setTextViewText(R.id.sticky_widget_date,DATE.format(note.day));',
        "remove obsolete grid from widget date")
    xml=one(old["row"],
        '''        <TextView android:id="@+id/sticky_widget_date"
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:singleLine="true" android:ellipsize="end" android:textSize="12sp"
            android:textStyle="bold" android:textColor="#38516E"
            android:contentDescription="Fecha de la nota"/>''',
        '''        <!-- Same approved PNG calendar as the editable notes and date picker. -->
        <LinearLayout android:layout_width="match_parent"
            android:layout_height="wrap_content" android:orientation="horizontal"
            android:gravity="center_vertical">
            <ImageView android:id="@+id/sticky_widget_calendar_icon"
                android:layout_width="18dp" android:layout_height="18dp"
                android:layout_marginEnd="8dp" android:src="@drawable/ic_ref_date"
                android:contentDescription="@null"/>
            <TextView android:id="@+id/sticky_widget_date"
                android:layout_width="0dp" android:layout_height="wrap_content"
                android:layout_weight="1" android:singleLine="true"
                android:ellipsize="end" android:textSize="12sp"
                android:textStyle="bold" android:textColor="#38516E"
                android:contentDescription="Fecha de la nota"/>
        </LinearLayout>''',
        "widget date row with PNG calendar and comfortable spacing")
    gradle=one(old["gradle"],"versionCode 33","versionCode 34","new version code")
    gradle=one(gradle,"versionName '3.9.2'","versionName '3.9.3'","new version name")
    # No changes to bottom navigation, task data, calendar picker, or note schema.
    for name,value in (("ui",ui),("widget",widget),("row",xml),("gradle",gradle)):
        paths[name].write_text(value,encoding="utf-8")
    drawable=ROOT/"res/drawable-nodpi"
    if not (drawable/"ic_ref_date.png").is_file():
        raise RuntimeError("Approved calendar PNG missing: ic_ref_date.png")
    generate(drawable)
    print("PASS phase33: glossy pin PNGs for six note colors; PNG calendar in agenda/editor/widget; bold editable text; 3.9.3")

if __name__=="__main__":apply()
