#!/usr/bin/env python3
from pathlib import Path
app=Path("AgendaClara/app")
g=(app/"build.gradle").read_text()
k=(app/"src/main/java/pe/agendaclara/app/ComposeDayActivity.kt").read_text()
m=(app/"src/main/AndroidManifest.xml").read_text()
s=(app/"src/main/java/pe/agendaclara/app/MainActivity.java").read_text()
tests={
 "2.5 version": "versionCode 14" in g and "versionName '2.5.0'" in g,
 "app id unchanged": "applicationId 'pe.agendaclara.app'" in g,
 "API 36": "targetSdk 36" in g,
 "Kotlin plugin": "id 'org.jetbrains.kotlin.android'" in g,
 "Compose compiler": "id 'org.jetbrains.kotlin.plugin.compose'" in g,
 "Compose enabled": "compose true" in g,
 "BOM pinned": "compose-bom:2026.02.00" in g,
 "Activity dependency": "activity-compose:1.10.1" in g,
 "same Kotlin plugin version": (Path("AgendaClara/build.gradle").read_text().count("version '2.4.10'")==2),
 "separate Kotlin activity": "class ComposeDayActivity : ComponentActivity()" in k,
 "immutable snapshot": "data class TaskPreview" in k,
 "background DB": "io.execute {" in k,
 "private activity": '.ComposeDayActivity" android:exported="false"' in m,
 "legacy launcher unchanged": '.MainActivity" android:exported="true"' in m,
 "native editor route": 'putExtra("task_id", id)' in k,
 "accent-insensitive search": "AgendaFilters.searchKey" in k,
 "no automated edits": ".save(" not in k and "Store.get(applicationContext).all()" in k,
 "entrypoint visible": "new Intent(this,ComposeDayActivity.class)" in s,
 "whatsapp preserved": "WhatsAppSessionService" in m,
 "encrypted backups preserved": "SecureTaskBackup" in s,
 "SQLite 7 intact": 'super(c,"agenda_clara.db",null,7)' in (app/"src/main/java/pe/agendaclara/app/Store.java").read_text(),
 "historical signature retained": "signingConfig signingConfigs.development" in g
}
for key,ok in tests.items():
 if not ok: raise AssertionError(key)
print("PASS:",len(tests),"Kotlin+Compose 2.5 regression checks")
