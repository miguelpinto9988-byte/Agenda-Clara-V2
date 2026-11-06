#!/usr/bin/env python3
"""One-time import of approved Canva PNGs into version-controlled Android assets.
The expiring image URLs are needed only for initial vendoring. Rebuilds read the
committed local PNG files and never depend on Canva or network access.
"""
from pathlib import Path
from PIL import Image
from io import BytesIO
from urllib.request import Request, urlopen
import hashlib
import json

STAGE=Path(__file__).resolve().parent
OUT=STAGE/"assets"
NAMES=(
    "ac_day_landscape","ac_day_icon_calendar","ac_day_icon_cap",
    "ac_day_icon_books","ac_day_icon_flask","ac_day_icon_clock",
    "ac_day_icon_room","ac_day_icon_check","ac_day_icon_arrow",
)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if all((OUT/(name+".png")).is_file() for name in NAMES):
        print("PASS: all original-source PNG assets already bundled; no network request")
        return
    sources=json.loads((STAGE/"assets_source_urls.json").read_text(encoding="utf-8"))
    for name in NAMES:
        output=OUT/(name+".png")
        if output.is_file():continue
        url=sources.get(name)
        if not url or not url.startswith("https://"):
            raise RuntimeError("Missing approved PNG source: "+name)
        request=Request(url,headers={"User-Agent":"Mozilla/5.0 (AgendaClaraCI/1.0)"})
        with urlopen(request,timeout=45) as response:
            raw=response.read(9000000)
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("Canva source is not PNG: "+name)
        with Image.open(BytesIO(raw)) as picture:
            if picture.format!="PNG":raise RuntimeError("Invalid PNG source")
            picture.load()
            if name=="ac_day_landscape":
                if picture.width<900 or picture.height<320:
                    raise RuntimeError("Canva landscape export too small; refusing blurry output: "
                                       +str(picture.size))
                # The exported Canva image has the unaltered approved landscape
                # layered across the top 960x320 pixels of a 960x656 design.
                result=picture.convert("RGB").crop((0,0,960,320))
                result=result.quantize(colors=256,method=Image.Quantize.MEDIANCUT,
                    dither=Image.Dither.FLOYDSTEINBERG)
            else:
                if picture.width<180 or picture.height<180:
                    raise RuntimeError("Canva icon thumbnail too small: "+name)
                picture=picture.convert("RGBA")
                alpha=picture.getchannel("A")
                if alpha.getextrema()[0]!=0 or alpha.getextrema()[1]<180:
                    raise RuntimeError("PNG icon is missing transparent pixels: "+name)
                result=picture.resize((192,192),Image.Resampling.LANCZOS)
                result=result.quantize(colors=256,method=Image.Quantize.FASTOCTREE)
            result.save(output,"PNG",optimize=True,compress_level=9)
        print("PASS:",name,output.stat().st_size,
            hashlib.sha256(output.read_bytes()).hexdigest()[:16])
    assert len(list(OUT.glob("ac_day_*.png")))==9
    print("PASS: 9 approved Canva PNGs, including alpha-transparent UI icons")

if __name__=="__main__":
    main()
