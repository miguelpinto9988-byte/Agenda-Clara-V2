#!/usr/bin/env python3
"""Update only the schedule editor hours/days; preserve color UI and data schema."""
from pathlib import Path

SRC=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
STAGE=Path(__file__).resolve().parent
GRADLE=Path('AgendaClara/app/build.gradle')

def one(src, old, new, label):
    count=src.count(old)
    if count!=1:
        raise RuntimeError('phase37 '+label+': expected one anchor, found '+str(count))
    return src.replace(old,new,1)

def apply():
    source=(SRC/'ScheduleActivity.java').read_text(encoding='utf-8')
    before=source
    old_start='        space(form,6);form.addView(txt("El mismo curso conservará este color en todos sus días.",12,MUTED,false));'
    old_end='        EditText room=field("Lugar / aula",current.room,form,false)'
    start=source.index(old_start)
    end=source.index(old_end,start)
    replacement=r'''        space(form,6);form.addView(txt("El mismo curso conservará este color en todos sus días.",12,MUTED,false));
        space(form,12);
        form.addView(txt("Días y horarios",16,INK,true));space(form,7);
        form.addView(txt("Cada día de este curso puede tener una hora distinta. Selecciona AM o PM en el inicio y el fin.",12,MUTED,true));
        space(form,9);
        final TreeMap<Integer,ScheduleDayClock.Slot> sessions=new TreeMap<>();
        final TreeMap<Integer,ScheduleDayClock.Slot> initial=new TreeMap<>();
        // Load ALL sessions of the chosen saved course, not merely this one day.
        // For a course with two blocks on a single day, only the clicked block is
        // editable here; the other record is never overwritten or deleted.
        if(current.id>0){
            for(ScheduleEntry existing:ScheduleDatabase.get(this).all()){
                if(ScheduleCourseColors.same(current.course,existing.course)){
                    ScheduleDayClock.Slot slot=new ScheduleDayClock.Slot(existing.day,existing.start,existing.end,existing.id);
                    if(!sessions.containsKey(existing.day)||existing.id==current.id)sessions.put(existing.day,slot);
                }
            }
        }
        sessions.put(current.day,new ScheduleDayClock.Slot(current.day,current.start,current.end,current.id));
        for(ScheduleDayClock.Slot slot:sessions.values())
            initial.put(slot.day,new ScheduleDayClock.Slot(slot.day,slot.start,slot.end,slot.id));
        LinearLayout dayRow=row(), dayCards=col();
        final Runnable[] redraw=new Runnable[1];
        redraw[0]=()->{
            dayRow.removeAllViews();dayCards.removeAllViews();
            String[] shortDays={"Lu","Mar","Mi","Ju","Vi","Sá","Do"};
            for(int i=1;i<=7;i++){
                final int d=i;
                TextView button=txt(shortDays[i-1],11,sessions.containsKey(i)?0xffffffff:BLUE,true);
                button.setGravity(Gravity.CENTER);button.setSingleLine(true);
                button.setBackground(sessions.containsKey(i)?bg(BLUE,12):outline(PALE,12));
                button.setContentDescription(ScheduleEntry.dayName(i)+(sessions.containsKey(i)?", seleccionado":", agregar día"));
                LinearLayout.LayoutParams dayChip=new LinearLayout.LayoutParams(0,dp(44),1);
                dayChip.setMargins(dp(2),0,dp(2),0);
                dayRow.addView(button,dayChip);
                button.setOnClickListener(v->{
                    if(!sessions.containsKey(d)){
                        sessions.put(d,new ScheduleDayClock.Slot(d,current.start,current.end,0));
                        redraw[0].run();
                    }else{
                        Toast.makeText(this,"Edita las horas de "+ScheduleEntry.dayName(d)+" debajo",Toast.LENGTH_SHORT).show();
                    }
                });
            }
            for(ScheduleDayClock.Slot slot:sessions.values()){
                LinearLayout card=col();card.setPadding(dp(12),dp(10),dp(12),dp(11));
                card.setBackground(outline(0xfff1f5ff,15));
                LinearLayout head=row();
                TextView dayLabel=txt(ScheduleEntry.dayName(slot.day),15,INK,true);
                head.addView(dayLabel,new LinearLayout.LayoutParams(0,dp(44),1));
                ImageButton remove=new ImageButton(this);
                remove.setImageResource(android.R.drawable.ic_menu_delete);
                remove.setImageTintList(ColorStateList.valueOf(RED));
                remove.setBackground(bg(0xfffceaf0,11));
                remove.setContentDescription("Quitar "+ScheduleEntry.dayName(slot.day));
                head.addView(remove,new LinearLayout.LayoutParams(dp(44),dp(44)));
                remove.setOnClickListener(v->{
                    if(sessions.size()<=1){toast("Añade otro día antes de quitar este.");return;}
                    sessions.remove(slot.day);redraw[0].run();
                });
                card.addView(head);
                float scale=getResources().getConfiguration().fontScale;
                boolean sideBySide=getResources().getDisplayMetrics().widthPixels/
                     getResources().getDisplayMetrics().density>=460&&scale<=1.15f;
                LinearLayout clocks=sideBySide?row():col();
                LinearLayout begin=timeChoice(slot,true,redraw[0]);
                LinearLayout finish=timeChoice(slot,false,redraw[0]);
                if(sideBySide){
                    LinearLayout.LayoutParams first=new LinearLayout.LayoutParams(0,-2,1);
                    first.rightMargin=dp(6);clocks.addView(begin,first);
                    clocks.addView(finish,new LinearLayout.LayoutParams(0,-2,1));
                }else{
                    clocks.addView(begin,new LinearLayout.LayoutParams(-1,-2));
                    clocks.addView(finish,new LinearLayout.LayoutParams(-1,-2));
                }
                card.addView(clocks);
                LinearLayout.LayoutParams cardSpace=new LinearLayout.LayoutParams(-1,-2);
                cardSpace.bottomMargin=dp(10);
                dayCards.addView(card,cardSpace);
            }
        };
        form.addView(dayRow);space(form,9);
        form.addView(dayCards);
        Button addDay=btn("＋  Agregar otro día",()->{
            ArrayList<String> labels=new ArrayList<>();ArrayList<Integer> indices=new ArrayList<>();
            for(int day=1;day<=7;day++)if(!sessions.containsKey(day)){
                labels.add(ScheduleEntry.dayName(day));indices.add(day);
            }
            if(labels.isEmpty()){toast("Ya están seleccionados los siete días.");return;}
            scheduleDialog().setTitle("Agregar día al curso")
                .setItems(labels.toArray(new String[0]),(which,n)->{
                    int day=indices.get(n);sessions.put(day,new ScheduleDayClock.Slot(day,current.start,current.end,0));
                    redraw[0].run();
                }).setNegativeButton("Cancelar",null).show();
        },false);
        form.addView(addDay,new LinearLayout.LayoutParams(-1,dp(52)));
        redraw[0].run();space(form,10);
'''
    source=source[:start]+replacement+source[end:]
    save_start='        dialog.setOnShowListener(ignored->{dialog.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);dialog.getButton(-1).setOnClickListener(v->{'
    save_end='        });});dialog.show();'
    a=source.index(save_start)
    b=source.index(save_end,a)+len(save_end)
    saving=r'''        dialog.setOnShowListener(ignored->{dialog.getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);dialog.getButton(-1).setOnClickListener(v->{
            if(course.getText().toString().trim().length()<3){course.setError("Indica el nombre del curso");return;}
            if(sessions.isEmpty()){toast("Selecciona al menos un día.");return;}
            ArrayList<ScheduleEntry> additions=new ArrayList<>();
            for(ScheduleDayClock.Slot slot:sessions.values()){
                if(!ScheduleDayClock.validInterval(slot.start,slot.end)){
                    toast("Revisa inicio y fin de "+ScheduleEntry.dayName(slot.day)+". El fin debe ser posterior al inicio, máximo 12 horas.");
                    return;
                }
                ScheduleEntry s=current.copy();s.id=slot.id;s.day=slot.day;
                s.start=slot.start;s.end=slot.end;
                s.course=course.getText().toString().trim();
                s.room=room.getText().toString().trim();
                s.teacher=teacher.getText().toString().trim();
                s.notes=notes.getText().toString().trim();
                s.color=color[0];s.reminder=offsets[remind.getSelectedItemPosition()];
                if(!ScheduleEntry.valid(s)){toast("Revisa los campos de "+ScheduleEntry.dayName(slot.day));return;}
                additions.add(s);
            }
            if(importing){
                if(detected!=null){
                    int index=detected.candidates.indexOf(previous);
                    if(index<0)index=detected.candidates.indexOf(current);
                    boolean checked=index>=0&&index<chosen.size()?chosen.get(index):true;
                    if(index>=0){detected.candidates.remove(index);if(index<chosen.size())chosen.remove(index);}
                    else index=detected.candidates.size();
                    for(ScheduleEntry s:additions){
                        s.id=0;
                        boolean duplicate=false;
                        for(ScheduleEntry other:detected.candidates)
                            if(other.day==s.day&&other.start==s.start&&other.end==s.end&&
                               ScheduleCourseColors.same(other.course,s.course)){duplicate=true;break;}
                        if(!duplicate){
                            detected.candidates.add(Math.min(index,detected.candidates.size()),s);
                            chosen.add(Math.min(index,chosen.size()),checked);index++;
                        }
                    }
                    ScheduleCourseColors.align(detected.candidates,ScheduleDatabase.get(this).all());
                }else{
                    ScheduleEntry first=additions.get(0);
                    current.day=first.day;current.start=first.start;current.end=first.end;
                    current.course=first.course;current.room=first.room;
                    current.teacher=first.teacher;current.notes=first.notes;
                    current.color=first.color;current.reminder=first.reminder;
                }
                dialog.dismiss();if(onDone!=null)onDone.run();return;
            }
            HashSet<Long> removedIds=new HashSet<>();
            HashSet<Long> retainedIds=new HashSet<>();
            for(ScheduleEntry s:additions)if(s.id>0)retainedIds.add(s.id);
            for(ScheduleDayClock.Slot old:initial.values())
                if(old.id>0&&!retainedIds.contains(old.id))removedIds.add(old.id);
            ArrayList<ScheduleEntry> others=new ArrayList<>();
            for(ScheduleEntry old:ScheduleDatabase.get(this).all())
                if(!retainedIds.contains(old.id)&&!removedIds.contains(old.id))others.add(old);
            List<String> overlaps=ScheduleConflict.describe(additions,others);
            Runnable commit=()->{
                ScheduleDatabase db=ScheduleDatabase.get(this);
                for(long id:removedIds){ScheduleReminders.cancel(this,id);db.delete(id);}
                for(ScheduleEntry s:additions){
                    if(db.save(s))ScheduleReminders.schedule(this,s);
                    db.recolorSameCourse(s.course,s.color);
                }
                dialog.dismiss();notificationPermission();toast("Horarios del curso guardados");
                if(onDone!=null)onDone.run();else show(2);
            };
            Runnable confirmDeletions=()->{
                if(removedIds.isEmpty()){commit.run();return;}
                scheduleDialog().setTitle("Quitar días del curso")
                    .setMessage("Se eliminarán "+removedIds.size()+" sesión(es) semanal(es) y sus avisos. ¿Continuar?")
                    .setNegativeButton("Volver",null)
                    .setPositiveButton("Confirmar",(x,y)->commit.run()).show();
            };
            if(overlaps.isEmpty())confirmDeletions.run();
            else scheduleDialog().setTitle("Las clases se superponen")
                .setMessage(android.text.TextUtils.join("\n",overlaps.subList(0,Math.min(6,overlaps.size())))+
                            "\n\n¿Guardar de todas formas?")
                .setNegativeButton("Revisar",null)
                .setPositiveButton("Guardar igualmente",(x,y)->confirmDeletions.run()).show();
        });});dialog.show();'''
    source=source[:a]+saving+source[b:]
    # Add the 12h picker controls without disturbing the existing theme or color picker.
    anchor='    private void colorCatalog(int[] color,boolean[] manuallyColored,View preview){'
    helper=r'''    /** One start/end field has its own time and independent AM/PM controls. */
    private LinearLayout timeChoice(ScheduleDayClock.Slot slot,boolean beginning,Runnable repaint){
        LinearLayout outer=col();
        outer.addView(txt(beginning?"Inicio":"Fin",12,INK,true));
        LinearLayout bar=row();bar.setPadding(dp(8),dp(4),dp(6),dp(4));
        bar.setBackground(outline(0xffffffff,12));
        int clock=beginning?slot.start:slot.end;
        TextView time=txt(ScheduleDayClock.clock12(clock),15,INK,true);
        time.setSingleLine(true);time.setGravity(Gravity.CENTER_VERTICAL);
        time.setContentDescription((beginning?"Hora de inicio de ":"Hora de fin de ")+
           ScheduleEntry.dayName(slot.day)+": "+ScheduleDayClock.display(clock)+". Tocar para cambiar");
        bar.addView(time,new LinearLayout.LayoutParams(0,dp(44),1));
        time.setOnClickListener(v->{
            int initial=beginning?slot.start:slot.end;
            new TimePickerDialog(this,(dialog,h,m)->{
                if(beginning)slot.start=h*60+m;else slot.end=h*60+m;
                repaint.run();
            },(initial%1440)/60,initial%60,false).show();
        });
        for(boolean pm:new boolean[]{false,true}){
            final boolean selected=ScheduleDayClock.isPm(clock)==pm;
            TextView toggle=txt(pm?"PM":"AM",11,selected?0xffffffff:BLUE,true);
            toggle.setSingleLine(true);toggle.setGravity(Gravity.CENTER);
            toggle.setBackground(selected?bg(BLUE,9):outline(PALE,9));
            toggle.setContentDescription((beginning?"Inicio":"Fin")+" "+ScheduleEntry.dayName(slot.day)+" "+(pm?"tarde/noche PM":"mañana AM"));
            LinearLayout.LayoutParams size=new LinearLayout.LayoutParams(dp(44),dp(44));
            size.leftMargin=dp(3);bar.addView(toggle,size);
            toggle.setOnClickListener(v->{
                int prev=beginning?slot.start:slot.end;
                int minutes=ScheduleDayClock.withMeridiem(prev,pm);
                if(beginning)slot.start=minutes;else slot.end=minutes;
                repaint.run();
            });
        }
        outer.addView(bar,new LinearLayout.LayoutParams(-1,-2));
        return outer;
    }
'''
    source=one(source,anchor,helper+anchor,'time choice helper')
    if 'private void pickClock(EditText destination)' not in source:
        raise RuntimeError('Legacy picker unexpectedly absent')
    # The old picker was no longer used; remove this obsolete editor-only helper.
    picker='''    private void pickClock(EditText destination){int minutes=ScheduleEntry.minutes(destination.getText().toString());if(minutes<0)minutes=480;
        new TimePickerDialog(this,(p,h,m)->destination.setText(String.format(Locale.ROOT,"%02d:%02d",h,m)),minutes/60,minutes%60,true).show();
    }
'''
    source=one(source,picker,'','remove legacy 24-hour picker')
    # Must be code-only change: screenshots' upper color controls and layout remain untouched.
    color_before=before[before.index('        form.addView(txt("Color del curso'):before.index(old_start)]
    color_after=source[source.index('        form.addView(txt("Color del curso'):source.index(old_start)]
    if color_before!=color_after:raise RuntimeError('Color controls unexpectedly modified')
    dest=SRC/'ScheduleDayClock.java'
    if dest.exists():raise RuntimeError('Day clock already exists')
    source_path=SRC/'ScheduleActivity.java'
    build=GRADLE.read_text(encoding='utf-8')
    build=one(build,'versionCode 37','versionCode 38','versionCode')
    build=one(build,"versionName '3.9.6'","versionName '3.9.7'",'versionName')
    source_path.write_text(source,encoding='utf-8')
    dest.write_bytes((STAGE/'ScheduleDayClock.java').read_bytes())
    GRADLE.write_text(build,encoding='utf-8')
    print('PASS phase37: per-day course times, AM/PM independent, color UI unchanged, 3.9.7')

if __name__=='__main__':apply()
