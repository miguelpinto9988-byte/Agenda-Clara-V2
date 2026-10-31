#!/usr/bin/env python3
"""Replace the two text glyphs in Calendar with PNGs; never alter bottom tabs."""
from pathlib import Path
STAGE=Path(__file__).resolve().parent

MAIN=Path('AgendaClara/app/src/main/java/pe/agendaclara/app/MainActivity.java')
GRADLE=Path('AgendaClara/app/build.gradle')
ART=Path('AgendaClara/app/src/main/res/drawable-nodpi')

def one(src,old,new,label):
    matches=src.count(old)
    if matches!=1:raise RuntimeError(f'phase38 {label}: expected one anchor, found {matches}')
    return src.replace(old,new,1)

def apply():
    src=MAIN.read_text(encoding='utf-8')
    grad=GRADLE.read_text(encoding='utf-8')
    nav_start=src.index('        nav=row();')
    nav_end=src.index('        View line=new View(this);',nav_start)
    original_nav=src[nav_start:nav_end]
    src=one(src,
      '''        c.addView(grid);gap(c,10);c.addView(button("▣  Ir a hoy",()->{selectedDay=LocalDate.now();month=selectedDay.withDayOfMonth(1);render();}));''',
      '''        c.addView(grid);gap(c,10);
        Button todayButton=button("Ir a hoy",()->{
            selectedDay=LocalDate.now();month=selectedDay.withDayOfMonth(1);render();
        });
        ApprovedPng.button(todayButton,"today_jump",28);
        todayButton.setCompoundDrawablePadding(dp(12));
        todayButton.setGravity(Gravity.CENTER);
        todayButton.setPadding(dp(18),dp(8),dp(18),dp(8));
        todayButton.setMinHeight(dp(54));
        todayButton.setSingleLine(true);
        todayButton.setContentDescription("Ir a hoy, volver a la fecha actual");
        c.addView(todayButton);''',
      'today button text symbol -> PNG')
    src=one(src,
      '''        schedule.addView(text("▦  Horario de clases",17,INK,true));gap(schedule,6);''',
      '''        LinearLayout scheduleHeading=row();
        ImageView scheduleIcon=ApprovedPng.view(this,"class_schedule",32);
        scheduleIcon.setContentDescription(null);
        LinearLayout.LayoutParams scheduleIconSpace=new LinearLayout.LayoutParams(dp(36),dp(36));
        scheduleIconSpace.rightMargin=dp(12);
        scheduleHeading.addView(scheduleIcon,scheduleIconSpace);
        TextView scheduleTitle=text("Horario de clases",17,INK,true);
        scheduleTitle.setGravity(Gravity.CENTER_VERTICAL);
        scheduleHeading.addView(scheduleTitle,new LinearLayout.LayoutParams(0,-2,1));
        schedule.addView(scheduleHeading);gap(schedule,6);''',
      'schedule header text symbol -> PNG')
    updated_nav=src[src.index('        nav=row();'):src.index('        View line=new View(this);')]
    if original_nav!=updated_nav:raise RuntimeError('Bottom navigation unexpectedly changed')
    if 'button("▣  Ir a hoy"' in src or 'text("▦  Horario de clases"' in src:
        raise RuntimeError('Legacy text glyph still present in targets')
    grad=one(grad,'versionCode 38','versionCode 39','code')
    grad=one(grad,"versionName '3.9.7'","versionName '3.9.8'",'version')
    if (ART/'ic_ref_today_jump.png').exists() or (ART/'ic_ref_class_schedule.png').exists():
        raise RuntimeError('Refusing to overwrite an existing PNG icon')
    MAIN.write_text(src,encoding='utf-8')
    GRADLE.write_text(grad,encoding='utf-8')
    for filename in ('ic_ref_today_jump.png','ic_ref_class_schedule.png'):
        source=STAGE/'assets'/filename
        data=source.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise RuntimeError('Invalid image resource '+filename)
        target=ART/filename
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    print('PASS phase38: two transparent PNG icons; icon/text spacing; bottom navigation unchanged')

if __name__=='__main__':apply()
