#!/usr/bin/env python3
"""Checks for Android 16 build configuration, UI controls and SQL batching."""
from pathlib import Path
p=Path("AgendaClara")
java=p/"app/src/main/java/pe/agendaclara/app"
main=(java/"MainActivity.java").read_text()
store=(java/"Store.java").read_text()
gradle=(p/"app/build.gradle").read_text()
manifest=(p/"app/src/main/AndroidManifest.xml").read_text()
assertions={
 "versionCode 9":"versionCode 9" in gradle,
 "versionName 2.0.0":"versionName '2.0.0'" in gradle,
 "targetSdk 36":"targetSdk 36" in gradle,
 "compileSdk 36":"compileSdk 36" in gradle,
 "manifest targetSdk 36":'android:targetSdkVersion="36"' in manifest,
 "AGP version":"8.13.2" in (p/"build.gradle").read_text(),
 "Gradle wrapper":"gradle-8.13-bin.zip" in (p/"gradle/wrapper/gradle-wrapper.properties").read_text(),
 "accessibility settings":"Accesibilidad y lectura" in main,
 "persist contrast":"UiPreferences.setContrast" in main,
 "persist text size":"UiPreferences.setSizePercent" in main,
 "text scaling":"setTextSize(UiPreferences.scaled(this,size))" in main,
 "button scaling":"setTextSize(UiPreferences.scaled(this,14))" in main,
 "minimum tappable size":"b.setMinHeight(dp(48))" in main,
 "nav selection state":"item.setSelected(page==n)" in main,
 "accessible task checkbox":"Marcar como completada: " in main,
 "aggregate subtasks":"SELECT task_id,COUNT(*),COALESCE(SUM(done),0) FROM subtasks GROUP BY task_id" in store,
 "subtask map for visible pages":"taskProgressCache=page<2?Store.get(this).subtaskProgressAll()" in main,
 "summary math":"TaskSummary.calculate(all,now" in main,
 "summary transparency":"Avance estimado =" in main,
 "backup still available":"TaskBackup.importFrom" in main,
 "WhatsApp consent still available":"chooseGroup(chat)" in main
}
for label,ok in assertions.items():
 if not ok:raise AssertionError(label)
print("PASS:",len(assertions),"Android 16, accessibility, UI, data, compatibility checks")
