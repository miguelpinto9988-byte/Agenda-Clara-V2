#!/usr/bin/env python3
"""Pruebas de regresión estáticas para el navegador de conexiones 3.6."""
from pathlib import Path
root=Path("AgendaClara/app/src/main/java/pe/agendaclara/app")
main=(root/"MainActivity.java").read_text(encoding="utf-8")
listener=(root/"WhatsAppListener.java").read_text(encoding="utf-8")
store=(root/"Store.java").read_text(encoding="utf-8")
review=(root/"ReviewFlow.java").read_text(encoding="utf-8")
checks={
  "expandir/contraer comunidades":("inner.setVisibility(expanded?View.VISIBLE:View.GONE)" in main or "MotionKit.collapse(inner)" in main),
  "expandir/contraer conversación":"details.setVisibility(expanding?View.VISIBLE:View.GONE)" in main,
  "estado persistido":"putStringArrayList(\"expanded_chat_cards\"" in main,
  "sin auto autorizar":"Autorizar lectura" in main and "Revocar lectura" in main,
  "filtro comunidades":"case 1:return chat.community;" in main,
  "filtro grupos":"case 2:return !chat.community&&isChatGroup(chat);" in main,
  "filtro individuales":"case 3:return !chat.community&&!isChatGroup(chat);" in main,
  "origen notificaciones":"NOTIFICACIONES" in main,
  "origen vinculado":"VINCULADO" in main,
  "reconocimiento notificaciones activo":"getBoolean(\"discover\"" in listener,
  "metadatos sin leer mensajes no seleccionados":"!chat.selected)return;" in listener,
  "captura bajo autorización explícita":"putBoolean(\"capture\",true)" in main,
  "autorizar no es guardar tarea":"Store.get(this).selectChat(chat.key,true)" in main,
  "importacion individual explícita":"recordImportedMessage(key,m)" in main,
  "mensajes de importación separados":"saveMessageWithScope(key,m,true)" in store,
  "propuestas de importación":"analyzeImported(Context context,String chatKey)" in review,
}
for label,passed in checks.items():
  if not passed:raise AssertionError(label)
print("PASS: "+str(len(checks))+" verificaciones estáticas de conexiones 3.6")
