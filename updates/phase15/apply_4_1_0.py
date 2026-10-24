from pathlib import Path
import shutil
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
source=Path("updates/phase15/AgendaMotion.kt")
target=root/"motion/AgendaMotion.kt"
target.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(source,target)
compose=root/"ComposeDayActivity.kt"
s=compose.read_text()
needle="import androidx.compose.runtime.*"
assert needle in s
s=s.replace(needle,needle+"\nimport pe.agendaclara.app.motion.MotionReveal")
old='''            if (loading) LinearProgressIndicator(Modifier.fillMaxWidth())
            if (error != null) Text(error, color = MaterialTheme.colorScheme.error)
            if (!loading && error == null && visible.isEmpty()) {
                Text("No hay tareas para este filtro.", color = muted, modifier = Modifier.padding(20.dp))
            }'''
new='''            MotionReveal(visible = loading) {
                LinearProgressIndicator(Modifier.fillMaxWidth())
            }
            MotionReveal(visible = error != null) {
                Text(error ?: "", color = MaterialTheme.colorScheme.error)
            }
            MotionReveal(visible = !loading && error == null && visible.isEmpty()) {
                Text("No hay tareas para este filtro.", color = muted, modifier = Modifier.padding(20.dp))
            }'''
assert old in s
compose.write_text(s.replace(old,new))
java=root/"UiMotion.java"
u=java.read_text()
# Existing 4.0 patch occasionally duplicates slideReveal; normalize identical copies.
start=u.index("    public static void slideReveal(")
end=u.index("    public static void reveal(",start)
section=u[start:end]
if section.count("public static void slideReveal(")>1:
    midpoint=section.index("    public static void slideReveal(",10)
    section=section[:midpoint]
    u=u[:start]+section+u[end:]
u=u.replace('setDuration(250)','setDuration(240)').replace('setDuration(140)','setDuration(140)')
java.write_text(u)
g=Path("AgendaClara/app/build.gradle")
z=g.read_text()
assert "versionCode 30" in z and "versionName '4.0.0'" in z
g.write_text(z.replace("versionCode 30","versionCode 31").replace("versionName '4.0.0'","versionName '4.1.0'"))
print("Phase 1 integrated: Compose motion library + native Java compatibility")
