#!/usr/bin/env python3
"""3.9.9 — substitute the two calendar PNGs with icon-only transparent artworks.

The preceding phase38 lays out the buttons and starts from a reproducible source
archive. This patch only replaces their image assets and bumps the version.
"""
from pathlib import Path
import struct, zlib

STAGE=Path(__file__).resolve().parent
DRAWABLE=Path("AgendaClara/app/src/main/res/drawable-nodpi")
GRADLE=Path("AgendaClara/app/build.gradle")

def alpha_stats(data):
    assert data.startswith(b'\x89PNG\r\n\x1a\n')
    offset=8; raw=bytearray(); width=height=0; depth=color=0
    while offset<len(data):
        length=struct.unpack_from(">I",data,offset)[0]; kind=data[offset+4:offset+8]
        body=data[offset+8:offset+8+length]
        stored=struct.unpack_from(">I",data,offset+8+length)[0]
        if zlib.crc32(kind+body)&0xffffffff!=stored:raise ValueError("PNG chunk CRC mismatch")
        if kind==b'IHDR':
            width,height,depth,color=struct.unpack(">IIBB",body[:10])
        if kind==b'IDAT':raw+=body
        offset+=12+length
        if kind==b'IEND':break
    if (width,height,depth,color)!=(256,256,8,6):
        raise ValueError(f"Expected transparent 256px RGBA PNG, got {(width,height,depth,color)}")
    packed=zlib.decompress(bytes(raw))
    stride=width*4
    pos=0; prev=bytearray(stride)
    alphas=[]
    corner_samples=[]
    for y in range(height):
        kind=packed[pos];pos+=1
        scan=bytearray(packed[pos:pos+stride]);pos+=stride
        for i in range(stride):
            left=scan[i-4] if i>=4 else 0
            above=prev[i]
            ul=prev[i-4] if i>=4 else 0
            if kind==1:scan[i]=(scan[i]+left)&255
            elif kind==2:scan[i]=(scan[i]+above)&255
            elif kind==3:scan[i]=(scan[i]+((left+above)//2))&255
            elif kind==4:
                p=left+above-ul
                da,db,dc=abs(p-left),abs(p-above),abs(p-ul)
                paeth=left if da<=db and da<=dc else (above if db<=dc else ul)
                scan[i]=(scan[i]+paeth)&255
            elif kind!=0:raise ValueError("Unsupported PNG scanline filter")
        alphas.extend(scan[3::4])
        if y in (0,height-1):corner_samples.extend([scan[3],scan[-1]])
        prev=scan
    if any(corner_samples):raise ValueError("PNG image corners must be completely transparent")
    if not(0.15 < alphas.count(0)/len(alphas) < 0.75):
        raise ValueError("Expected a transparent outer canvas around the icon")
    if sum(a>230 for a in alphas)/len(alphas)<0.2:
        raise ValueError("Foreground icon unexpectedly missing")
    return width,height

def once(src,old,new):
    if src.count(old)!=1:raise RuntimeError("Expected one version anchor")
    return src.replace(old,new,1)

def apply():
    images={}
    for name in ('ic_ref_today_jump.png','ic_ref_class_schedule.png'):
        source=STAGE/'assets'/name
        data=source.read_bytes()
        alpha_stats(data)
        target=DRAWABLE/name
        if not target.is_file():raise RuntimeError("Phase38 resource missing: "+str(target))
        if not target.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            raise RuntimeError("Refusing to replace unrecognized resource")
        images[target]=data
    grad=GRADLE.read_text(encoding='utf-8')
    grad=once(grad,'versionCode 39','versionCode 40')
    grad=once(grad,"versionName '3.9.8'","versionName '3.9.9'")
    for path,data in images.items():path.write_bytes(data)
    GRADLE.write_text(grad,encoding='utf-8')
    print("PASS phase39: transparent icon-only multicolor PNGs, calendar layout unchanged, 3.9.9")

if __name__=='__main__':apply()
