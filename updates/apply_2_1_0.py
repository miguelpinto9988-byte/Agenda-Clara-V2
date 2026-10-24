#!/usr/bin/env python3
"""2.1: encrypted backups, less UI-thread SQLite, lower event polling, privacy defaults."""
from pathlib import Path
p=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
def change(filename,old,new):
    file=p/filename;s=file.read_text(encoding="utf-8")
    if s.count(old)!=1:raise RuntimeError(f"{filename}: pattern count {s.count(old)} != 1: {old[:110]}")
    file.write_text(s.replace(old,new,1),encoding="utf-8")
for name in ("SecureArchive.java","SecureTaskBackup.java"):
    (p/name).write_bytes((Path("updates/phase5")/name).read_bytes())
change("TaskBackup.java",
'''  public static int exportTo(Context context,Uri uri)throws Exception{
    List<Task> list=Store.get(context).all();''',
'''  public static int exportTo(Context context,Uri uri)throws Exception{
    byte[] data=exportBytes(context);
    try(OutputStream out=context.getContentResolver().openOutputStream(uri,"wt")){
      if(out==null)throw new IOException("No se puede crear el archivo.");out.write(data);
    }finally{java.util.Arrays.fill(data,(byte)0);}
    return Store.get(context).all().size();
  }
  /** Compatible task-only JSON payload, built in private application memory. */
  public static byte[] exportBytes(Context context)throws Exception{
    List<Task> list=Store.get(context).all();''')
change("TaskBackup.java",
'''    try(OutputStream out=context.getContentResolver().openOutputStream(uri,"wt")){
      if(out==null)throw new IOException("No se puede crear el archivo.");
      out.write(data);
    }
    return list.size();
  }
  public static int importFrom(Context context,Uri uri)throws Exception{
    StringBuilder b=new StringBuilder();''',
'''    return data;
  }
  public static int importFrom(Context context,Uri uri)throws Exception{
    StringBuilder b=new StringBuilder();''')
change("TaskBackup.java",
'''    JSONObject root=new JSONObject(b.toString());
    if(!"agenda-clara-tasks"''',
'''    return importBytes(context,b.toString().getBytes(StandardCharsets.UTF_8));
  }
  public static int importBytes(Context context,byte[] data)throws Exception{
    if(data==null||data.length>MAX_CHARS)throw new IOException("Archivo superior a 6 MB.");
    JSONObject root=new JSONObject(new String(data,StandardCharsets.UTF_8));
    if(!"agenda-clara-tasks"''')
change("MainActivity.java",'import android.text.*;\nimport android.view.*;',
                         'import android.text.*;\nimport android.text.method.PasswordTransformationMethod;\nimport android.view.*;')
change("MainActivity.java",'import java.util.*;\n','import java.util.*;\nimport java.util.concurrent.*;\n')
change("MainActivity.java",
'    Map<Long,int[]> taskProgressCache=Collections.emptyMap();',
'''    private final ExecutorService periodicMaintenance=Executors.newSingleThreadExecutor();
    private char[] secureBackupPassword;
    Map<Long,int[]> taskProgressCache=Collections.emptyMap();''')
change("MainActivity.java",
'        if(resumed){CompletedTaskCleanup.run(MainActivity.this);if(page<2){forceRefresh=true;requestRefresh();}handler.postDelayed(this,60000);}',
'        if(resumed){periodicMaintenance.execute(()->CompletedTaskCleanup.run(getApplicationContext()));if(page<2){forceRefresh=true;requestRefresh();}handler.postDelayed(this,60000);}')
change("MainActivity.java",
'    @Override protected void onDestroy(){handler.removeCallbacksAndMessages(null);',
'    @Override protected void onDestroy(){periodicMaintenance.shutdownNow();clearBackupPassword();handler.removeCallbacksAndMessages(null);')
change("MainActivity.java",
'        protection.addView(button("Restaurar tareas desde JSON",this::importTasks));',
'''        protection.addView(button("Restaurar tareas desde JSON",this::importTasks));
        protection.addView(text("Recomendado: copia cifrada con contraseña para guardarla fuera del teléfono.",13,MUTED,true));
        protection.addView(button("🔒 Exportar copia cifrada (.acbak)",()->requestSecureBackup(true)));
        protection.addView(button("🔑 Restaurar copia cifrada (.acbak)",()->requestSecureBackup(false)));''')
change("MainActivity.java",
'text("Agenda Clara 2.0 · Interfaz accesible y Android 16",17,INK,true)',
'text("Agenda Clara 2.1 · Privacidad y estabilidad",17,INK,true)')
change("MainActivity.java",
'    private static final int EXPORT_TASKS_REQUEST=642,IMPORT_TASKS_REQUEST=643;',
'''    private static final int EXPORT_TASKS_REQUEST=642,IMPORT_TASKS_REQUEST=643;
    private static final int EXPORT_ENCRYPTED_REQUEST=644,IMPORT_ENCRYPTED_REQUEST=645;
    private void clearBackupPassword(){if(secureBackupPassword!=null)Arrays.fill(secureBackupPassword,'\0');secureBackupPassword=null;}
    private void requestSecureBackup(boolean exporting){
        clearBackupPassword();
        LinearLayout panel=column();panel.setPadding(dp(16),dp(4),dp(16),dp(4));
        EditText password=input("Contraseña (10 caracteres mínimo)","",android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);
        password.setTransformationMethod(PasswordTransformationMethod.getInstance());panel.addView(password);
        EditText repeat=null;
        if(exporting){repeat=input("Repite la contraseña","",android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);repeat.setTransformationMethod(PasswordTransformationMethod.getInstance());panel.addView(repeat);}
        final EditText confirm=repeat;
        AlertDialog dlg=dialogBuilder().setTitle(exporting?"Crear copia cifrada":"Restaurar copia cifrada")
            .setMessage("El cifrado utiliza AES-GCM y una contraseña que no se guarda en la app. Si la pierdes, no podrás recuperar la copia. No se incluyen mensajes ni sesiones de WhatsApp.")
            .setView(panel).setNegativeButton("Cancelar",null).setPositiveButton("Continuar",null).create();
        dlg.setOnShowListener(ignore->dlg.getButton(-1).setOnClickListener(v->{
            String value=password.getText().toString();
            if(value.length()<10||value.length()>256){password.setError("De 10 a 256 caracteres.");return;}
            if(confirm!=null&&!value.equals(confirm.getText().toString())){confirm.setError("Las contraseñas no coinciden.");return;}
            secureBackupPassword=value.toCharArray();password.setText("");if(confirm!=null)confirm.setText("");
            dlg.dismiss();
            Intent intent=new Intent(exporting?Intent.ACTION_CREATE_DOCUMENT:Intent.ACTION_OPEN_DOCUMENT)
                .addCategory(Intent.CATEGORY_OPENABLE).setType("application/octet-stream");
            if(exporting)intent.putExtra(Intent.EXTRA_TITLE,"Agenda-Clara-copia-cifrada.acbak");
            try{startActivityForResult(intent,exporting?EXPORT_ENCRYPTED_REQUEST:IMPORT_ENCRYPTED_REQUEST);}
            catch(ActivityNotFoundException ex){clearBackupPassword();toast("No hay una aplicación de archivos compatible.");}
        }));dlg.show();
    }
    private void encryptedResult(int request,Uri uri){
        final char[] password=secureBackupPassword;secureBackupPassword=null;
        if(password==null){toast("Vuelve a introducir la contraseña.");return;}
        new Thread(()->{
            try{
                final int count=request==EXPORT_ENCRYPTED_REQUEST?
                    SecureTaskBackup.exportTo(this,uri,password):SecureTaskBackup.importFrom(this,uri,password);
                if(request==IMPORT_ENCRYPTED_REQUEST){CompletedTaskCleanup.run(this);Reminders.rebuild(this);TaskWidget.refresh(this);}
                runOnUiThread(()->{toast(request==EXPORT_ENCRYPTED_REQUEST?"Copia cifrada guardada: "+count+" tareas.":"Restauradas "+count+" tareas desde copia cifrada.");forceRefresh=true;requestRefresh();});
            }catch(Exception ex){runOnUiThread(()->toast("No se pudo procesar la copia. Comprueba contraseña y archivo."));}
            finally{Arrays.fill(password,'\0');}
        },"secure-backup").start();
    }''')
change("MainActivity.java",
'''        if((request==EXPORT_TASKS_REQUEST||request==IMPORT_TASKS_REQUEST)&&result==RESULT_OK&&data!=null&&data.getData()!=null){backupResult(request,data.getData());return;}''',
'''        if(request==EXPORT_ENCRYPTED_REQUEST||request==IMPORT_ENCRYPTED_REQUEST){
            if(result==RESULT_OK&&data!=null&&data.getData()!=null)encryptedResult(request,data.getData());
            else clearBackupPassword();return;
        }
        if((request==EXPORT_TASKS_REQUEST||request==IMPORT_TASKS_REQUEST)&&result==RESULT_OK&&data!=null&&data.getData()!=null){backupResult(request,data.getData());return;}''')
change("WhatsAppSessionService.java",'        },300,500,TimeUnit.MILLISECONDS);','        },300,1500,TimeUnit.MILLISECONDS);')
change("WhatsAppSessionService.java",'        stopping=true;worker.shutdown();','        stopping=true;worker.shutdownNow();')
for filename in ("MainActivity.java","ReviewFlow.java","Store.java","WhatsAppSessionService.java"):
    file=p/filename
    contents=file.read_text(encoding="utf-8")
    file.write_text(contents.replace('getInt("wa_history_days",90)','getInt("wa_history_days",30)'),encoding="utf-8")
change("Store.java",
'''    public synchronized List<Task> all(){
        purgeExpiredCompleted(System.currentTimeMillis());''',
'''    public synchronized List<Task> all(){
        // Expiration uses scheduled maintenance; avoid writes on normal UI reads.''')
change("MainActivity.java",
'                if(Store.get(this).messageCount(chat.key)>0)c.addView(text("Mensajes conservados: "+Store.get(this).messageCount(chat.key),12,MUTED,false));',
'                int retained=Store.get(this).messageCount(chat.key);\n                if(retained>0)c.addView(text("Mensajes conservados: "+retained,12,MUTED,false));')
gradle=Path("AgendaClara/app/build.gradle");config=gradle.read_text(encoding="utf-8")
if config.count("versionCode 9")!=1 or config.count("versionName '2.0.0'")!=1:raise RuntimeError("Expected 2.0.0 base")
gradle.write_text(config.replace("versionCode 9","versionCode 10").replace("versionName '2.0.0'","versionName '2.1.0'"),encoding="utf-8")
print("Agenda Clara 2.1.0 security and stability changes applied.")
