#!/usr/bin/env python3
"""Six 256x256 transparent PNG icons, generated with stdlib only."""
import math,struct,zlib
from pathlib import Path
OUT=Path('AgendaClara/app/src/main/res/drawable-nodpi');OUT.mkdir(parents=True,exist_ok=True)
N=256;BLUE=(4,93,249);CYAN=(31,205,247)
def circle(x,y,cx,cy,r):return math.hypot(x-cx,y-cy)<=r
def rr(x,y,l,t,r,b,q):
    return abs(x-min(max(x,l+q),r-q))**2+abs(y-min(max(y,t+q),b-q))**2<=q*q and l<=x<=r and t<=y<=b
def segment(x,y,x1,y1,x2,y2,w):
    dx=x2-x1;dy=y2-y1;z=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy+0.00001)))
    return math.hypot(x-(x1+dx*z),y-(y1+dy*z))<=w
def shape(kind,x,y):
    if kind=='microphone':
        if rr(x,y,91,43,165,148,36):return 2
        if ((96<=x<=160 and 130<=y<=178 and ((x-128)**2+(y-131)**2>=28**2)) or segment(x,y,97,143,97,156,9) or segment(x,y,159,143,159,156,9) or (90<=x<=166 and 141<=y<=187 and abs(math.hypot(x-128,y-147)-39)<=8 and y>=147)):return 1
        if segment(x,y,128,187,128,215,10) or segment(x,y,93,220,163,220,10):return 1
    elif kind=='waveform':
        lengths=[30,58,86,119,158,185,139,107,78,55,29]
        i=round((x-27)/20.2)
        if 0<=i<11 and abs(x-(27+i*20.2))<8:
            h=lengths[i]
            if rr(x,y,27+i*20.2-8,128-h/2,27+i*20.2+8,128+h/2,8):return 1 if i%2 else 2
    elif kind=='bell':
        if circle(x,y,128,202,14):return 2
        if (70<=x<=186 and 66<=y<=181 and (circle(x,y,128,131,60) or rr(x,y,68,133,188,181,30))) or rr(x,y,54,176,202,196,8):return 1
        if circle(x,y,128,68,18):return 2
    elif kind=='check':
        if rr(x,y,28,28,228,228,42):return 3
        if segment(x,y,68,130,111,173,13) or segment(x,y,111,173,194,80,13):return 1
    elif kind=='calendar':
        if rr(x,y,35,48,221,221,28):return 1
        if rr(x,y,52,107,203,204,13):return 3
        if segment(x,y,87,35,87,76,12) or segment(x,y,170,35,170,76,12):return 2
        if circle(x,y,89,145,12) or circle(x,y,130,145,12) or circle(x,y,171,145,12) or circle(x,y,89,178,12) or circle(x,y,130,178,12):return 1
    elif kind=='clock':
        if circle(x,y,128,128,93):return 1
        if circle(x,y,128,128,72):return 3
        if segment(x,y,128,128,128,79,10) or segment(x,y,128,128,166,154,10):return 1
    return 0
def write(kind):
    rows=[]
    for y in range(N):
        row=bytearray([0])
        for x in range(N):
            paint=shape(kind,x+0.5,y+0.5)
            if not paint:row.extend((0,0,0,0));continue
            if paint==3:row.extend((216,241,255,255));continue
            g=y/N;base=BLUE if paint==1 else CYAN
            rgb=tuple(min(255,int(v*(1-0.14*g)+20*(1-g))) for v in base)
            row.extend((*rgb,255))
        rows.append(bytes(row))
    raw=zlib.compress(b''.join(rows),9)
    def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,6,0,0,0))+chunk(b'IDAT',raw)+chunk(b'IEND',b'')
    path=OUT/f'ic_ref_voice_{kind}.png'
    if path.exists():raise RuntimeError('Refusing to overwrite icon '+str(path))
    path.write_bytes(png)
    print('PASS PNG icon:',path)
for kind in ('microphone','waveform','bell','check','calendar','clock'):write(kind)
