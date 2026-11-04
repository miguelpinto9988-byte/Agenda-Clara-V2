#!/usr/bin/env python3
"""Phase 8: final responsive polish without changing existing persistence/services.

No Gradle invocation. Applied after phase54; leaves the user-visible APK
build disabled until the user approves the final static preview.
"""
from pathlib import Path

CODE = Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
MAIN = CODE / 'MainActivity.java'
OLD = '        body.removeAllViews();if(page==0){if(homeSection==1)tasksPage();else if(homeSection==2)MiDiaStudyPage.render(this);else MiDiaDashboard.render(this);}else if(page==1)calendarPage();else if(page==2)messagesPage();else if(page==4)MiDiaMorePage.render(this);else settingsPage();if(!samePage)UiMotion.reveal(body);'
NEW = '''        body.removeAllViews();
        boolean isHome=page==0&&homeSection==0;
        // More visual space for the designed home; every legacy page retains
        // its existing padding, query UI, scroll and keyboard behavior.
        body.setPadding(isHome?dp(12):dp(22),isHome?dp(6):dp(18),
                isHome?dp(12):dp(22),isHome?dp(18):dp(40));
        contentScroll.setBackgroundColor(isHome?0xffffffff:BG);
        contentScroll.setVerticalScrollBarEnabled(!isHome);
        if(page==0){
            if(homeSection==1){
                // The original toolbar is hidden on all home subsections.
                // Retain an obvious creation affordance in the task tab.
                LinearLayout taskHeading=row();
                taskHeading.addView(text("Mis tareas",22,INK,true),
                        new LinearLayout.LayoutParams(0,-2,1));
                Button newTask=button("＋ Nueva",()->showCreationMenu());
                newTask.setContentDescription("Crear una tarea o nota");
                taskHeading.addView(newTask);
                body.addView(taskHeading);gap(body,13);
                tasksPage();
            }else if(homeSection==2)MiDiaStudyPage.render(this);
            else MiDiaDashboard.render(this);
        }else if(page==1)calendarPage();
        else if(page==2)messagesPage();
        else if(page==4)MiDiaMorePage.render(this);
        else settingsPage();
        if(!samePage)UiMotion.reveal(body);'''


def install():
    if not MAIN.is_file():
        raise RuntimeError('Reconstruct Android sources and apply phase54 first')
    content = MAIN.read_text(encoding='utf-8')
    if NEW not in content:
        if content.count(OLD) != 1:
            raise RuntimeError('Wrong version or conflicting MainActivity; not modifying')
        content = content.replace(OLD, NEW, 1)
    # Fail closed: do not leave a partial render.
    for required in ('MiDiaNavigation.selectedTab(this)', 'MiDiaStudyPage.render(this)',
                     'MiDiaMorePage.render(this)', 'body.setPadding(isHome?',
                     'newTask.setContentDescription("Crear una tarea o nota")'):
        if required not in content:
            raise RuntimeError('Missing final polish requirement: ' + required)
    MAIN.write_text(content, encoding='utf-8')
    print('PASS phase8 visual polish: responsive home, task creation access, unchanged legacy pages')


if __name__ == '__main__':
    install()
