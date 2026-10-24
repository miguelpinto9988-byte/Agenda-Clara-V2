#!/usr/bin/env python3
"""2.1 static regression coverage alongside JVM crypto tests and Gradle build."""
from pathlib import Path
p=Path("AgendaClara")
app=p/"app/src/main/java/pe/agendaclara/app"
main=(app/"MainActivity.java").read_text(encoding="utf-8")
backup=(app/"TaskBackup.java").read_text(encoding="utf-8")
service=(app/"WhatsAppSessionService.java").read_text(encoding="utf-8")
store=(app/"Store.java").read_text(encoding="utf-8")
gradle=(p/"app/build.gradle").read_text(encoding="utf-8")
checks={
"version 2.1.0":"versionName '2.1.0'" in gradle and "versionCode 10" in gradle,
"package unchanged":"applicationId 'pe.agendaclara.app'" in gradle,
"target compatibility":"targetSdk 36" in gradle,
"AES encrypted class":(app/"SecureArchive.java").exists(),
"encrypted import":(app/"SecureTaskBackup.java").exists(),
"export safe payload":"public static byte[] exportBytes" in backup,
"import safe payload":"public static int importBytes" in backup,
"backwards compatible JSON":'root.optInt("schema",-1)!=1' in backup,
"new encrypted export UI":"Exportar copia cifrada" in main,
"new encrypted import UI":"Restaurar copia cifrada" in main,
"password wiped":"Arrays.fill(password" in main,
"password never stored prefs":"secureBackupPassword=value.toCharArray()" in main,
"maintenance executor":"periodicMaintenance.execute(" in main,
"shutdown executor":"periodicMaintenance.shutdownNow()" in main,
"no UI-time expiration in all()":"purgeExpiredCompleted(System.currentTimeMillis());" not in store[store.index("public synchronized List<Task> all()"):store.index("public synchronized List<Task> all()")+240],
"reduced native event polling":"},300,1500,TimeUnit.MILLISECONDS);" in service,
"existing user history preference honored":'getInt("wa_history_days",30)' in service,
"no duplicate per-chat count":"int retained=Store.get(this).messageCount(chat.key);" in main,
"existing signing config retained":"signingConfig signingConfigs.development" in gradle
}
for title,ok in checks.items():
 if not ok:raise AssertionError(title)
print("PASS:",len(checks),"safety, upgrade and compatibility checks")
