#!/usr/bin/env python3
"""Generate a synthetic timetable screenshot for on-device OCR regression.

No external imagery or personal data. Test fixture is internal to Android QA.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

output=Path("/tmp/horario_ocr_regresion.png")
w,h=1200,760
image=Image.new("RGB",(w,h),(250,251,254))
d=ImageDraw.Draw(image)
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title=ImageFont.truetype(font_bold,33)
body=ImageFont.truetype(font_bold,27)
small=ImageFont.truetype(font_path,23)
d.text((70,35),"HORARIO DE CLASES - SEMANA 4",font=title,fill=(25,40,70))
headers=[("LUNES",255),("MARTES",595),("MIÉRCOLES",935)]
for name,x in headers:
    d.text((x,120),name,font=body,fill=(30,55,86))
d.text((36,234),"08:00 - 09:00",font=small,fill=(25,40,70))
d.text((36,464),"09:00 - 10:00",font=small,fill=(25,40,70))
# Two genuine course titles share EDUCACION only at the END, not the first word.
cells=[
  (225,185,540,335,(166,208,245),["Didáctica de","Educación"]),
  (555,185,870,335,(169,235,196),["Historia de la","Educación"]),
  (885,185,1185,335,(245,202,216),["Geografía"]),
  (225,420,540,590,(233,222,172),["Taller de Arte"]),
  (555,420,870,590,(178,215,236),["Matemática"]),
  (885,420,1185,590,(199,232,211),["Programación"]),
]
for left,top,right,bottom,color,words in cells:
    d.rounded_rectangle((left,top,right,bottom),radius=13,fill=color)
    for index,line in enumerate(words):
        d.text((left+18,top+27+index*46),line,font=body,fill=(18,43,75))
image.save(output)
print(output)
