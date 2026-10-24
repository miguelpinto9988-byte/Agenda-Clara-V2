#!/usr/bin/env python3
"""Agenda Clara 2.7.0: position-aware offline OCR for multirow timetable images.
Run after the verified 2.6.1 patch. Preserves all stored data and signing.
"""
from pathlib import Path
import zlib,base64,json,hashlib
base=Path("AgendaClara")
src=base/"app/src/main/java/pe/agendaclara/app"
payload=Path("updates/phase12/ocr_payload.b64.txt").read_text(encoding="utf-8").strip()
if hashlib.sha256(payload.encode()).hexdigest()!="088846592b482b984bca1bb1657f346495f04d42df638f5fd38109d492ecdbac":
    raise RuntimeError("OCR source checksum mismatch; refusing to overwrite files")
files=json.loads(zlib.decompress(base64.b64decode(payload)).decode("utf-8"))
for name,content in files.items():
    if name not in ("SchedulePhotoLoader.java","ScheduleOcr.java","ScheduleGridInterpreter.java","ScheduleImageBlocks.java"):
        raise RuntimeError("Unexpected file in patch: "+name)
    (src/name).write_text(content,encoding="utf-8")
activity=src/"ScheduleActivity.java"
code=activity.read_text(encoding="utf-8")
old="""                InputImage image=SchedulePhotoLoader.read(this,uri);
                runOnUiThread(()->{
                    if(isFinishing()||isDestroyed())return;
                    TextRecognizer scanner=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
                    scanner.process(image).addOnSuccessListener(text->{scanner.close();recognizing=false;detected=ScheduleOcr.analyze(text);chosen.clear();for(int n=0;n<detected.candidates.size();n++)chosen.add(true);show(5);})
                        .addOnFailureListener(ex->{scanner.close();recognizing=false;toast("No se pudo leer la imagen. Prueba con otra foto.");show(1);});
                });"""
new="""                SchedulePhotoLoader.Photo photo=SchedulePhotoLoader.readForLayout(this,uri);
                List<ScheduleGridInterpreter.Tile> rectangles=ScheduleImageBlocks.detect(photo.bitmap);
                int imageWidth=photo.bitmap.getWidth(),imageHeight=photo.bitmap.getHeight();
                runOnUiThread(()->{
                    if(isFinishing()||isDestroyed()){photo.bitmap.recycle();recognizing=false;return;}
                    TextRecognizer scanner=TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
                    scanner.process(photo.image).addOnSuccessListener(text->{
                        scanner.close();recognizing=false;
                        try{detected=ScheduleOcr.analyze(text,rectangles,imageWidth,imageHeight);}
                        finally{if(!photo.bitmap.isRecycled())photo.bitmap.recycle();}
                        chosen.clear();for(int n=0;n<detected.candidates.size();n++)chosen.add(true);show(5);
                    }).addOnFailureListener(ex->{scanner.close();recognizing=false;if(!photo.bitmap.isRecycled())photo.bitmap.recycle();toast("No se pudo leer la imagen. Prueba con otra foto.");show(1);});
                });"""
if code.count(old)!=1:raise RuntimeError("ScheduleActivity OCR anchor changed")
code=code.replace(old,new,1)
old_review='head(top,"Revisa antes de guardar","Reconocimos "+(detected==null?0:detected.candidates.size())+" clases posibles. Comprueba especialmente días, aulas y horas.");'
new_review='head(top,"Revisa antes de guardar","Reconocimos "+(detected==null?0:detected.candidates.size())+" bloques de clase. Si un curso abarca varias filas, se toma el inicio de la primera y el fin de la última. Revisa antes de guardar.");'
if code.count(old_review)!=1:raise RuntimeError("OCR review anchor changed")
activity.write_text(code.replace(old_review,new_review,1),encoding="utf-8")
gradle=base/"app/build.gradle"
config=gradle.read_text(encoding="utf-8")
if config.count("versionCode 16")!=1 or config.count("versionName '2.6.1'")!=1:
    raise RuntimeError("Requires Agenda Clara 2.6.1")
gradle.write_text(config.replace("versionCode 16","versionCode 17").replace("versionName '2.6.1'","versionName '2.7.0'"),encoding="utf-8")
print("Agenda Clara 2.7.0: multi-row image geometry importer installed")
