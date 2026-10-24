from pathlib import Path
p=Path('AgendaClara/app/src/main/java/pe/agendaclara/app/MainActivity.java')
s=p.read_text()
assert 'void dynamicAddButton' not in s and 'View dynamicAddButton()' in s

def replace_method(name,next_name,content):
 global s
 start=s.index('    '+name)
 end=s.index('    '+next_name,start)
 s=s[:start]+content+'\n'+s[end:]

replace_method('void openQuickActions()', 'View communityMetric(', '''    void openQuickActions(){
        final String[] labels={"Nueva tarea","Nuevo evento","Nuevo recordatorio","Nueva nota","Importar desde archivo"};
        final String[] glyphs={"☑","▣","♧","▤","⇧"};
        final int[] accents={0xff2765f5,0xff237fd7,0xff8b4bda,0xff159b66,0xffd32e89};
        LinearLayout menu=column();menu.setPadding(dp(8),dp(10),dp(8),dp(8));
        final AlertDialog dialog=dialogBuilder().setView(menu).create();
        for(int i=0;i<labels.length;i++){
            final int index=i;
            LinearLayout line=row();line.setGravity(Gravity.CENTER_VERTICAL);
            TextView label=text(labels[i],14,INK,true);label.setGravity(Gravity.CENTER_VERTICAL);
            label.setPadding(dp(18),0,dp(14),0);label.setBackground(rounded(0xffffffff,28));
            line.addView(label,new LinearLayout.LayoutParams(0,dp(48),1));
            TextView circle=text(glyphs[i],24,accents[i],true);circle.setGravity(Gravity.CENTER);
            circle.setBackground(rounded(0xffeef3ff,30));
            line.addView(circle,new LinearLayout.LayoutParams(dp(49),dp(49)));
            line.setPadding(dp(0),dp(4),dp(4),dp(4));
            line.setOnClickListener(v->{dialog.dismiss();
                if(index==4){page=2;render();toast("Selecciona el archivo desde la opción de importación correspondiente.");}
                else {if(index==1){page=1;render();}openEditor(-1,null,null);}
            });
            menu.addView(line,new LinearLayout.LayoutParams(dp(278),dp(57)));
        }
        TextView close=text("×",27,0xffffffff,true);close.setGravity(Gravity.CENTER);
        close.setBackground(rounded(0xff2765f5,40));
        LinearLayout bottom=row();bottom.setGravity(Gravity.RIGHT);bottom.addView(close,new LinearLayout.LayoutParams(dp(48),dp(48)));
        menu.addView(bottom);close.setOnClickListener(v->dialog.dismiss());
        dialog.setOnShowListener(v->{android.view.Window w=dialog.getWindow();if(w!=null){
            w.setBackgroundDrawableResource(android.R.color.transparent);
            w.setGravity(Gravity.TOP|Gravity.RIGHT);
            w.setLayout(dp(306),-2);
            android.view.WindowManager.LayoutParams a=w.getAttributes();a.y=dp(75);a.x=dp(15);a.dimAmount=.60f;w.setAttributes(a);
            w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);
        }
        menu.setAlpha(0f);menu.setTranslationY(-dp(18));menu.animate().alpha(1f).translationY(0f).setDuration(240).start();});
        dialog.show();
    }
''')

replace_method('void showQuickDatePicker(', 'void openEditor(', '''    void showQuickDatePicker(LocalDate[] date,LocalTime[] time,boolean[] dateSet,boolean[] timeSet,Runnable onConfirm){
        final LocalDate[] chosen={date[0]};final LocalTime[] chosenTime={time[0]};
        final LocalDate[] shownMonth={chosen[0].withDayOfMonth(1)};
        LinearLayout panel=column();panel.setPadding(dp(13),dp(12),dp(13),dp(9));
        ScrollView scroll=new WindowLayout.DialogScroll(this);scroll.setFillViewport(false);scroll.addView(panel);
        panel.addView(text("Seleccionar fecha y hora",19,INK,true));gap(panel,9);
        LinearLayout presets=row();panel.addView(presets);
        LinearLayout monthBar=row();monthBar.setGravity(Gravity.CENTER_VERTICAL);panel.addView(monthBar);
        LinearLayout grid=column();panel.addView(grid);
        final Runnable[] redraw={null};
        String[] names={"Hoy","Mañana","Esta semana","Otra fecha"};
        for(int i=0;i<4;i++){final int n=i;Button b=button(names[i],()->{
            chosen[0]=n==0?LocalDate.now():n==1?LocalDate.now().plusDays(1):n==2?LocalDate.now().plusDays(7):chosen[0];
            shownMonth[0]=chosen[0].withDayOfMonth(1);redraw[0].run();
        });b.setTextSize(11);b.setPadding(0,0,0,0);b.setBackground(rounded(i==0?0xff2765f5:PALE,12));
            if(i==0)b.setTextColor(0xffffffff);presets.addView(b,new LinearLayout.LayoutParams(0,dp(43),1));}
        final java.time.format.DateTimeFormatter monthFmt=DateTimeFormatter.ofPattern("MMMM yyyy",new Locale("es","PE"));
        redraw[0]=()->{
            monthBar.removeAllViews();grid.removeAllViews();
            Button prev=button("‹",()->{shownMonth[0]=shownMonth[0].minusMonths(1);redraw[0].run();});
            monthBar.addView(prev,new LinearLayout.LayoutParams(dp(45),dp(45)));
            TextView title=text(shownMonth[0].format(monthFmt),16,INK,true);title.setGravity(Gravity.CENTER);
            monthBar.addView(title,new LinearLayout.LayoutParams(0,dp(45),1));
            Button next=button("›",()->{shownMonth[0]=shownMonth[0].plusMonths(1);redraw[0].run();});
            monthBar.addView(next,new LinearLayout.LayoutParams(dp(45),dp(45)));
            String[] week={"Lun","Mar","Mié","Jue","Vie","Sáb","Dom"};
            LinearLayout weekRow=row();grid.addView(weekRow);
            for(String day:week){TextView head=text(day,10,MUTED,true);head.setGravity(Gravity.CENTER);
                weekRow.addView(head,new LinearLayout.LayoutParams(0,dp(27),1));}
            int offset=shownMonth[0].getDayOfWeek().getValue()-1;
            int total=shownMonth[0].lengthOfMonth();
            for(int r=0;r<6;r++){
                LinearLayout cells=row();grid.addView(cells);
                for(int c=0;c<7;c++){
                    int day=r*7+c-offset;
                    if(day<1||day>total){View empty=new View(this);cells.addView(empty,new LinearLayout.LayoutParams(0,dp(40),1));continue;}
                    LocalDate candidate=shownMonth[0].withDayOfMonth(day);
                    TextView cell=text(""+day,12,candidate.equals(chosen[0])?0xffffffff:INK,false);
                    cell.setGravity(Gravity.CENTER);cell.setBackground(rounded(candidate.equals(chosen[0])?0xff2765f5:candidate.equals(LocalDate.now())?PALE:0xffffffff,12));
                    cell.setContentDescription("Seleccionar "+candidate.toString());
                    cell.setOnClickListener(v->{chosen[0]=candidate;redraw[0].run();});
                    cells.addView(cell,new LinearLayout.LayoutParams(0,dp(40),1));
                }
            }
        };redraw[0].run();gap(panel,7);
        panel.addView(text("Selecciona la hora",14,INK,true));gap(panel,5);
        LinearLayout timeGrid=column();panel.addView(timeGrid);
        final Runnable[] redrawHours={null};
        final int[] hours={8,9,10,12,14,16,18,20};
        redrawHours[0]=()->{timeGrid.removeAllViews();for(int i=0;i<hours.length;i+=4){
            LinearLayout line=row();timeGrid.addView(line);
            for(int j=i;j<i+4;j++){final int h=hours[j];
                boolean selected=chosenTime[0].getHour()==h&&chosenTime[0].getMinute()==0;
                Button slot=button(String.format(Locale.ROOT,"%02d:00",h),()->{chosenTime[0]=LocalTime.of(h,0);redrawHours[0].run();});
                slot.setTextSize(11);slot.setTextColor(selected?0xffffffff:GREEN);
                slot.setBackground(rounded(selected?0xff2765f5:PALE,12));
                line.addView(slot,new LinearLayout.LayoutParams(0,dp(42),1));
            }
        }};redrawHours[0].run();
        LinearLayout dayparts=row();panel.addView(dayparts);
        String[] dayNames={"☀ Mañana","☀ Tarde","☾ Noche"};int[] dayHours={8,14,20};
        for(int i=0;i<3;i++){final int h=dayHours[i];Button b=button(dayNames[i],()->{chosenTime[0]=LocalTime.of(h,0);redrawHours[0].run();});
            b.setTextSize(11);dayparts.addView(b,new LinearLayout.LayoutParams(0,dp(43),1));}
        Button custom=button("◷  Hora personalizada · "+chosenTime[0],()->{
            TimePickerDialog picker=new TimePickerDialog(this,(v,h,m)->{chosenTime[0]=LocalTime.of(h,m);redrawHours[0].run();},
                chosenTime[0].getHour(),chosenTime[0].getMinute(),true);picker.show();});panel.addView(custom);
        CheckBox allDay=new CheckBox(this);allDay.setText("Todo el día");allDay.setChecked(!timeSet[0]);panel.addView(allDay);
        final AlertDialog dialog=dialogBuilder().setView(scroll).setNegativeButton("Cancelar",null).setPositiveButton("Confirmar",null).create();
        dialog.setOnShowListener(v->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(b->{
            date[0]=chosen[0];time[0]=chosenTime[0];dateSet[0]=true;timeSet[0]=!allDay.isChecked();onConfirm.run();dialog.dismiss();}));
        dialog.show();
    }
''')
# Upgrade animated plus: extra glow rings, keep button accessible
s=s.replace('frame.addView(halo,haloLp);\n        Button plus=', '''frame.addView(halo,haloLp);
        View glow=new View(this);glow.setBackground(outlined(0xffd9e9ff,50,0xffb6d2ff));
        frame.addView(glow,new android.widget.FrameLayout.LayoutParams(dp(58),dp(58),Gravity.CENTER));
        glow.animate().alpha(.65f).scaleX(1.09f).scaleY(1.09f).setDuration(500).start();
        Button plus=''',1)
# Make community accordion motion smooth
s=s.replace('inner.setVisibility(expanded?View.VISIBLE:View.GONE);arrow.setText(expanded?"⌃":"›");', '''inner.setVisibility(expanded?View.VISIBLE:View.GONE);
                    if(expanded){inner.setAlpha(0f);inner.setTranslationY(-dp(10));inner.animate().alpha(1f).translationY(0f).setDuration(190).start();}
                    arrow.animate().rotation(expanded?180f:0f).setDuration(180).start();arrow.setText(expanded?"⌃":"›");''',1)
# enhance date summary button
s=s.replace('dateBtn.setBackground(outlined(PALE,16,0xffc8dafe));','dateBtn.setBackground(outlined(0xffffffff,18,0xffc8dafe));dateBtn.setMinHeight(dp(56));',1)
p.write_text(s)
print('PATCH 3.9 OK',len(s))