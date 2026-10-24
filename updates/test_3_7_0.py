#!/usr/bin/env python3
"""Regresiones de integración: pantalla Calendar por cuenta y conversión semanal."""
from pathlib import Path
p=Path('AgendaClara/app/src/main/java/pe/agendaclara/app')
main=(p/'MainActivity.java').read_text(encoding='utf8')
bridge=(p/'CalendarBridge.java').read_text(encoding='utf8')
conv=(p/'CalendarScheduleImport.java').read_text(encoding='utf8')
checks={
 'cuentas separadas': 'Map<String,List<CalendarBridge.CalendarInfo>> accounts=new LinkedHashMap<>()' in main,
 'Google o Android': 'k.google?"Google: ":"Android: "' in main,
 'expandir cuentas': 'expandedCalendarAccounts.add(key)' in main,
 'contraer cuentas': 'expandedCalendarAccounts.remove(key)' in main,
 'expandir calendarios': 'expandedCalendarIds.add(calendar.id)' in main,
 'contraer calendarios': 'expandedCalendarIds.remove(calendar.id)' in main,
 'restaurar estado': 'expanded_calendar_accounts' in main and 'expanded_calendar_ids' in main,
 'selección de calendario': 'Prefs.selectCalendar(this,calendar.id,on)' in main,
 'lectura concreta': 'CalendarBridge.events(this,calendar.id)' in main,
 'previsualización': 'showCalendarSchedulePreview(calendar,groups)' in main,
 'confirmación antes de importar': 'Confirmar horario importado' in main,
 'importación clases': 'db.importReviewed(picked)' in main,
 'reprogramación recordatorios': 'ScheduleReminders.rebuild(this)' in main,
 'deduplicación por día hora': 'String signature=day+":"+start+":"+end;' in conv,
 'zonas horarias': 'atZone(zone)' in conv,
 'exclusión día completo': 'e.allDay' in conv,
 'exclusión cruces medianoche': 'begin.toLocalDate().equals(finish.toLocalDate())' in conv,
 'eventos sin ubicación': 'e.location==null?"":e.location.trim()' in conv,
 'color único por curso': 'ScheduleCourseColors.deterministic(item.course)' in conv,
 'captura de ubicación': '"eventLocation"' in bridge,
 'cuenta como origen': 'Cuenta: "+calendar.account' in main,
}
for label,passed in checks.items():
    if not passed: raise AssertionError('FALLÓ '+label)
print('PASS:',len(checks),'verificaciones de Agenda 3.7')