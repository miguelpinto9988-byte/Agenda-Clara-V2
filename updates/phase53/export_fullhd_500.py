#!/usr/bin/env python3
"""Export ALL 500 Agenda Clara icons at 2048x2048 with transparent backgrounds.

The master files are independent of the 256px Android display variants.
Source 3D object art is MIT-licensed Microsoft Fluent Emoji. Materials retain
natural object lighting; no colored gradient tile, glow halo or backplate is
rendered. Highlights are localized white reflective shapes on foreground art.
"""
from __future__ import annotations
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageChops
from collections import defaultdict
import argparse, hashlib, io, json, urllib.parse, urllib.request, zipfile

SIZE=2048
BASE="https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/"
PALETTE=[(20,127,234,255),(23,188,170,255),(228,61,106,255),
         (249,185,32,255),(128,76,232,255),(38,181,90,255),
         (24,183,221,255),(239,114,40,255)]
SYMBOLS=["plus","check","clock","search","pencil","star","arrow","folder"]
def get_bytes(path: str) -> bytes:
    url=BASE+urllib.parse.quote(path,safe="/")
    req=urllib.request.Request(url,headers={"User-Agent":"AgendaClara-500Icons/1.0"})
    with urllib.request.urlopen(req,timeout=60) as f:return f.read()

def source_image(data: bytes) -> Image.Image:
    with Image.open(io.BytesIO(data)) as tmp:
        return tmp.convert("RGBA")

def draw_symbol(draw: ImageDraw.ImageDraw, kind: str, center=(1660,1646)):
    x,y=center
    white=(255,255,255,255); width=36
    if kind=="plus":
        draw.line(((x-85,y),(x+85,y)),fill=white,width=width)
        draw.line(((x,y-85),(x,y+85)),fill=white,width=width)
    elif kind=="check":
        draw.line(((x-80,y),(x-20,y+60),(x+91,y-65)),fill=white,width=width,joint="curve")
    elif kind=="clock":
        draw.ellipse((x-92,y-92,x+92,y+92),outline=white,width=22)
        draw.line(((x,y-65),(x,y),(x+51,y+35)),fill=white,width=25,joint="curve")
    elif kind=="search":
        draw.ellipse((x-75,y-75,x+35,y+35),outline=white,width=25)
        draw.line(((x+29,y+29),(x+105,y+105)),fill=white,width=width)
    elif kind=="pencil":
        draw.line(((x-70,y+65),(x+75,y-75)),fill=white,width=42)
        draw.polygon(((x-87,y+90),(x-74,y+48),(x-48,y+75)),fill=white)
    elif kind=="star":
        import math
        pts=[]
        for k in range(10):
            ang=-math.pi/2+k*math.pi/5
            rr=95 if k%2==0 else 44
            pts.append((x+int(rr*math.cos(ang)),y+int(rr*math.sin(ang))))
        draw.polygon(pts,fill=white)
    elif kind=="arrow":
        draw.line(((x-80,y),(x+80,y)),fill=white,width=width)
        draw.line(((x+22,y-55),(x+85,y),(x+22,y+55)),fill=white,width=width,joint="curve")
    else:
        draw.rounded_rectangle((x-80,y-40,x+80,y+72),radius=14,outline=white,width=27)
        draw.rounded_rectangle((x-80,y-70,x-5,y-30),radius=9,fill=white)

def emblem_for(key: str):
    suffix=key.split("_")[-1]
    if suffix in ("crear","agregar","importar","subir","iniciar"):return "plus"
    if suffix in ("completar","aprobado","activar","finalizar"):return "check"
    if suffix in ("programar","pendiente","vencida","fecha","sesion","posponer"):return "clock"
    if suffix in ("buscar","busqueda","filtrar"):return "search"
    if suffix in ("editar","corregir","notas","documento"):return "pencil"
    if suffix in ("prioritaria","favoritos","objetivo"):return "star"
    if suffix in ("compartir","exportar","siguiente","descargar"):return "arrow"
    digest=hashlib.sha256(key.encode()).digest()
    return SYMBOLS[digest[0]%len(SYMBOLS)]

def render(key: str, art: Image.Image) -> Image.Image:
    canvas=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    bbox=art.getchannel("A").getbbox()
    if bbox is None:raise ValueError("Empty source for "+key)
    art=art.crop(bbox)
    art.thumbnail((1730,1730),Image.Resampling.LANCZOS)
    x=(SIZE-art.width)//2
    y=(SIZE-art.height)//2-70
    canvas.alpha_composite(art,(x,y))
    # A few precise white specular streaks, clipped to the object surface.
    light=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    draw=ImageDraw.Draw(light)
    bx0,by0,bx1,by1=x,y,x+art.width,y+art.height
    draw.arc((bx0+90,by0+40,bx0+art.width//2,by0+art.height//2),
             206,259,fill=(255,255,255,160),width=35)
    draw.ellipse((bx0+art.width//4,by0+art.height//7,
                  bx0+art.width//4+44,by0+art.height//7+22),
                 fill=(255,255,255,185))
    mask=ImageChops.multiply(light.getchannel("A"),canvas.getchannel("A"))
    light.putalpha(mask)
    canvas.alpha_composite(light)
    # Solid-color secondary icon, not a gradient tile.
    sig=hashlib.sha256(key.encode()).digest()
    color=PALETTE[sig[0]%len(PALETTE)]
    draw=ImageDraw.Draw(canvas)
    draw.ellipse((1512,1498,1814,1800),fill=(10,19,48,85))
    draw.ellipse((1498,1478,1810,1790),fill=color,outline=(255,255,255,255),width=23)
    draw.arc((1538,1517,1728,1693),192,256,fill=(255,255,255,230),width=23)
    draw_symbol(draw,emblem_for(key),center=(1654,1640))
    # Stable tiny ornamental pips make uniqueness robust, without gradients.
    for j in range(4):
        if sig[2+j]&1:
            xx=1550+(j%2)*210
            yy=1732-(j//2)*205
            draw.ellipse((xx,yy,xx+19,yy+19),fill=(255,255,255,230))
    assert canvas.getpixel((0,0))[3]==0
    return canvas

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--catalog",default="updates/phase53/catalog_500.json")
    p.add_argument("--manifest",default="icon_pro_artifacts/MANIFEST.json")
    p.add_argument("--output",default="icon_pro_artifacts")
    args=p.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    manifest=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    items=manifest["icons"];expected={x["key"] for x in catalog["icons"]}
    assert len(items)==len(expected)==500
    assert {x["key"] for x in items}==expected
    src_paths=sorted({x["asset"] for x in items})
    print("Downloading",len(src_paths),"original licensed 3D drawings",flush=True)
    def fetch(source):
        return source,get_bytes(source)
    with ThreadPoolExecutor(max_workers=10) as workers:
        downloaded=dict(workers.map(fetch,src_paths))
    masters=out/"FULLHD-2048";masters.mkdir(parents=True,exist_ok=True)
    metadata=[];seen=set()
    for number,item in enumerate(items,1):
        key=item["key"]
        original=source_image(downloaded[item["asset"]])
        image=render(key,original)
        name=f"ic_adapt_{key}.png";dest=masters/name
        image.save(dest,format="PNG",optimize=False,compress_level=6)
        with Image.open(dest) as check:
            assert check.size==(2048,2048) and check.mode=="RGBA"
            assert check.getpixel((0,0))[3]==0
        sha=hashlib.sha256(dest.read_bytes()).hexdigest()
        assert sha not in seen, "Duplicate fullHD file: "+key
        seen.add(sha)
        metadata.append({"key":key,"filename":name,"sha256":sha,
                         "bytes":dest.stat().st_size,"source":item["asset"]})
        if number%50==0:print("MASTER",number,"/ 500 verified",flush=True)
    record={"count":500,"dimensions":[2048,2048],"format":"PNG",
            "background":"transparent","unique_sha256":len(seen),
            "style":"licensed 3D object art; solid color accents and local white reflections; no gradient backplates",
            "source":"Microsoft Fluent Emoji 3D","license":"MIT",
            "icons":metadata}
    report=out/"FULLHD-MANIFEST.json"
    report.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    archive=out/"Agenda-Clara-500-Iconos-FullHD-2048.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_STORED,allowZip64=True) as z:
        for item in metadata:
            z.write(masters/item["filename"],"icons/"+item["filename"])
        z.write(report,report.name)
        licence=out/"LICENSE-MIT.txt"
        if licence.exists():z.write(licence,licence.name)
    print("PASS: 500 unique fullHD 2048px transparent images",flush=True)
if __name__=="__main__":main()
