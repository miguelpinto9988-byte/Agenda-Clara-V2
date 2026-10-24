#!/usr/bin/env python3
from pathlib import Path
root=Path("AgendaClara")
p=root/"app/src/main/java/pe/agendaclara/app"
s=(p/"MainActivity.java").read_text(encoding="utf-8")
gradle=(root/"app/build.gradle").read_text()
checks={
"version 2.2":"versionName '2.2.0'" in gradle and "versionCode 11" in gradle,
"Android 16":"compileSdk 36" in gradle and "targetSdk 36" in gradle,
"modular agenda":(p/"AgendaFilters.java").is_file() and "AgendaFilters.matches" in s,
"modular review":(p/"ReviewFilters.java").is_file() and "ReviewFilters.matches" in s,
"motion guarded":(p/"UiMotion.java").is_file() and "if(!samePage)UiMotion.reveal(body)" in s,
"review search preserved":"reviewQuery=state.getString" in s and 'out.putString("review_query",reviewQuery)' in s,
"review independent list":"void fillReviewList(List<Store.Inbox> all)" in s,
"review stateful filters":'"Sin fecha","Vencidas","Del historial","Próximas"' in s,
"review search without full render":'reviewSearchTask=()->{if(page==2&&search.isAttachedToWindow())fillReviewList(inbox);}' in s,
"review expanded text":'"Ocultar mensaje original"' in s,
"review date warning":"PLAZO VENCIDO" in s,
"task search accents":"AgendaFilters.searchKey(search)" in (p/"ReviewFilters.java").read_text(),
"task save retained":"Store.get(this).save(t)" in s,
"proposal confirmation retained":'openEditor(-1,p,null)' in s,
"content descriptions":'Buscar propuestas por actividad' in s,
"same signing key":"signingConfig signingConfigs.development" in gradle,
"1h cleanup untouched":'CompletedTaskCleanup.run' in s
}
for label,ok in checks.items():
 if not ok:raise AssertionError(label)
print("PASS:",len(checks),"Agenda 2.2 modularization and UI checks")
