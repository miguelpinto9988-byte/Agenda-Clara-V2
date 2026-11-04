#!/usr/bin/env python3
"""Phase 7: five visible tabs on top of existing four internal routes.

The WhatsApp, Review, Calendar, Notes and SQLite implementations are not
removed. Original pages 2/3 are opened through the More hub or home shortcuts.
"""
from pathlib import Path
import shutil

BASE = Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
HERE = Path(__file__).resolve().parent


def exactly(src, old, new, label):
    if src.count(old) != 1:
        raise RuntimeError(f'{label}: expected one match, found {src.count(old)}')
    return src.replace(old, new, 1)


def install():
    main_path = BASE / 'MainActivity.java'
    ui_path = BASE / 'UiDesign.java'
    if not main_path.is_file() or not ui_path.is_file():
        raise RuntimeError('Apply earlier phases to reconstructed Android sources first')
    for name in ('MiDiaNavigation.java', 'MiDiaStudyPage.java', 'MiDiaMorePage.java'):
        source = (HERE / name).read_text(encoding='utf-8')
        if 'package pe.agendaclara.app;' not in source:
            raise RuntimeError(f'Unexpected Java package in {name}')
        target = BASE / name
        if target.exists() and target.read_text(encoding='utf-8') != source:
            raise RuntimeError(f'Conflicting staged navigation file: {name}')

    main = main_path.read_text(encoding='utf-8')
    ui = ui_path.read_text(encoding='utf-8')
    marker = 'MiDiaNavigation.selectedTab(this)'
    if marker not in main:
        main = exactly(main,
            'String pendingHistoryChat="";boolean dashboardAllTasksExpanded=false;ScrollView contentScroll;int renderedPage=-1,',
            'String pendingHistoryChat="";boolean dashboardAllTasksExpanded=false;int homeSection=0,renderedHomeSection=-1;ScrollView contentScroll;int renderedPage=-1,',
            'navigation state')
        main = exactly(main,
            'if(state!=null){dashboardAllTasksExpanded=state.getBoolean("mi_dia_all_tasks",false);',
            'if(state!=null){homeSection=Math.max(0,Math.min(2,state.getInt("mi_dia_home_section",0)));dashboardAllTasksExpanded=state.getBoolean("mi_dia_all_tasks",false);',
            'restore home subsection')
        main = exactly(main,
            'page=Math.max(0,Math.min(3,state.getInt("page")));',
            'page=Math.max(0,Math.min(4,state.getInt("page")));',
            'restore More page')
        main = exactly(main,
            'out.putBoolean("mi_dia_all_tasks",dashboardAllTasksExpanded);',
            'out.putInt("mi_dia_home_section",homeSection);out.putBoolean("mi_dia_all_tasks",dashboardAllTasksExpanded);',
            'save home subsection')
        main = exactly(main,
            'boolean samePage=renderedPage==page&&contentScroll!=null;',
            'boolean samePage=renderedPage==page&&(page!=0||renderedHomeSection==homeSection)&&contentScroll!=null;',
            'scroll continuity')
        main = exactly(main,
            'final ScrollAnchor anchor=samePage?scrollAnchor(body):null;renderedPage=page;',
            'final ScrollAnchor anchor=samePage?scrollAnchor(body):null;renderedPage=page;renderedHomeSection=homeSection;',
            'last home subsection')
        main = exactly(main,
            'new String[]{"Inicio — Mi día","Calendario","Revisión","Conexiones"}[page]',
            'new String[]{"Inicio — Mi día","Calendario","Revisión","Conexiones","Más"}[page]',
            'toolbar labels')
        main = exactly(main,
            'body.removeAllViews();if(page==0)MiDiaDashboard.render(this);else if(page==1)calendarPage();else if(page==2)messagesPage();else settingsPage();if(!samePage)UiMotion.reveal(body);',
            'body.removeAllViews();if(page==0){if(homeSection==1)tasksPage();else if(homeSection==2)MiDiaStudyPage.render(this);else MiDiaDashboard.render(this);}else if(page==1)calendarPage();else if(page==2)messagesPage();else if(page==4)MiDiaMorePage.render(this);else settingsPage();if(!samePage)UiMotion.reveal(body);',
            'page renderer')

        old_nav_update = '        for(int n=0;n<nav.getChildCount();n++){'
        end_nav_update = '        contentScroll.getViewTreeObserver().addOnPreDrawListener('
        start = main.index(old_nav_update)
        end = main.index(end_nav_update, start)
        updated = '''        int selectedNav=MiDiaNavigation.selectedTab(this);
        for(int n=0;n<nav.getChildCount();n++){
            LinearLayout item=(LinearLayout)nav.getChildAt(n);
            boolean active=selectedNav==n;
            String navLabel=MiDiaNavigation.TAB_LABELS[n];
            item.setBackground(rounded(active?0xffe6f2ff:0xffffffff,15));
            item.setSelected(active);
            item.setContentDescription(navLabel+(active?", pestaña actual":", abrir pestaña"));
            ImageView tabIcon=(ImageView)item.getChildAt(0);
            int tabColor=active?0xff1468d0:MUTED;
            if(!(tabIcon.getTag() instanceof Integer)||((Integer)tabIcon.getTag())!=tabColor){
                tabIcon.setImageTintList(null);
                tabIcon.setImageDrawable(new UiDesign.OutlineIcon(UiDesign.statusIcon(navLabel),tabColor));
                tabIcon.setTag(tabColor);
            }
            TextView navText=(TextView)item.getChildAt(1);
            navText.setTextColor(active?0xff1468d0:MUTED);
            UiDesign.text(navText,active);
        }
'''
        main = main[:start] + updated + main[end:]

        old_shell = '        nav=row();'
        shell_end = '        View line=new View(this);'
        start = main.index(old_shell)
        end = main.index(shell_end, start)
        revised_shell = '''        nav=row();nav.setPadding(dp(5),dp(7),dp(5),dp(9));
        nav.setBackgroundColor(0xffffffff);
        String[] labels=MiDiaNavigation.TAB_LABELS;
        for(int n=0;n<labels.length;n++){
            final int index=n;
            LinearLayout item=column();item.setGravity(Gravity.CENTER);
            item.setPadding(dp(1),dp(5),dp(1),dp(5));
            ImageView icon=new ImageView(this);
            icon.setImageDrawable(new UiDesign.OutlineIcon(UiDesign.statusIcon(labels[n]),MUTED));
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            icon.setPadding(dp(1),dp(1),dp(1),dp(1));
            item.addView(icon,new LinearLayout.LayoutParams(dp(24),dp(24)));
            TextView caption=text(labels[n],10,MUTED,false);
            caption.setGravity(Gravity.CENTER);caption.setSingleLine(true);
            item.addView(caption);
            item.setContentDescription(labels[n]+", abrir pestaña");
            item.setFocusable(true);item.setOnClickListener(v->MiDiaNavigation.open(this,index));
            nav.addView(item,new LinearLayout.LayoutParams(0,dp(67),1));
        }
        UiDesign.polishTree(nav);
'''
        main = main[:start] + revised_shell + main[end:]

        main = exactly(main,
            'page=0;dashboardAllTasksExpanded=true;selectedCategory="Notas";render();',
            'page=0;homeSection=1;dashboardAllTasksExpanded=true;selectedCategory="Notas";render();',
            'notes deep link')
        main = exactly(main,
            'page=0;dashboardAllTasksExpanded=true;selectedCategory=note.category;render();',
            'page=0;homeSection=1;dashboardAllTasksExpanded=true;selectedCategory=note.category;render();',
            'note widget deep link')
    if 'case "Estudio":return "graduation";' not in ui:
        ui = exactly(ui,
            'case "Inicio":case "Agenda":return "check";',
            'case "Inicio":return "home";\n            case "Tareas":case "Agenda":return "check";\n            case "Estudio":return "graduation";\n            case "Más":return "grid";',
            'new nav icons')
        ui = exactly(ui,
            '            switch(name){\n                case "check":',
            '''            switch(name){
                case "home":
                    Path house=new Path();house.moveTo(3,11);house.lineTo(12,3);
                    house.lineTo(21,11);canvas.drawPath(house,paint);
                    canvas.drawRoundRect(6,11,18,21,1,1,paint);
                    line(canvas,11,21,11,15);line(canvas,11,15,14,15);line(canvas,14,15,14,21);break;
                case "graduation":
                    Path cap=new Path();cap.moveTo(2,9);cap.lineTo(12,4);
                    cap.lineTo(22,9);cap.lineTo(12,14);cap.close();canvas.drawPath(cap,paint);
                    line(canvas,6,12,6,18);canvas.drawArc(6,15,18,21,0,180,false,paint);
                    line(canvas,21,10,21,17);break;
                case "grid":
                    canvas.drawRoundRect(3,3,10,10,1,1,paint);
                    canvas.drawRoundRect(14,3,21,10,1,1,paint);
                    canvas.drawRoundRect(3,14,10,21,1,1,paint);
                    canvas.drawRoundRect(14,14,21,21,1,1,paint);break;
                case "check":''',
            'draw icons')
    mandatory = ('MiDiaNavigation.selectedTab(this)', 'MiDiaStudyPage.render(this)',
                 'MiDiaMorePage.render(this)', 'homeSection=1', 'out.putInt("mi_dia_home_section"')
    if not all(term in main for term in mandatory):
        raise RuntimeError('Incomplete navigation integration')
    main_path.write_text(main, encoding='utf-8')
    ui_path.write_text(ui, encoding='utf-8')
    for name in ('MiDiaNavigation.java','MiDiaStudyPage.java','MiDiaMorePage.java'):
        shutil.copyfile(HERE / name, BASE / name)
    print('PASS phase7: five tabs; original review, WhatsApp, calendar, voice, notes and settings preserved')

if __name__ == '__main__':
    install()
