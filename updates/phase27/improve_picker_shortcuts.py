#!/usr/bin/env python3
"""Add optional quick dates and times to the efficient branded native dialogs."""
from pathlib import Path
path=Path("AgendaClara/app/src/main/java/pe/agendaclara/app/ModernPickers.java")
s=path.read_text(encoding="utf-8")
def one(a,b,label):
    global s
    count=s.count(a)
    if count!=1:raise RuntimeError(f"phase27 quick {label}: expected one source match, got {count}")
    s=s.replace(a,b,1)

one('''        content.addView(selectedRow);
        final Runnable[] render={null};
        render[0]=()->{''',
'''        content.addView(selectedRow);gap(a,content,14);
        content.addView(label(a,"Fechas rápidas",14,INK));gap(a,content,8);
        final Runnable[] render={null};
        LinearLayout extra=row(a);
        int[] quickOffsets={1,7,30};
        String[] names={"En 1 día","En 1 semana","En 30 días"};
        for(int k=0;k<quickOffsets.length;k++){
            final int offset=quickOffsets[k];
            Button b=chip(a,names[k],false);
            LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,dp(a,49),1);
            params.setMargins(dp(a,3),0,dp(a,3),0);extra.addView(b,params);
            b.setOnClickListener(v->{
                chosen[0]=LocalDate.now().plusDays(offset);
                month[0]=YearMonth.from(chosen[0]);render[0].run();
            });
        }
        content.addView(extra);
        render[0]=()->{''',"date quick choices")

one('''        minutes.setOnValueChangedListener((picker,oldValue,newValue)->{
            minute[0]=newValue;
            big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));
        });
        clock.setOnClickListener''',
'''        minutes.setOnValueChangedListener((picker,oldValue,newValue)->{
            minute[0]=newValue;
            big.setText(String.format(ES,"%02d:%02d",hour[0],minute[0]));
        });
        content.addView(label(a,"Horas rápidas",14,INK));gap(a,content,7);
        int[] delta={0,30,60,180,360,720};
        String[] names={"Ahora","+30 min","+1 hora","+3 horas","+6 horas","+12 horas"};
        for(int rowIndex=0;rowIndex<2;rowIndex++){
            LinearLayout options=row(a);
            for(int colIndex=0;colIndex<3;colIndex++){
                final int minutesAfter=delta[rowIndex*3+colIndex];
                Button b=chip(a,names[rowIndex*3+colIndex],false);
                LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(0,dp(a,48),1);
                params.setMargins(dp(a,3),dp(a,2),dp(a,3),dp(a,2));
                options.addView(b,params);
                b.setOnClickListener(v->{
                    LocalTime value=LocalTime.now().plusMinutes(minutesAfter);
                    hour[0]=value.getHour()%12==0?12:value.getHour()%12;
                    minute[0]=value.getMinute();pm[0]=value.getHour()>=12;
                    hours.setValue(hour[0]);
                    minutes.setValue(minute[0]);
                    redraw[0].run();
                });
            }
            content.addView(options);
        }
        clock.setOnClickListener''',"time quick choices")

path.write_text(s,encoding="utf-8")
print("PASS phase27 quick date/time: Android-native responsive shortcuts with correct callbacks")
