#!/usr/bin/env python3
"""Six polished sticky-note PNG backgrounds, no Pillow/network dependency.

Keeps the pin and folded corner in the PNG; all note text remains editable native
Android TextViews. Reproducible and independent of density/theme.
"""
from pathlib import Path
import math
import struct
import zlib

W,H=800,460
COLORS={
    "yellow":(255,234,135),"pink":(255,196,215),"blue":(161,215,253),
    "green":(168,222,196),"purple":(212,190,249),"peach":(255,210,180)
}

def mix(a,b,k):
    k=max(0.0,min(1.0,k))
    return tuple(round(a[i]*(1-k)+b[i]*k) for i in range(3))

def rounded(x,y,l,t,r,b,rad):
    cx=min(max(x,l+rad),r-rad)
    cy=min(max(y,t+rad),b-rad)
    if (x<l+rad or x>r-rad) and (y<t+rad or y>b-rad):
        return math.hypot(x-cx,y-cy)<=rad
    return l<=x<=r and t<=y<=b

def segment_distance(x,y,ax,ay,bx,by):
    vx,vy=bx-ax,by-ay
    u=max(0.0,min(1.0,((x-ax)*vx+(y-ay)*vy)/(vx*vx+vy*vy)))
    return math.hypot(x-(ax+u*vx),y-(ay+u*vy))

def png_bytes(color):
    pixels=bytearray(W*H*4)
    for y in range(H):
        for x in range(W):
            p=(y*W+x)*4
            paper=rounded(x,y,27,29,775,432,26)
            if not paper:
                if rounded(x-5,y-8,27,29,775,432,26):
                    pixels[p:p+4]=bytes((59,46,87,46))
                continue
            base=mix(color,(255,255,255),.10+.07*(1-y/H))
            base=mix(base,(117,94,169),.027*y/H)
            noise=math.sin(x*.42+y*.76)*math.cos(x*.27-y*.59)*1.1
            rgb=tuple(round(max(0,min(255,c+noise))) for c in base)
            edge=min(x-27,775-x,y-29,432-y)
            if edge<4:rgb=mix(rgb,(194,159,233),.12*(4-edge)/4)
            if y>425:rgb=mix(rgb,(175,143,220),.22)
            # Cream-colored folded page corner, with a fine lavender crease.
            fold_y=373+(775-x)*(432-373)/75 if x>=700 else H+1
            if x>=700 and y>fold_y:
                rgb=mix((255,249,207),(245,227,135),.12+(x-700)/75*.08)
                if y-fold_y<2.4:rgb=mix(rgb,(165,142,208),.55)
            pixels[p:p+4]=bytes((*rgb,255))

    def overlay(x,y,rgb,alpha):
        if not(0<=x<W and 0<=y<H):return
        alpha=max(0.0,min(1.0,alpha))
        p=(y*W+x)*4
        below=pixels[p:p+4]
        old=below[3]/255
        result_alpha=alpha+old*(1-alpha)
        if not result_alpha:return
        new=tuple(round((rgb[c]*alpha+below[c]*old*(1-alpha))/result_alpha)
                  for c in range(3))
        pixels[p:p+4]=bytes((*new,round(result_alpha*255)))

    cx=W//2
    # Soft shadow under small tack
    for y in range(0,92):
        for x in range(cx-55,cx+55):
            d=math.hypot((x-(cx+10))*.88,(y-45)*1.08)
            if d<47:overlay(x,y,(55,30,81),.16*(1-d/47)**1.4)
    # Steel pin / needle, visible just below the head
    for y in range(18,86):
        for x in range(cx-32,cx+32):
            d=segment_distance(x,y,cx+3,39,cx-9,82)
            if d<3:overlay(x,y,(55,57,69),.95)
            elif d<4.2:overlay(x,y,(155,158,170),.72*(4.2-d)/1.2)
            if d<1.1:overlay(x,y,(205,209,219),.69)
    # Darker red pushpin collar, partly hidden by glossy cap
    for y in range(15,62):
        for x in range(cx-42,cx+42):
            dx=(x-cx)/31
            dy=(y-37)/19
            if dx*dx+dy*dy<1:
                overlay(x,y,mix((143,0,43),(244,35,80),.47-.15*dx-.10*dy),1)
    # Glossy red head: gradient, reflection and bevel.
    for y in range(-1,53):
        for x in range(cx-50,cx+50):
            dx=(x-cx)/39
            dy=(y-25)/26
            d=dx*dx+dy*dy
            if d<1:
                light=max(0.,min(1.,.37+.25*(-dx)+.25*(-dy)))
                fill=mix((158,2,45),(255,42,82),light)
                if ((dx+.32)/.27)**2+((dy+.48)/.19)**2<1:
                    fill=mix(fill,(255,229,235),.76)
                if ((dx-.12)/.78)**2+((dy-.85)/.13)**2<1:
                    fill=mix(fill,(103,0,36),.22)
                overlay(x,y,fill,1)

    raw=b"".join(b"\0"+pixels[y*W*4:(y+1)*W*4] for y in range(H))
    def chunk(tag,payload):
        return struct.pack(">I",len(payload))+tag+payload+struct.pack(">I",zlib.crc32(tag+payload)&0xffffffff)
    return (b"\x89PNG\r\n\x1a\n"+
            chunk(b"IHDR",struct.pack(">IIBBBBB",W,H,8,6,0,0,0))+
            chunk(b"IDAT",zlib.compress(raw,8))+
            chunk(b"IEND",b""))

def generate(destination):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    for name,color in COLORS.items():
        png=png_bytes(color)
        path=destination/("sticky_"+name+".png")
        path.write_bytes(png)
        print("PNG",path.name,len(png))

if __name__=="__main__":
    import sys
    if len(sys.argv)!=2:
        raise SystemExit("Usage: generate_sticky_assets.py drawable-nodpi-directory")
    generate(sys.argv[1])
